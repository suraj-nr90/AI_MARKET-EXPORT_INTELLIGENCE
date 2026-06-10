import sys
import os

# Adjust paths to import from knowledge module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.product_kb import PRODUCT_KB
from knowledge.regions import REGIONS

def test_product_kb_structure():
    # Verify both products exist
    assert "gel_packs" in PRODUCT_KB
    assert "pcm_panels" in PRODUCT_KB
    
    # Check Gel Packs product sectors and structures
    gel_packs = PRODUCT_KB["gel_packs"]
    assert gel_packs["name"] == "Advanced Temperature-Controlled Gel Packs"
    assert len(gel_packs["sectors"]) == 4
    for sector in gel_packs["sectors"]:
        assert "name" in sector
        assert "applications" in sector
        assert "event_triggers" in sector
        assert "peak_timing" in sector
        assert "demand_keywords" in sector
        assert isinstance(sector["applications"], list)
        assert isinstance(sector["event_triggers"], list)
        assert isinstance(sector["demand_keywords"], list)
        
    # Check PCM Panels product sectors and structures
    pcm_panels = PRODUCT_KB["pcm_panels"]
    assert pcm_panels["name"] == "Phase Change Material (PCM) Thermal Panels"
    assert len(pcm_panels["sectors"]) == 4
    for sector in pcm_panels["sectors"]:
        assert "name" in sector
        assert "applications" in sector
        assert "event_triggers" in sector
        assert "peak_timing" in sector
        assert "demand_keywords" in sector
        assert isinstance(sector["applications"], list)
        assert isinstance(sector["event_triggers"], list)
        assert isinstance(sector["demand_keywords"], list)

def test_regions_structure():
    # Verify all 5 regions exist and have cluster, regulatory, event and currency details
    expected_regions = ["United States", "India", "Europe", "Middle East", "Southeast Asia"]
    for reg in expected_regions:
        assert reg in REGIONS
        data = REGIONS[reg]
        assert "key_industry_clusters" in data
        assert "regulatory_bodies" in data
        assert "dominant_trade_events" in data
        assert "currency" in data
        assert "import_notes" in data
        assert isinstance(data["key_industry_clusters"], list)
        assert isinstance(data["regulatory_bodies"], list)
        assert isinstance(data["dominant_trade_events"], list)
        assert isinstance(data["currency"], str)
        assert isinstance(data["import_notes"], str)
