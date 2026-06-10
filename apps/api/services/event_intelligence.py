import os
import logging
import datetime
from urllib.parse import urlparse
import httpx
from rapidfuzz import fuzz
from dotenv import load_dotenv, find_dotenv

from knowledge.product_kb import PRODUCT_KB
from knowledge.regions import REGIONS
from knowledge.static_events import STATIC_EVENTS

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_intelligence")

# In production, call load_dotenv() at the entry point.
load_dotenv(find_dotenv())

PREDICTHQ_API_KEY = os.getenv("PREDICTHQ_API_KEY")

# Mapping of region name to PredictHQ ISO-3166 country codes
REGION_COUNTRY_MAP = {
    "united states": ["US"],
    "india": ["IN"],
    "europe": ["DE", "FR", "GB", "NL", "CH", "BE", "IT", "ES"],
    "middle east": ["AE", "SA", "QA", "OM", "KW", "BH"],
    "southeast asia": ["SG", "MY", "TH", "VN", "ID", "PH"]
}

def map_spike_score(rank: int) -> int:
    """Maps PredictHQ 0-100 rank to a 1-10 demand spike score."""
    if rank >= 80:
        return 10 if rank >= 90 else 9
    elif rank >= 60:
        return 8 if rank >= 70 else 7
    elif rank >= 40:
        return 6 if rank >= 50 else 5
    else:
        return 4 if rank >= 20 else 3

def generate_action(event_name: str, product_id: str, sector: str) -> str:
    """Generates a contextual one-sentence outreach suggestion."""
    p_name = "Gel Packs" if product_id == "gel_packs" else "PCM Panels"
    
    if "Pharm" in sector or "Life Sciences" in sector:
        return f"Initiate GDP-compliant cold chain outreach to pharmaceutical exporters exhibiting at {event_name}."
    elif "Food" in sector or "E-Commerce" in sector:
        return f"Contact food logistics and meal kit distributors attending {event_name} regarding last-mile {p_name} procurement."
    elif "Building" in sector or "Construction" in sector:
        return f"Engage green building contractors and passive design architects exhibiting at {event_name}."
    elif "Tele" in sector:
        return f"Target telecom cabinet manufacturers showcasing infrastructure solutions at {event_name}."
    elif "Renew" in sector or "Energy" in sector:
        return f"Outreach to battery storage (BESS) suppliers presenting solar/wind thermal safety components at {event_name}."
    return f"Coordinate export sales outreach targeting {sector} exhibitors at {event_name} regarding {p_name} options."

