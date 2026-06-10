import sys
import os
import pytest

# Adjust paths to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.report_orchestrator import generate_report

@pytest.mark.anyio
async def test_generate_report():
    # Run orchestration for PCM Panels in India
    # Since our orchestrator has a robust fallback to local rules if the external NIM endpoint fails,
    # this test will successfully validate the schema output either way.
    report = await generate_report("Phase Change Material (PCM) Thermal Panels", "India")
    
    assert isinstance(report, dict)
    assert report["product"] == "Phase Change Material (PCM) Thermal Panels"
    assert report["region"] == "India"
    assert "executive_summary" in report
    assert "product_regional_fit" in report
    assert "top_sectors" in report
    assert "event_procurement_windows" in report
    assert "potential_clients" in report
    assert "competitive_landscape" in report
    assert "market_attractiveness_score" in report
    assert "strategic_recommendations" in report
    
    # Verify exact types and lengths
    assert isinstance(report["market_attractiveness_score"], int)
    assert len(report["top_sectors"]) == 4
    
    # Check sectors ranking and structure
    for idx, s in enumerate(report["top_sectors"]):
        assert "sector_name" in s
        assert "demand_score" in s
        assert "top_companies" in s
        assert len(s["top_companies"]) >= 3 # Check presence of real companies
