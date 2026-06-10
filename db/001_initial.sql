-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: research_sessions
CREATE TABLE IF NOT EXISTS research_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product VARCHAR(255) NOT NULL, -- Gel Packs or PCM Panels
    region VARCHAR(100) NOT NULL,  -- US, India, Europe, Middle East, Southeast Asia
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES research_sessions(id) ON DELETE CASCADE,
    report_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: events_cache
CREATE TABLE IF NOT EXISTS events_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region VARCHAR(100) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    sector VARCHAR(255),
    relevance_score INT CHECK (relevance_score >= 1 AND relevance_score <= 100),
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_research_sessions_status ON research_sessions(status);
CREATE INDEX IF NOT EXISTS idx_reports_session_id ON reports(session_id);
CREATE INDEX IF NOT EXISTS idx_events_cache_region ON events_cache(region);

-- Table: search_cache
CREATE TABLE IF NOT EXISTS search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    search_type VARCHAR(100) NOT NULL,
    response_json JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_cache_lookup ON search_cache(product, region, search_type);

