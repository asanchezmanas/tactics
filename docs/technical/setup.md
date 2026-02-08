# Setup & Configuration Guide

To get the **Tactics** project running locally or in production, follow these steps.

## 1. Environment Variables
Create a `.env` file in the project root with the following keys:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Resilient Database (Optional - defaults shown)
LOCAL_CACHE_PATH=.cache/tactics.db
RETRY_QUEUE_PATH=.cache/retry_queue.json

# Shopify (Placeholder for Auth)
SHOPIFY_API_KEY=your-api-key
SHOPIFY_API_SECRET=your-api-secret

# Meta Ads (Placeholder for Auth)
FB_APP_ID=your-app-id
FB_APP_SECRET=your-app-secret
```

## 2. Database Initialization
1. Create a new project in [Supabase](https://supabase.com/).
2. Go to the **SQL Editor**.
3. Execute the schema from [db_schema.sql](file:///c:/Users/Artur/tactics/docs/db_schema.sql).
4. **For JSONB support**, also execute:

```sql
CREATE TABLE IF NOT EXISTS insights_jsonb (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    insight_type TEXT NOT NULL,
    data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_insights_company ON insights_jsonb(company_id);
CREATE INDEX idx_insights_type ON insights_jsonb(insight_type);
CREATE INDEX idx_insights_data_gin ON insights_jsonb USING GIN (data);
```

## 3. Installation
Install the required Python dependencies:

```bash
pip install -r requirements.txt

# For Enterprise SOTA features (optional):
pip install tensorflow pymc nevergrad
```

## 4. Running the API
Start the FastAPI server:

```bash
python api/main.py
```
The API will be available at `http://localhost:8000`.

- **Health Check**: `GET /health` - Returns database and cache status
- **Trigger Sync**: `POST /sync-all` with body `{"company_id": "your-uuid"}`
- **Budget Simulation**: `POST /simulate-budget` with body `{"company_id": "your-uuid", "total_budget": 5000}`

## 5. Testing
Run the test suite:

```bash
# Core algorithm tests
pytest tests/test_core.py -v

# Enterprise SOTA tests
pytest tests/test_enterprise.py -v

# Resilient database tests
pytest tests/test_database_resilient.py -v

# All tests
pytest tests/ -v
```

## 6. Offline Mode
The resilient database layer automatically creates a local SQLite cache at `LOCAL_CACHE_PATH`. If Supabase is unavailable:
- **Reads**: Use cached data (with configurable TTL)
- **Writes**: Queue for automatic retry when connection is restored
- **Health**: Check `/health` endpoint for system status
