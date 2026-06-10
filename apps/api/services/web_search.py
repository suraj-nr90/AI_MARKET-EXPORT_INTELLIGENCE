import os
import asyncio
import logging
import datetime
from urllib.parse import urlparse
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_search")

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully in web_search.")
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {e}")

# In-memory fallback cache in case Supabase is offline/unconfigured
local_cache = {}

def estimate_tokens(text: str) -> int:
    """Estimates the token count based on word count (approx. 1.3 tokens per word)."""
    if not text:
        return 0
    words = text.split()
    return int(len(words) * 1.3)

async def check_db_cache(product: str, region: str, search_type: str) -> dict | None:
    """Checks the Supabase search_cache table for cached results under 24 hours old."""
    if not supabase_client:
        # Fallback to local cache
        cache_key = f"{product}:{region}:{search_type}"
        cached = local_cache.get(cache_key)
        if cached:
            age = datetime.datetime.now() - cached["fetched_at"]
            if age.total_seconds() < 86400: # 24h
                logger.info(f"Local Cache HIT for {cache_key}")
                return cached["data"]
        return None
    
    try:
        # Query cache older than 24h
        time_limit = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)).isoformat()
        response = supabase_client.table("search_cache").select("*")\
            .eq("product", product)\
            .eq("region", region)\
            .eq("search_type", search_type)\
            .gte("fetched_at", time_limit)\
            .order("fetched_at", desc=True)\
            .limit(1)\
            .execute()
        
        if response.data:
            logger.info(f"Supabase Cache HIT for {product} | {region} | {search_type}")
            return response.data[0]["response_json"]
    except Exception as e:
        logger.error(f"Supabase cache read failed: {e}")
    return None

async def save_db_cache(product: str, region: str, search_type: str, data: dict):
    """Saves search results to the Supabase search_cache table."""
    cache_key = f"{product}:{region}:{search_type}"
    local_cache[cache_key] = {
        "fetched_at": datetime.datetime.now(),
        "data": data
    }
    
    if not supabase_client:
        return
        
    try:
        supabase_client.table("search_cache").insert({
            "product": product,
            "region": region,
            "search_type": search_type,
            "response_json": data,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }).execute()
        logger.info(f"Cache saved to Supabase for {product} | {region} | {search_type}")
    except Exception as e:
        logger.error(f"Supabase cache save failed: {e}")

