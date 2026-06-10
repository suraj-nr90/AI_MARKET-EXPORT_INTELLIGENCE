from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/")
async def get_companies():
    return {"message": "Get client discovery companies"}
