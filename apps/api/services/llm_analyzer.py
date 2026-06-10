import os
import json
import httpx
import logging
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import datetime

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_analyzer")

load_dotenv()

NVIDIA_NIM_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY")

async def get_available_model() -> str:
    """Queries the NVIDIA NIM /models endpoint to detect the active model id."""
    default_model = "nvidia/nemotron-3-8b-chat-4k-steerlm"
    if not NVIDIA_NIM_API_KEY:
        return default_model
        
    url = f"{NVIDIA_NIM_BASE_URL.rstrip('/')}/models"
    headers = {"Authorization": f"Bearer {NVIDIA_NIM_API_KEY}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=6.0)
            if response.status_code == 200:
                models_data = response.json()
                model_ids = [m.get("id") for m in models_data.get("data", [])]
                logger.info(f"Detected available NIM models: {model_ids}")
                
                # Prioritize faster, modern preferred models
                preferred_models = [
                    "meta/llama-3.1-8b-instruct",
                    "meta/llama-3.3-70b-instruct",
                    "nvidia/llama-3.1-nemotron-51b-instruct",
                    "nvidia/nemotron-3-8b-chat-4k-steerlm",
                    "nvidia/nemotron-3-8b-instruct"
                ]
                for pref in preferred_models:
                    for m_id in model_ids:
                        if pref in m_id:
                            return m_id
                            
                # Fallback check for any nemotron
                for m_id in model_ids:
                    if "nemotron" in m_id:
                        return m_id
                        
                # Look for fallback models hosted on NIM (like Llama-3-8b)
                for m_id in model_ids:
                    if "llama" in m_id and "8b" in m_id:
                        return m_id
                        
                if model_ids:
                    return model_ids[0]
    except Exception as e:
        logger.warning(f"Could not reach NIM models endpoint: {e}. Defaulting to {default_model}")
        
    return default_model

def clean_json_response(raw_text: str) -> str:
    """Cleans markdown fences or trailing whitespaces from the LLM output."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

async def analyze_with_llm(context_bundle: dict) -> dict:
    """Synthesizes the gathered market data into a structured report using NVIDIA NIM API."""
    if not NVIDIA_NIM_API_KEY:
        logger.error("NVIDIA_NIM_API_KEY is missing. Returning partial bundle report.")
        return generate_partial_fallback(context_bundle, "Missing NVIDIA NIM API Key")

    # Detect the correct model
    model_name = await get_available_model()
    logger.info(f"Using NIM model: {model_name}")

    client = OpenAI(
        base_url=NVIDIA_NIM_BASE_URL,
        api_key=NVIDIA_NIM_API_KEY,
        timeout=30.0
    )

    # Context variables
    product = context_bundle.get("product", "Gel Packs")
    region = context_bundle.get("region", "India")
    
    market_overview = context_bundle.get("market_overview", {}).get("combined_snippets", "No market data found.")
    
    # Format sectors and companies
    sector_data_list = []
    for s in context_bundle.get("sectors", []):
        sec_name = s.get("name")
        comp_str = "\n".join([
            f"  - Company: {c['company_name']}, Relevance: {c['relevance_score']}, Snippet: {c['snippet'][:150]}"
            for c in s.get("companies", [])
        ])
        sector_data_list.append(f"Sector: {sec_name}\nDemand Keywords: {s.get('demand_keywords')}\nAssociated Companies:\n{comp_str}")
    sector_data_with_companies = "\n\n".join(sector_data_list)

    # Format event intelligence
    event_list = []
    for e in context_bundle.get("events", []):
        event_list.append(
            f"- Event: {e['event_name']}, Date/Window: {e['event_date_or_window']}, Location: {e['location']}, "
            f"Matched Sector: {e['matched_sector']}, Spike Score: {e['demand_spike_score']}, Recommendation: {e['recommended_action']}"
        )
    event_intelligence_data = "\n".join(event_list)

    # Format competitive landscape
    comp_landscape = context_bundle.get("competitive_landscape", {})
    competitor_list = ", ".join(comp_landscape.get("competitor_names", []))
    competitive_data = (
        f"Competitors: {competitor_list}\n"
        f"Market Share Notes: {comp_landscape.get('market_share_notes', '')[:1000]}\n"
        f"Barriers to Entry: {comp_landscape.get('barriers_to_entry', '')}"
    )

    # Format regional context
    reg_context = context_bundle.get("regional_context", {})
    regional_clusters_and_regulations = (
        f"Key Clusters: {', '.join(reg_context.get('key_industry_clusters', []))}\n"
        f"Regulatory Bodies: {', '.join(reg_context.get('regulatory_bodies', []))}\n"
        f"Currency: {reg_context.get('currency', '')}\n"
        f"Import Notes: {reg_context.get('import_notes', '')}"
    )

    system_prompt = (
        "You are an expert export market intelligence analyst specializing in "
        "thermal management and cold-chain packaging products. Your task is to "
        "analyze the provided market research data and generate a structured "
        "intelligence report. You must respond ONLY with a valid JSON object. "
        "No preamble, no markdown formatting (do not wrap in ```json), no explanation. Only raw JSON."
    )

    user_prompt = f"""
Product: {product}
Target Region: {region}

=== MARKET OVERVIEW ===
{market_overview}

=== SECTOR RESEARCH DATA ===
{sector_data_with_companies}

=== UPCOMING EVENTS (DEMAND TRIGGERS) ===
{event_intelligence_data}

=== COMPETITIVE LANDSCAPE ===
{competitive_data}

=== REGIONAL CONTEXT ===
{regional_clusters_and_regulations}

Generate a complete market intelligence report as a JSON object with this exact structure:
{{
  "product": "{product}",
  "region": "{region}",
  "generated_at": "{datetime.datetime.now(datetime.timezone.utc).isoformat()}",
  "executive_summary": "string (3–4 sentences overviewing the market opportunity and strategic fit)",
  "product_regional_fit": {{
    "fit_score": 85,
    "fit_rationale": "detailed explanation of why the product fits this region based on regulatory compliance and sector demands"
  }},
  "top_sectors": [
    {{
      "rank": 1,
      "sector_name": "string (one of the 4 sectors provided)",
      "demand_score": 9,
      "key_drivers": ["driver 1", "driver 2", "driver 3"],
      "top_companies": [
        {{"company": "Real Company Name from Sector Data", "rationale": "why they need this product", "estimated_need": "Estimated annual gel pack/panel usage"}},
        {{"company": "Real Company Name from Sector Data", "rationale": "why they need this product", "estimated_need": "Estimated annual gel pack/panel usage"}},
        {{"company": "Real Company Name from Sector Data", "rationale": "why they need this product", "estimated_need": "Estimated annual gel pack/panel usage"}},
        {{"company": "Real Company Name from Sector Data", "rationale": "why they need this product", "estimated_need": "Estimated annual gel pack/panel usage"}},
        {{"company": "Real Company Name from Sector Data", "rationale": "why they need this product", "estimated_need": "Estimated annual gel pack/panel usage"}}
      ],
      "entry_difficulty": "Medium"
    }}
  ],
  "event_procurement_windows": [
    {{
      "event": "Event Name",
      "date_window": "Event Date",
      "procurement_start": "Procurement Window Start Date",
      "sector": "Matched Sector Name",
      "demand_spike_score": 8,
      "outreach_recommendation": "recommendation suggestion"
    }}
  ],
  "potential_clients": [
    {{
      "company_name": "Real Company Name",
      "sector": "Sector Name",
      "region_country": "Country/Region",
      "relevance_rationale": "detailed explanation of relevance",
      "estimated_annual_need": "estimated volume/units",
      "contact_strategy": "specific channel/angle to pitch"
    }}
  ],
  "competitive_landscape": {{
    "main_competitors": ["competitor 1", "competitor 2"],
    "competitive_advantages_to_emphasize": ["advantage 1", "advantage 2"],
    "market_gaps": ["gap 1", "gap 2"]
  }},
  "market_attractiveness_score": 78,
  "market_attractiveness_breakdown": {{
    "market_size": 18,
    "growth_trajectory": 20,
    "competitive_intensity": 17,
    "event_driven_demand": 23
  }},
  "strategic_recommendations": [
    {{"priority": 1, "action": "recommended action item", "timeline": "30 days", "expected_outcome": "what to expect"}},
    {{"priority": 2, "action": "recommended action item", "timeline": "60 days", "expected_outcome": "what to expect"}},
    {{"priority": 3, "action": "recommended action item", "timeline": "90 days", "expected_outcome": "what to expect"}}
  ]
}}

Ensure that:
1. `top_sectors` lists all 4 sectors, ranked by `demand_score`.
2. `top_companies` within each sector has 5 real companies.
3. `potential_clients` lists exactly 10 real companies total (extracted from the provided sector research data).
4. `event_procurement_windows` lists the top 5 events.
5. All scores and sub-scores are strictly integers.
6. The output is ONLY the JSON object. Do not explain anything.
7. CRITICAL COMPANY NAME EXTRACTION RULES:
   For both `top_companies` and `potential_clients`, you MUST extract the ACTUAL, real company name (e.g. "CEVA Logistics", "DHL", "DuPont", "Bayer", "Caplinq", "Wacker Chemie", etc.) from the titles or snippets provided. 
   Do NOT use raw search result titles, blog titles, or general descriptive phrases (like "Development of PCM-based...", "Active and Passive Packaging solutions - CEVA Logistics", "Order Fulfillment Service Europe...") as the company name. 
   If a search result contains a description, parse it and extract ONLY the name of the company responsible (e.g. from "Active and Passive Packaging solutions - CEVA Logistics", extract "CEVA Logistics"; from "Order Fulfillment Service Europe - CAPLINQ Corporation", extract "CAPLINQ Corporation").
   Never output generic sentences or descriptions as company names.
"""

    attempts = 2
    for attempt in range(attempts):
        try:
            logger.info(f"Sending request to NIM API (completions, attempt {attempt+1})...")
            
            # Use OpenAI compat client
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            raw_content = response.choices[0].message.content
            cleaned_content = clean_json_response(raw_content)
            
            report = json.loads(cleaned_content)
            logger.info("Successfully received and parsed AI report JSON.")
            return report
            
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            logger.warning(f"NIM API HTTP Error (attempt {attempt+1}): {e}")
            if attempt == 0:
                logger.info("Retrying NIM API call in 3 seconds...")
                await asyncio.sleep(3.0)
            else:
                return generate_partial_fallback(context_bundle, f"NIM Connection failed: {e}")
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed on attempt {attempt+1}: {e}")
            if attempt == 0:
                logger.info("Retrying with a stricter formatting prompt...")
                system_prompt += " CRITICAL: Ensure you output absolutely nothing but the valid JSON string. Do not include markdown code block syntax."
            else:
                return generate_partial_fallback(context_bundle, f"JSON Parsing failed: {e}")
                
        except Exception as e:
            logger.error(f"Unexpected error during NIM completion: {e}")
            return generate_partial_fallback(context_bundle, f"Unexpected error: {e}")
            
    return generate_partial_fallback(context_bundle, "LLM Synthesis failed")

def generate_partial_fallback(context_bundle: dict, error_msg: str) -> dict:
    """Generates a structured fallback JSON report using gathered context when LLM synthesis fails."""
    logger.warning(f"Generating fallback report. Reason: {error_msg}")
    
    product = context_bundle.get("product", "Gel Packs")
    region = context_bundle.get("region", "India")
    
    # Extract some companies
    potential_clients = []
    for sector in context_bundle.get("sectors", []):
        for c in sector.get("companies", [])[:3]:
            potential_clients.append({
                "company_name": c["company_name"],
                "sector": sector["name"],
                "region_country": region,
                "relevance_rationale": c["snippet"][:150],
                "estimated_annual_need": "TBD (High Relevance)",
                "contact_strategy": "Pitch direct cold chain compliance value."
            })
            
    # Extract some events
    event_windows = []
    for e in context_bundle.get("events", [])[:5]:
        event_windows.append({
            "event": e["event_name"],
            "date_window": e["event_date_or_window"],
            "procurement_start": e["procurement_window_start"],
            "sector": e["matched_sector"],
            "demand_spike_score": e["demand_spike_score"],
            "outreach_recommendation": e["recommended_action"]
        })
        
    fallback = {
        "product": product,
        "region": region,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "executive_summary": f"Failed to synthesize with LLM due to: {error_msg}. Serving partial rule-based intelligence report instead.",
        "product_regional_fit": {
            "fit_score": 75,
            "fit_rationale": "High volume clusters exist, but automated LLM evaluation is temporarily unavailable."
        },
        "top_sectors": [
            {
                "rank": idx + 1,
                "sector_name": s["name"],
                "demand_score": 8 - idx,
                "key_drivers": ["Regional industrial logistics clusters", "Regulatory standards"],
                "top_companies": [
                    {"company": c["company_name"], "rationale": c["snippet"][:100], "estimated_need": "Volume matching local cluster scale"}
                    for c in s.get("companies", [])[:5]
                ],
                "entry_difficulty": "Medium"
            }
            for idx, s in enumerate(context_bundle.get("sectors", []))
        ],
        "event_procurement_windows": event_windows,
        "potential_clients": potential_clients[:10],
        "competitive_landscape": {
            "main_competitors": context_bundle.get("competitive_landscape", {}).get("competitor_names", ["Regional players"]),
            "competitive_advantages_to_emphasize": ["High thermal payload duration", "GDP compliance certificates"],
            "market_gaps": ["Sustainable packaging materials", "Real-time thermal tracking integrations"]
        },
        "market_attractiveness_score": 70,
        "market_attractiveness_breakdown": {
            "market_size": 15,
            "growth_trajectory": 18,
            "competitive_intensity": 15,
            "event_driven_demand": 22
        },
        "strategic_recommendations": [
            {"priority": 1, "action": "Re-trigger LLM analysis when the NIM endpoint recovers.", "timeline": "Immediate", "expected_outcome": "Detailed AI synthesis"},
            {"priority": 2, "action": "Initiate target outreach to companies in the generic pharma sector.", "timeline": "30 Days", "expected_outcome": "Client discovery validation"},
            {"priority": 3, "action": "Validate local customs tariff compliance for PCM panel designs.", "timeline": "60 Days", "expected_outcome": "Reduced import frictions"}
        ]
    }
    return fallback