async def execute_serper_search(client: httpx.AsyncClient, query: str, attempts: int = 3) -> dict:
    """Executes a Google Search query via Serper API with exponential backoff retries."""
    if not SERPER_API_KEY:
        logger.error("SERPER_API_KEY is not set.")
        return {"organic": []}
        
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    backoff = 1.0
    for attempt in range(attempts):
        try:
            timestamp = datetime.datetime.now().isoformat()
            logger.info(f"[{timestamp}] API Call: query='{query}' (attempt {attempt+1})")
            
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            result_json = response.json()
            
            # Log token estimation for the response
            est_tokens = estimate_tokens(str(result_json))
            logger.info(f"[{timestamp}] API Success: Estimated response tokens: {est_tokens}")
            return result_json
            
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            if attempt == attempts - 1:
                logger.error(f"Serper API failed after {attempts} attempts: {e}")
                return {"organic": []}
            logger.warning(f"Serper query '{query}' failed: {e}. Retrying in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff *= 2.0
            
    return {"organic": []}

async def search_market_overview(product: str, region: str) -> dict:
    """Executes search for market size, demand growth, and cold chain logistics."""
    search_type = "market_overview"
    cached = await check_db_cache(product, region, search_type)
    if cached:
        return cached

    # Reduced from 3 to 1 query for ultra-smooth progress without Serper API rate limits
    queries = [
        f"{product} market size demand growth cold chain logistics {region}"
    ]
    
    snippets = []
    urls = []
    source_names = []
    
    async with httpx.AsyncClient() as client:
        tasks = [execute_serper_search(client, query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            for item in res.get("organic", []):
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                title = item.get("title", "")
                
                if snippet:
                    snippets.append(snippet)
                if link:
                    urls.append(link)
                    try:
                        domain = urlparse(link).netloc
                        source_names.append(domain)
                    except Exception:
                        source_names.append(title)
                        
    combined_data = {
        "combined_snippets": "\n".join(snippets),
        "top_urls": list(set(urls))[:15],
        "source_names": list(set(source_names))[:15]
    }
    
    await save_db_cache(product, region, search_type, combined_data)
    return combined_data

def extract_clean_company_name(title: str, url: str) -> str:
    """Extracts a clean, actual company name from a search title and URL, ignoring generic terms/descriptions."""
    import re
    from urllib.parse import urlparse

    # 1. Try to extract from URL domain name as a clean brand hint
    domain_brand = ""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
            
        # Strip TLD and get main domain name
        domain_parts = domain.split(".")
        if len(domain_parts) >= 2:
            tlds = ["com", "org", "net", "gov", "edu", "mil", "biz", "info", "co", "in", "uk", "de", "fr", "nl", "sg", "in", "us", "eu", "ae", "sa"]
            clean_parts = [p for p in domain_parts if p not in tlds]
            if clean_parts:
                domain = clean_parts[0]
            else:
                domain = domain_parts[0]
        else:
            domain = domain_parts[0]
            
        domain = domain.replace("-", " ").replace("_", " ")
        domain_brand = " ".join([w.capitalize() for w in domain.split()])
    except Exception:
        pass

    # 2. Split title by common delimiters
    parts = re.split(r'\||-|—|–', title)
    parts = [p.strip() for p in parts if p.strip()]
    
    # Heuristics to skip descriptive titles
    banned_keywords = [
        "market", "report", "research", "size", "share", "forecast", "trends", "analysis", 
        "how to", "what is", "what are", "guide", "industry", "packaging", "thermal", "panel", 
        "gel pack", "cold chain", "logistics", "service", "services", "manufacturing", "enclosures", 
        "energy", "solutions", "products", "systems", "passive", "active", "supplier", "manufacturer"
    ]
    
    candidate = ""
    for part in parts:
        part_lower = part.lower()
        # If part is short and matches domain name, it is almost certainly the company name
        if domain_brand and (domain_brand.lower() in part_lower or part_lower in domain_brand.lower()):
            if len(part) < 35 and len(part) >= 2:
                return part
                
        # Otherwise, check if part contains no banned words and is short
        if not any(bk in part_lower for bk in banned_keywords):
            if len(part) >= 2 and len(part) < 35:
                candidate = part
                
    if candidate:
        return candidate
        
    # If the last part is short and does not contain banned keywords, it is often the brand name
    if parts and len(parts[-1]) < 30 and not any(bk in parts[-1].lower() for bk in ["report", "research", "market", "size"]):
        return parts[-1]
        
    # If the first part is short and doesn't contain banned keywords, return it
    if parts:
        first_part = parts[0]
        if len(first_part) < 35 and not any(bk in first_part.lower() for bk in ["market research", "market report", "size", "share"]):
            return first_part
            
    # Fallback to domain brand
    if domain_brand and len(domain_brand) > 2 and len(domain_brand) < 30:
        ignored_domains = ["medium", "linkedin", "github", "wikipedia", "youtube", "google", "facebook", "twitter", "justdial", "indiamart", "glassdoor", "indeed"]
        if domain_brand.lower() not in ignored_domains:
            return domain_brand
            
    return "Target Client Partner"

async def search_top_companies(sector: str, region: str, demand_keywords: list[str]) -> list[dict]:
    """Search for suppliers, buyers, and distributors of the product/keywords in the region."""
    # Use sector as the 'product' for naming cache keys
    search_type = f"top_companies"
    cached = await check_db_cache(sector, region, search_type)
    if cached:
        return cached.get("companies", [])

    import re
    # Clean sector name (remove text in parentheses)
    sector_clean = re.sub(r'\(.*?\)', '', sector).strip()
    
    # Reduced from 6 to 2 queries per sector (8 total queries across 4 sectors) for speed & reliability
    queries = [
        f"top cold chain {sector_clean} companies {region} distributors manufacturers",
        f"cold chain {sector_clean} {region} logistics suppliers"
    ]
        
    raw_companies = []
    
    async with httpx.AsyncClient() as client:
        tasks = [execute_serper_search(client, query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            for item in res.get("organic", []):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                
                title_lower = title.lower()
                snippet_lower = snippet.lower()
                link_lower = link.lower()
                
                # Skip market reports and research databases
                report_keywords = [
                    "market research", "market report", "market size", "market share", 
                    "market forecast", "market analysis", "market trends", "industry size", 
                    "industry report", "market insights", "research report", "study report",
                    "forecast 20", "global size", "growth analysis", "opportunity analysis"
                ]
                if any(rk in title_lower or rk in snippet_lower for rk in report_keywords):
                    continue
                    
                report_domains = [
                    "marketresearch", "grandviewresearch", "mordorintelligence", 
                    "reportlinker", "persistencemarketresearch", "alliedmarketresearch", 
                    "researchandmarkets", "marketsandmarkets", "industryarc", 
                    "coherentmarketinsights", "transparencymarketresearch", "verifiedmarketresearch",
                    "prnewswire", "businesswire", "globenewswire", "expertmarketresearch"
                ]
                if any(rd in link_lower for rd in report_domains):
                    continue
                    
                # Extract clean company name
                company_name = extract_clean_company_name(title, link)
                
                # Filter out generic or junk company names
                company_name_lower = company_name.lower().strip()
                generic_names = [
                    "telecom", "electronics", "chemical", "chemicals", "logistics", 
                    "packaging", "services", "solutions", "products", "market", "industry",
                    "target client partner", "passive packaging", "active packaging", "cold chain"
                ]
                if len(company_name_lower) < 3 or company_name_lower in generic_names:
                    continue
                if any(kw in company_name_lower for kw in ["report", "research", "size", "share", "forecast", "market study"]):
                    continue
                    
                # Calculate relevance score based on keyword density
                score = 0
                for kw in demand_keywords:
                    kw_lower = kw.lower()
                    score += snippet_lower.count(kw_lower) * 12
                    score += title_lower.count(kw_lower) * 25
                
                relevance_score = min(max(score, 20), 98) # Clamp between 20 and 98
                
                raw_companies.append({
                    "company_name": company_name,
                    "snippet": snippet,
                    "url": link,
                    "relevance_score": relevance_score
                })
                
    # Deduplicate companies by domain/url or name
    seen_domains = set()
    deduplicated = []
    
    # Sort by relevance score desc
    raw_companies.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    for c in raw_companies:
        try:
            domain = urlparse(c["url"]).netloc
        except Exception:
            domain = c["company_name"]
            
        if domain and domain not in seen_domains and len(c["company_name"]) < 80:
            seen_domains.add(domain)
            deduplicated.append(c)
            
    top_10 = deduplicated[:10]
    
    await save_db_cache(sector, region, search_type, {"companies": top_10})
    return top_10

async def search_industry_news(product: str, region: str, event_triggers: list[str]) -> list[dict]:
    """Queries upcoming events and procurement announcements for event triggers."""
    search_type = "industry_news"
    cached = await check_db_cache(product, region, search_type)
    if cached:
        return cached.get("news", [])

    queries = []
    # Query for the top triggers
    for trigger in event_triggers[:4]:
        queries.append(f"{trigger} {product} procurement demand")
        
    news_items = []
    
    async with httpx.AsyncClient() as client:
        tasks = [execute_serper_search(client, query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        for trigger, res in zip(event_triggers, results):
            for item in res.get("organic", []):
                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                date_str = item.get("date", "Within 12 months")
                
                try:
                    domain = urlparse(link).netloc
                except Exception:
                    domain = "News Source"
                    
                news_items.append({
                    "headline": title,
                    "source": domain,
                    "date": date_str,
                    "url": link,
                    "event_trigger_matched": trigger
                })
                
    # Deduplicate and sort
    seen_urls = set()
    dedup_news = []
    for item in news_items:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            dedup_news.append(item)
            
    top_news = dedup_news[:15]
    await save_db_cache(product, region, search_type, {"news": top_news})
    return top_news

async def search_competitive_landscape(product: str, region: str) -> dict:
    """Searches for manufacturers, competitors, and barrier details."""
    search_type = "competitive_landscape"
    cached = await check_db_cache(product, region, search_type)
    if cached:
        return cached

    # Reduced from 2 to 1 query for ultra-smooth performance
    queries = [
        f"{product} competitors manufacturers market share {region}"
    ]
    
    snippets = []
    competitor_names = []
    
    async with httpx.AsyncClient() as client:
        tasks = [execute_serper_search(client, query) for query in queries]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            for item in res.get("organic", []):
                snippet = item.get("snippet", "")
                title = item.get("title", "")
                if snippet:
                    snippets.append(snippet)
                    
                # Basic competitor name extraction heuristics from search titles
                parts = [p.strip() for p in title.split("|") if p.strip()]
                if len(parts) > 0 and len(parts[0].split()) <= 4:
                    name = parts[0].replace("Manufacturer", "").replace("Supplier", "").strip()
                    if name and name.lower() not in [product.lower(), "google", "search"]:
                        competitor_names.append(name)
                        
    combined_snippets = "\n".join(snippets)
    
    # Estimate barriers to entry from snippets
    barriers = "Regulatory certifications (e.g., FDA GDP, WHO pre-qualification) and logistics infrastructure complexity are significant barriers. Premium pricing of raw materials is also a barrier."
    if "certif" in combined_snippets.lower() or "regul" in combined_snippets.lower():
        barriers = "High compliance barriers: requires regional regulatory clearances (FDA, CDSCO, or EMA GDP) and certifications. Multi-day thermal payload validation is needed."
        
    landscape_data = {
        "competitor_names": list(set(competitor_names))[:8],
        "market_share_notes": combined_snippets[:1200], # Keep a reasonable size snippet text
        "barriers_to_entry": barriers
    }
    
    await save_db_cache(product, region, search_type, landscape_data)
    return landscape_data