async def fetch_live_events(region: str, categories: list[str], horizon_days: int = 365) -> list[dict]:
    """Fetches live event data from the PredictHQ API."""
    if not PREDICTHQ_API_KEY:
        logger.warning("PREDICTHQ_API_KEY is not configured. Falling back to static events.")
        return []

    countries = REGION_COUNTRY_MAP.get(region.lower(), ["US"])
    
    # Calculate dates
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=horizon_days)
    
    url = "https://api.predicthq.com/v1/events/"
    headers = {
        "Authorization": f"Bearer {PREDICTHQ_API_KEY}",
        "Accept": "application/json"
    }
    
    # PredictHQ supports country comma-separated filter and category comma-separated filter
    params = {
        "country": ",".join(countries),
        "category": ",".join(categories),
        "active.gte": today.strftime("%Y-%m-%d"),
        "active.lte": end_date.strftime("%Y-%m-%d"),
        "limit": 50,
        "sort": "rank"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Querying PredictHQ for countries: {countries}, categories: {categories}")
            response = await client.get(url, headers=headers, params=params, timeout=12.0, follow_redirects=True)
            
            if response.status_code == 401:
                logger.error("PredictHQ API authentication failed (401 Unauthorized).")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            events = []
            for item in data.get("results", []):
                title = item.get("title", "Unnamed Event")
                start_str = item.get("start", "")
                
                # Format start date
                event_date = start_str[:10] if start_str else today.strftime("%Y-%m-%d")
                
                # Format location
                country_code = item.get("country", "")
                phq_location = item.get("location", [])
                location_str = f"{country_code}"
                
                events.append({
                    "event_name": title,
                    "event_date": event_date,
                    "location": location_str,
                    "category": item.get("category", ""),
                    "predicted_attendance": item.get("phq_attendance", 0) or 0,
                    "phq_rank": item.get("rank", 50) or 50
                })
            return events
            
    except Exception as e:
        logger.error(f"Error querying PredictHQ API: {e}. Falling back to static.")
        return []

def map_events_to_sectors(events: list[dict], product: str, sectors: list[dict]) -> list[dict]:
    """Fuzzy-matches event names against sector event_triggers in the product KB."""
    mapped_events = []
    
    for e in events:
        matched_sector = None
        best_score = 0
        
        # Calculate fuzzy match across all triggers in all sectors
        for sector in sectors:
            for trigger in sector.get("event_triggers", []):
                # We use partial_ratio to match "Arab Health" in "Arab Health Exhibition and Congress 2024"
                score = fuzz.partial_ratio(trigger.lower(), e["event_name"].lower())
                if score > best_score:
                    best_score = score
                    if score >= 70:
                        matched_sector = sector["name"]
                        
        # If no fuzzy match from the triggers, check if it's a static event that has predefined tags
        if not matched_sector and "sector_tags" in e:
            # Match first tag that matches our product sectors
            valid_sectors = [s["name"] for s in sectors]
            for tag in e["sector_tags"]:
                if tag in valid_sectors:
                    matched_sector = tag
                    break
                    
        # Skip events that have absolutely no matched sector mapping
        if not matched_sector:
            continue
            
        # Parse date and compute procurement window (event_date - 90 days)
        event_date_str = e["event_date"]
        try:
            date_obj = datetime.datetime.strptime(event_date_str, "%Y-%m-%d").date()
        except Exception:
            date_obj = datetime.date.today()
            
        proc_start_obj = date_obj - datetime.timedelta(days=90)
        procurement_window_start = proc_start_obj.strftime("%Y-%m-%d")
        
        # Determine demand spike score (1-10)
        rank = e.get("phq_rank", 50)
        spike_score = map_spike_score(rank)
        
        mapped_events.append({
            "event_name": e["event_name"],
            "event_date_or_window": event_date_str,
            "location": e["location"],
            "matched_sector": matched_sector,
            "procurement_window_start": procurement_window_start,
            "demand_spike_score": spike_score,
            "recommended_action": generate_action(e["event_name"], product, matched_sector)
        })
        
    return mapped_events

def get_event_intelligence(product: str, region: str) -> list[dict]:
    """Main coordinator to fetch, merge, deduplicate, map, and rank events."""
    # Validate product input
    p_id = "gel_packs" if "gel" in product.lower() else "pcm_panels"
    product_data = PRODUCT_KB.get(p_id, {})
    sectors = product_data.get("sectors", [])
    
    # 1. Fetch live events (PredictHQ)
    categories = ["expos", "conferences", "sports", "public-holidays"]
    
    # Run fetch synchronously inside async context or handle async execution wrapper
    # Since FastAPI endpoints are async, get_event_intelligence is called in async route.
    # We will make this function async to call fetch_live_events cleanly.
    return []

# To make implementation robust, let's redefine get_event_intelligence as async:
async def get_event_intelligence_async(product: str, region: str) -> list[dict]:
    """Main coordinator to fetch, merge, deduplicate, map, and rank events (async)."""
    p_id = "gel_packs" if "gel" in product.lower() else "pcm_panels"
    product_data = PRODUCT_KB.get(p_id, {})
    sectors = product_data.get("sectors", [])
    
    # 1. Fetch live events
    categories = ["expos", "conferences", "sports", "public-holidays"]
    live_events = await fetch_live_events(region, categories)
    
    # 2. Filter and project STATIC_EVENTS by region
    projected_static = []
    today = datetime.date.today()
    
    for se in STATIC_EVENTS:
        typical_reg = se["typical_region"].lower()
        if typical_reg == region.lower() or typical_reg == "global":
            # Project typical_month to next occurrence
            year = today.year
            if se["typical_month"] < today.month:
                year += 1
            # Project to the 15th of that month
            projected_date = datetime.date(year, se["typical_month"], 15)
            
            # Map score to phq_rank equivalents: static score 10 -> rank 95, etc.
            static_score = se["product_relevance"].get(p_id, 5)
            equivalent_rank = static_score * 9.5
            
            projected_static.append({
                "event_name": se["event_name"],
                "event_date": projected_date.strftime("%Y-%m-%d"),
                "location": se["typical_region"],
                "category": "static",
                "predicted_attendance": 0,
                "phq_rank": int(equivalent_rank),
                "sector_tags": se["sector_tags"]
            })
            
    # 3. Merge live and projected static events
    merged = []
    merged.extend(live_events)
    merged.extend(projected_static)
    
    # 4. Deduplicate by event name similarity
    deduplicated = []
    for event in merged:
        is_duplicate = False
        for existing in deduplicated:
            # Fuzzy match event names
            if fuzz.ratio(event["event_name"].lower(), existing["event_name"].lower()) >= 80:
                is_duplicate = True
                # Keep the live one (rank might be more accurate or date is exact)
                if event["category"] != "static" and existing["category"] == "static":
                    existing["event_name"] = event["event_name"]
                    existing["event_date"] = event["event_date"]
                    existing["location"] = event["location"]
                    existing["category"] = event["category"]
                    existing["phq_rank"] = event["phq_rank"]
                break
        if not is_duplicate:
            deduplicated.append(event)
            
    # 5. Run mapping
    mapped = map_events_to_sectors(deduplicated, p_id, sectors)
    
    # 6. Sort by score descending and return top 10
    mapped.sort(key=lambda x: x["demand_spike_score"], reverse=True)
    return mapped[:10]
