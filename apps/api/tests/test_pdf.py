import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pdf_generator import generate_report_pdf

def test_pdf_generation():
    dummy_report = {
        "product": "Gel Packs",
        "region": "Europe",
        "generated_at": "2026-06-10T12:00:00.000Z",
        "executive_summary": "Test executive summary showing that the market opportunity is large and growing.",
        "product_regional_fit": {
            "fit_score": 85,
            "fit_rationale": "Test rationale for product regional fit."
        },
        "top_sectors": [
            {
                "rank": 1,
                "sector_name": "Healthcare & Pharmaceuticals",
                "demand_score": 9,
                "key_drivers": ["Vaccine logistics", "Clinical trials"],
                "entry_difficulty": "Medium",
                "top_companies": [
                    {"company": "BioPharma Corp", "rationale": "High volume payload needs", "estimated_need": "50,000 units"}
                ]
            }
        ],
        "event_procurement_windows": [
            {
                "event": "Medica Trade Fair",
                "date_window": "November 2026",
                "procurement_start": "2026-08-01T00:00:00.000Z",
                "sector": "Healthcare & Pharmaceuticals",
                "demand_spike_score": 8,
                "outreach_recommendation": "Launch target campaign in August."
            }
        ],
        "potential_clients": [
            {
                "company_name": "DHL Cold Chain Germany",
                "sector": "Healthcare & Pharmaceuticals",
                "region_country": "Germany",
                "relevance_rationale": "Operates major pharmaceutical hubs.",
                "estimated_annual_need": "100,000 units",
                "contact_strategy": "Pitch long duration thermal gel packs."
            }
        ],
        "competitive_landscape": {
            "main_competitors": ["Inmark", "Sonoco"],
            "competitive_advantages_to_emphasize": ["GDP compliance", "High payload duration"],
            "market_gaps": ["Eco-friendly materials"]
        },
        "market_attractiveness_score": 80,
        "market_attractiveness_breakdown": {
            "market_size": 18,
            "growth_trajectory": 22,
            "competitive_intensity": 16,
            "event_driven_demand": 24
        },
        "strategic_recommendations": [
            {
                "priority": 1,
                "action": "Set up distributor in Germany.",
                "timeline": "30 days",
                "expected_outcome": "Local sales pipeline established."
            }
        ]
    }
    
    pdf_bytes = generate_report_pdf(dummy_report)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
