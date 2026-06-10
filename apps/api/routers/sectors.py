from fastapi import APIRouter

router = APIRouter(prefix="/sectors", tags=["Sectors"])

@router.get("/")
async def get_sectors():
    return {"message": "Get sector intelligence"}
