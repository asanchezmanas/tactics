-- SQL Schema for Marketing AI Insights (Supabase / PostgreSQL)

-- 1. Companies Table (Multi-tenancy)
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    tier TEXT DEFAULT 'core' CHECK (tier IN ('core', 'enterprise')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Integrations Table (OAuth tokens)
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    service_name TEXT NOT NULL, -- 'shopify', 'meta_ads', 'google_ads', 'search_console'
    access_token TEXT NOT NULL, -- Should be encrypted in production
    shop_url TEXT, -- Specifically for Shopify
    last_sync TIMESTAMP WITH TIME ZONE,
    UNIQUE(company_id, service_name)
);

-- 3. Clients Table (Customer dimensions)
CREATE TABLE IF NOT EXISTS clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    external_id TEXT NOT NULL, -- Shopify Customer ID
    email TEXT,
    nombre TEXT,
    segmento_ia TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, external_id)
);

-- 4. Sales Table (Transaction facts)
CREATE TABLE IF NOT EXISTS ventas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    order_id TEXT NOT NULL, -- Shopify Order ID
    fecha_venta TIMESTAMP WITH TIME ZONE NOT NULL,
    monto_total NUMERIC(12, 2) NOT NULL,
    moneda TEXT DEFAULT 'EUR',
    canal_origen TEXT,
    UNIQUE(company_id, order_id)
);

CREATE INDEX IF NOT EXISTS idx_ventas_fecha_company ON ventas (company_id, fecha_venta);

-- 5. Marketing Spend Table (Aggregated facts)
CREATE TABLE IF NOT EXISTS gastos_marketing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    canal TEXT NOT NULL, -- 'Meta Ads', 'Google Ads', 'TikTok', 'SEO'
    inversion NUMERIC(12, 2) NOT NULL DEFAULT 0,
    impresiones INTEGER DEFAULT 0,
    clics INTEGER DEFAULT 0,
    UNIQUE(company_id, fecha, canal)
);

CREATE INDEX IF NOT EXISTS idx_marketing_fecha_canal ON gastos_marketing (company_id, fecha, canal);

-- 6. Core Insights Table (Model outputs)
CREATE TABLE IF NOT EXISTS insights_core (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    probabilidad_churn FLOAT,
    ltv_predicho_12m NUMERIC(12, 2),
    compras_esperadas_90d FLOAT,
    ultima_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, cliente_id)
);

-- Row Level Security (RLS) - Production Policies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE ventas ENABLE ROW LEVEL SECURITY;
ALTER TABLE gastos_marketing ENABLE ROW LEVEL SECURITY;
ALTER TABLE insights_core ENABLE ROW LEVEL SECURITY;

-- 1. Policy for companies
CREATE POLICY company_isolation ON companies 
    FOR ALL USING (id = (auth.jwt() ->> 'company_id')::uuid);

-- 2. Policy for integrations
CREATE POLICY integration_isolation ON integrations 
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::uuid);

-- 3. Policy for clientes
CREATE POLICY client_isolation ON clientes 
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::uuid);

-- 4. Policy for ventas
CREATE POLICY sales_isolation ON ventas 
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::uuid);

-- 5. Policy for gastos_marketing
CREATE POLICY marketing_isolation ON gastos_marketing 
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::uuid);

-- 6. Policy for insights_core
CREATE POLICY insights_isolation ON insights_core 
    FOR ALL USING (company_id = (auth.jwt() ->> 'company_id')::uuid);
