import sys
import os
import pytest

# Adjust paths to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.web_search import (
    search_market_overview,
    search_top_companies,
    search_industry_news,
    search_competitive_landscape
)

@pytest.mark.anyio
async def test_search_market_overview():
    res = await search_market_overview("Gel Packs", "India")
    assert isinstance(res, dict)
    assert "combined_snippets" in res
    assert "top_urls" in res
    assert "source_names" in res
    assert isinstance(res["top_urls"], list)
    assert isinstance(res["source_names"], list)

@pytest.mark.anyio
async def test_search_top_companies():
    res = await search_top_companies("Pharma", "India", ["cold chain", "vaccine"])
    assert isinstance(res, list)
    if len(res) > 0:
        first = res[0]
        assert "company_name" in first
        assert "snippet" in first
        assert "url" in first
        assert "relevance_score" in first
        assert isinstance(first["relevance_score"], (int, float))

@pytest.mark.anyio
async def test_search_industry_news():
    res = await search_industry_news("Gel Packs", "India", ["Arab Health", "CPHI"])
    assert isinstance(res, list)
    if len(res) > 0:
        first = res[0]
        assert "headline" in first
        assert "source" in first
        assert "date" in first
        assert "url" in first
        assert "event_trigger_matched" in first

@pytest.mark.anyio
async def test_search_competitive_landscape():
    res = await search_competitive_landscape("Gel Packs", "India")
    assert isinstance(res, dict)
    assert "competitor_names" in res
    assert "market_share_notes" in res
    assert "barriers_to_entry" in res
    assert isinstance(res["competitor_names"], list)
