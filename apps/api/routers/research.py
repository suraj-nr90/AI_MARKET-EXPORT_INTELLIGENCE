from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.web_search import search_market_overview, supabase_client
import uuid
import datetime
import asyncio
import json

router = APIRouter(prefix="/research", tags=["Research"])

class SearchRequest(BaseModel):
    product: str
    region: str

@router.get("/")
async def get_research_sessions():
    if supabase_client:
        try:
            res = supabase_client.table("research_sessions").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Get all research sessions (Supabase offline)"}

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
    
    if supabase_client:
        try:
            supabase_client.table("research_sessions").insert(session_data).execute()
        except Exception as e:
            print(f"Error saving research session: {e}")
            
    try:
        # Call web search service
        search_results = await search_market_overview(req.product, req.region)
        
        # Update session status
        if supabase_client:
            try:
                supabase_client.table("research_sessions").update({"status": "completed"}).eq("id", session_id).execute()
            except Exception as e:
                print(f"Error updating research session status: {e}")
                
        return {
            "session_id": session_id,
            "status": "completed",
            "data": search_results
        }
    except Exception as e:
        if supabase_client:
            try:
                supabase_client.table("research_sessions").update({"status": "failed"}).eq("id", session_id).execute()
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
    
    async def event_generator():
        queue = asyncio.Queue()
        session_id = str(uuid.uuid4())
        
        async def status_callback(status_message: str):
            await queue.put({"status": status_message})
            
        async def run_pipeline():
            try:
                report = await generate_report(req.product, req.region, status_callback=status_callback, session_id=session_id)
                await queue.put({"status": "Complete", "report": report})
            except Exception as e:
                await queue.put({"status": "Error", "message": str(e)})
            finally:
                await queue.put(None)
                
        # Run background task
        asyncio.create_task(run_pipeline())
        
        while True:
            item = await queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


