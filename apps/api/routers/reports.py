from fastapi import APIRouter, HTTPException
from services.web_search import supabase_client
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/")
async def get_reports():
    if supabase_client:
        try:
            res = supabase_client.table("reports").select("id, created_at, report_json").order("created_at", desc=True).execute()
            reports = []
            for r in res.data:
                report_json = r.get("report_json", {})
                reports.append({
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "product": report_json.get("product", ""),
                    "region": report_json.get("region", ""),
                    "score": report_json.get("market_attractiveness_score", 0)
                })
            return reports
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return []

@router.get("/{report_id}")
async def get_report_by_id(report_id: str):
    if supabase_client:
        try:
            res = supabase_client.table("reports").select("*").eq("id", report_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Report not found")
            return res.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=501, detail="Database not configured")

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    if supabase_client:
        try:
            # First, check if report exists
            check = supabase_client.table("reports").select("id, session_id").eq("id", report_id).execute()
            if not check.data:
                raise HTTPException(status_code=404, detail="Report not found")
            
            # Delete report record
            supabase_client.table("reports").delete().eq("id", report_id).execute()
            
            # Optionally delete research_session
            session_id = check.data[0].get("session_id")
            if session_id:
                supabase_client.table("research_sessions").delete().eq("id", session_id).execute()
                
            return {"status": "deleted"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=501, detail="Database not configured")

# Support both /pdf and /export for PDF rendering
@router.get("/{report_id}/pdf")
@router.get("/{report_id}/export")
async def export_report_pdf(report_id: str):
    if supabase_client:
        try:
            res = supabase_client.table("reports").select("*").eq("id", report_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Report not found")
            
            report_record = res.data[0]
            report_json = report_record.get("report_json", {})
            
            from services.pdf_generator import generate_report_pdf
            pdf_data = generate_report_pdf(report_json)
            
            from fastapi.responses import Response
            product_clean = report_json.get("product", "Report").replace(" ", "_")
            region_clean = report_json.get("region", "Region").replace(" ", "_")
            
            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=Market_Report_{region_clean}_{product_clean}.pdf"}
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=501, detail="Database not configured")
