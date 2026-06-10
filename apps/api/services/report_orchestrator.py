import uuid
import datetime
import logging
import asyncio

from knowledge.product_kb import PRODUCT_KB
from knowledge.regions import REGIONS
from services.web_search import (
    search_market_overview,
    search_top_companies,
    search_competitive_landscape
)
from services.db import db
import json
from services.event_intelligence import get_event_intelligence_async
from services.llm_analyzer import analyze_with_llm

logger = logging.getLogger("report_orchestrator")

async def generate_report(product: str, region: str, status_callback=None, session_id: str = None) -> dict:
    """Orchestrates the full pipeline of regional product market research, event mapping, and AI synthesis."""
    
    # Generate a session ID if not provided, and log it to Supabase
    if not session_id:
        session_id = str(uuid.uuid4())
        
    db_product = "gel_packs" if "gel" in product.lower() else "pcm_panels"
    session_data = {
        "id": session_id,
        "product": db_product,
        "region": region,
        "status": "processing",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    if db.pool:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            async with db.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO research_sessions (id, product, region, status, created_at) VALUES ($1::uuid, $2, $3, $4, $5)",
                    session_id, db_product, region, "processing", now
                )
            logger.info(f"Initialized research session {session_id} in NeonDB.")
        except Exception as e:
            logger.error(f"Failed to create research session in DB: {e}")

    try:
        # Step 1: Load static KBs
        p_id = "gel_packs" if "gel" in product.lower() else "pcm_panels"
        product_kb_data = PRODUCT_KB.get(p_id, {})
        kb_sectors = product_kb_data.get("sectors", [])
        
        regional_context = REGIONS.get(region, REGIONS.get("United States")) # Fallback to US if not found

        # Step 2: Search market overview (Stepper Step 1)
        if status_callback:
            await status_callback("Searching market data...")
            
        market_overview = await search_market_overview(product, region)

        # Step 3: Gather event intelligence (Stepper Step 2)
        if status_callback:
            await status_callback("Scanning event calendars...")
            
        events_list = await get_event_intelligence_async(product, region)

        # Step 4: Discover client companies (Stepper Step 3)
        if status_callback:
            await status_callback("Discovering client companies...")
            
        company_tasks = []
        for sector in kb_sectors:
            company_tasks.append(
                search_top_companies(sector["name"], region, sector["demand_keywords"])
            )
            
        companies_results = await asyncio.gather(*company_tasks)
        
        # Merge company lists back into sectors
        sectors_bundle = []
        for sector, companies in zip(kb_sectors, companies_results):
            sectors_bundle.append({
                "name": sector["name"],
                "applications": sector["applications"],
                "event_triggers": sector["event_triggers"],
                "peak_timing": sector["peak_timing"],
                "demand_keywords": sector["demand_keywords"],
                "companies": companies
            })

        # Search competitive landscape
        comp_landscape = await search_competitive_landscape(product, region)

        # Step 5: Assemble Context Bundle and Run AI Synthesis (Stepper Step 4)
        if status_callback:
            await status_callback("Running AI synthesis...")
            
        context_bundle = {
            "product": product,
            "region": region,
            "market_overview": market_overview,
            "sectors": sectors_bundle,
            "competitive_landscape": comp_landscape,
            "events": events_list,
            "regional_context": regional_context
        }

        report_json = await analyze_with_llm(context_bundle)

        # Step 8: Save final report to NeonDB
        if db.pool:
            try:
                now = datetime.datetime.now(datetime.timezone.utc)
                async with db.pool.acquire() as conn:
                    # Update status of session
                    await conn.execute(
                        "UPDATE research_sessions SET status = $1 WHERE id = $2::uuid",
                        "completed", session_id
                    )
                    
                    # Insert report
                    report_id = str(uuid.uuid4())
                    await conn.execute(
                        "INSERT INTO reports (id, session_id, report_json, created_at) VALUES ($1::uuid, $2::uuid, $3, $4)",
                        report_id, session_id, json.dumps(report_json), now
                    )
                logger.info(f"Report saved successfully to NeonDB reports table for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to save report to database: {e}")

        if status_callback:
            await status_callback("Complete")
            
        return report_json

    except Exception as e:
        logger.error(f"Orchestration failure for product={product}, region={region}: {e}")
        if db.pool:
            try:
                async with db.pool.acquire() as conn:
                    await conn.execute(
                        "UPDATE research_sessions SET status = $1 WHERE id = $2::uuid",
                        "failed", session_id
                    )
            except Exception as e_status:
                logger.error(f"Failed to update session to failed: {e_status}")
        raise e
