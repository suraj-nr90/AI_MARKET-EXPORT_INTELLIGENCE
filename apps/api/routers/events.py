from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.event_intelligence import get_event_intelligence_async

router = APIRouter(prefix="/events", tags=["Events"])

class EventRequest(BaseModel):
    product: str
    region: str

@router.get("")
async def get_events():
    return {"message": "Get cached events (Route Placeholder)"}

@router.post("/upcoming")
async def upcoming_events(req: EventRequest):
    try:
        events = await get_event_intelligence_async(req.product, req.region)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
