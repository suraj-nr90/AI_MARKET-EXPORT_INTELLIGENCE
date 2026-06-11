from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.web_search import search_market_overview
from services.db import db
import uuid
import datetime
import asyncio
import json

router = APIRouter(prefix="/research", tags=["Research"])

class SearchRequest(BaseModel):
    product: str
    region: str

@router.get("")
async def get_research_sessions():
    if db.pool:
        try:
            async with db.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM research_sessions ORDER BY created_at DESC")
                # Convert asyncpg Records to dicts
                # and handle datetime to string if needed, FastAPI usually handles datetime dict values
                return [dict(row) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Get all research sessions (NeonDB offline)"}

@router.post("/search-test")
async def search_test(req: SearchRequest):
    # Try to insert a research session into Supabase to track
    session_id = str(uuid.uuid4())
    session_data = {
        "id": session_id,
        "product": req.product,
        "region": req.region,
        "status": "processing",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    if db.pool:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            async with db.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO research_sessions (id, product, region, status, created_at) VALUES ($1::uuid, $2, $3, $4, $5)",
                    session_id, req.product, req.region, "processing", now
                )
        except Exception as e:
            print(f"Error saving research session: {e}")
            
    try:
        # Call web search service
        search_results = await search_market_overview(req.product, req.region)
        
        # Update session status
        if db.pool:
            try:
                async with db.pool.acquire() as conn:
                    await conn.execute("UPDATE research_sessions SET status = $1 WHERE id = $2::uuid", "completed", session_id)
            except Exception as e:
                print(f"Error updating research session status: {e}")
                
        return {
            "session_id": session_id,
            "status": "completed",
            "data": search_results
        }
    except Exception as e:
        if db.pool:
            try:
                async with db.pool.acquire() as conn:
                    await conn.execute("UPDATE research_sessions SET status = $1 WHERE id = $2::uuid", "failed", session_id)
            except Exception as e_status:
                print(f"Error updating status to failed: {e_status}")
        raise HTTPException(status_code=500, detail=str(e))

class GenerateRequest(BaseModel):
    product: str
    region: str

@router.post("/generate")
async def generate_market_report(req: GenerateRequest):
    from fastapi.responses import StreamingResponse
    from services.report_orchestrator import generate_report
    import logging
    
    logger = logging.getLogger("research")
    
    async def event_generator():
        queue = asyncio.Queue()
        session_id = str(uuid.uuid4())
        
        async def status_callback(msg: str):
            await queue.put(msg)
        
        async def run_report():
            try:
                report = await generate_report(req.product, req.region, status_callback=status_callback, session_id=session_id)
                await queue.put(None)  # Signal end
                return report
            except Exception as e:
                logger.error(f"Error: {e}")
                await queue.put(f"ERROR: {str(e)}")
                await queue.put(None)
                raise
        
        task = asyncio.create_task(run_report())
        report = None
        
        try:
            while True:
                msg = await queue.get()
                if msg is None:
                    # Task finished, get the report
                    try:
                        report = await task
                    except:
                        report = None
                    if report:
                        yield f"data: {json.dumps({'status': 'Complete', 'report': report})}\n\n"
                    break
                else:
                    yield f"data: {json.dumps({'status': msg})}\n\n"
        except Exception as e:
            logger.error(f"Generator error: {e}")
            yield f"data: {json.dumps({'status': 'Error', 'message': str(e)})}\n\n"
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


