from fastapi import APIRouter, HTTPException
from services.db import db
from pydantic import BaseModel
import json

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/")
async def get_reports():
    if db.pool:
        try:
            async with db.pool.acquire() as conn:
                rows = await conn.fetch("SELECT id, created_at, report_json FROM reports ORDER BY created_at DESC")
                reports = []
                for r in rows:
                    res_json = r['report_json']
                    report_json = json.loads(res_json) if isinstance(res_json, str) else res_json
                    reports.append({
                        "id": str(r["id"]),
                        "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
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
    if db.pool:
        try:
            async with db.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM reports WHERE id = $1::uuid", report_id)
                if not row:
                    raise HTTPException(status_code=404, detail="Report not found")
                res = dict(row)
                res["id"] = str(res["id"])
                res["session_id"] = str(res["session_id"])
                res["created_at"] = res["created_at"].isoformat() if hasattr(res["created_at"], "isoformat") else str(res["created_at"])
                if isinstance(res["report_json"], str):
                    res["report_json"] = json.loads(res["report_json"])
                return res
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    raise HTTPException(status_code=501, detail="Database not configured")

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    if db.pool:
        try:
            async with db.pool.acquire() as conn:
                # First, check if report exists
                row = await conn.fetchrow("SELECT id, session_id FROM reports WHERE id = $1::uuid", report_id)
                if not row:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                # Delete report record
                await conn.execute("DELETE FROM reports WHERE id = $1::uuid", report_id)
                
                # Optionally delete research_session
                session_id = str(row["session_id"]) if row.get("session_id") else None
                if session_id:
                    await conn.execute("DELETE FROM research_sessions WHERE id = $1::uuid", session_id)
                    
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
    if db.pool:
        try:
            async with db.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT report_json FROM reports WHERE id = $1::uuid", report_id)
                if not row:
                    raise HTTPException(status_code=404, detail="Report not found")
            
                res_json = row["report_json"]
                report_json = json.loads(res_json) if isinstance(res_json, str) else res_json
                
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
