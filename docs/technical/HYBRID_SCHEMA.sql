-- Tactics Hybrid Storage Schema (SOTA Supabase/PostgreSQL)

-- 1. Raw Ingestion Layer (NoSQL-style)
CREATE TABLE IF NOT EXISTS raw_payloads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id TEXT NOT NULL,
    provider_id TEXT NOT NULL, -- meta, google, shopify, zendesk
    payload JSONB NOT NULL,    -- Flexible raw data
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for deep payload search (SOTA Performance)
CREATE INDEX idx_raw_payload_gin ON raw_payloads USING GIN (payload);

-- 2. Structured Core (CRM/Sales)
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    revenue DECIMAL(12,2) DEFAULT 0.0,
    canal_origen TEXT, -- pos, online, shopify, meta
    metadata JSONB -- Extra transaction info
);

-- 3. Marketing Spend (Awareness Grid)
CREATE TABLE IF NOT EXISTS marketing_spend (
    id SERIAL PRIMARY KEY,
    company_id TEXT NOT NULL,
    channel TEXT NOT NULL, -- meta, google, tiktok
    date DATE NOT NULL,
    spend DECIMAL(12,2) NOT NULL,
    impressions BIGINT,
    clicks INTEGER
);

-- 4. Experience Context (Sentiment Grid)
-- Requires pgvector extension
-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS sentiment_signals (
    id SERIAL PRIMARY KEY,
    company_id TEXT NOT NULL,
    customer_id TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source TEXT NOT NULL, -- zendesk, intercom
    content_summary TEXT, -- For audit
    sentiment_score FLOAT, -- -1.0 to 1.0
    -- embedding vector(1536) -- Placeholder for OpenAI/Llama embeddings
    metadata JSONB
);

-- 5. Audit & Traceability
CREATE TABLE IF NOT EXISTS ingestion_receipts (
    batch_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    data_type TEXT NOT NULL,
    source TEXT NOT NULL,
    filename TEXT,
    input_row_count INTEGER,
    success_count INTEGER,
    error_count INTEGER,
    checksum TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    errors JSONB
);

CREATE INDEX idx_receipt_company ON ingestion_receipts(company_id);
CREATE INDEX idx_receipt_batch ON ingestion_receipts(batch_id);
