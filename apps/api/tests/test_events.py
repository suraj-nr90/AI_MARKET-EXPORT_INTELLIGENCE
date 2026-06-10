import sys
import os
import pytest

# Adjust paths to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.event_intelligence import (
    fetch_live_events,
    map_events_to_sectors,
    get_event_intelligence_async
)

@pytest.mark.anyio
async def test_fetch_live_events():
    events = await fetch_live_events("United States", ["expos", "sports"])
    assert isinstance(events, list)
    if len(events) > 0:
        first = events[0]
        assert "event_name" in first
        assert "event_date" in first
        assert "location" in first
        assert "category" in first
        assert "phq_rank" in first

@pytest.mark.anyio
async def test_get_event_intelligence_gel_packs_us():
    events = await get_event_intelligence_async("Gel Packs", "United States")
    assert isinstance(events, list)
    # The requirement is that we return at least 5 events, up to 10
    assert len(events) >= 5
    assert len(events) <= 10
    for e in events:
        assert "event_name" in e
        assert "event_date_or_window" in e
        assert "location" in e
        assert "matched_sector" in e
        assert "procurement_window_start" in e
        assert "demand_spike_score" in e
        assert "recommended_action" in e
        assert 1 <= e["demand_spike_score"] <= 10

@pytest.mark.anyio
async def test_get_event_intelligence_pcm_panels_europe():
    events = await get_event_intelligence_async("PCM Thermal Panels", "Europe")
    assert isinstance(events, list)
    assert len(events) >= 5
    assert len(events) <= 10
    for e in events:
        assert "event_name" in e
        assert "event_date_or_window" in e
        assert "location" in e
        assert "matched_sector" in e
        assert "procurement_window_start" in e
        assert "demand_spike_score" in e
        assert "recommended_action" in e
        assert 1 <= e["demand_spike_score"] <= 10
