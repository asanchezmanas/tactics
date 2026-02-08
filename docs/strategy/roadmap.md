# Project Roadmap: Marketing AI Insights

## 🎯 Vision
A premium B2B SaaS that acts as the "Strategic Brain" for e-commerce marketing departments. It transforms raw transaction and ad spend data into actionable predictions for customer retention (LTV/Churn) and budget optimization (MMM).

## 🧩 Core Modules

### 1. Customer Intelligence (LTV & Churn)
- **Engine**: Probabilistic models (BG/NBD & Gamma-Gamma).
- **Goal**: Predict future purchases and identifying at-risk VIP clients.
- **Value**: "Don't lose your best customers."

### 2. Marketing Mix Modeling (MMM)
- **Engine**: Non-linear optimization with Hill saturation and Adstock filters.
- **Goal**: Optimal budget allocation across channels (Meta, Google, TikTok, SEO).
- **Value**: "Invest every euro where it yields the most long-term value."

### 3. Data Connectors
- **Ingestion**: Shopify, Meta Ads, Google Ads, Google Search Console.
- **Strategy**: Incremental loads to Supabase for efficiency.

### 4. Strategic Dashboard
- **Views**: Executive Summary, Customer Explorer, Channel Anatomy, Sandbox Simulator.

---

## 📈 Development Phases

### Phase 1: The Core (Starting Now)
- [ ] Implement `DataScienceCore` (Python).
- [ ] Implement Budget Optimizer (Python).
- [ ] Establish Supabase Schema.

### Phase 2: The API & Connectivity
- [ ] Develop FastAPI backend.
- [ ] Implement Shopify and Meta Ads connectors.
- [ ] OAuth integration logic.

### Phase 3: The Dashboard (Stitch AI focus)
- [ ] Frontend development with modern UI (Stripe-like aesthetics).
- [ ] Interactive Budget Simulator.
- [ ] Automated insights generation (GPT-4o powered).

### Phase 4: Launch & Scale
- [ ] Deployment to Render.
- [ ] Beta testing with initial stores.
- [ ] Pricing model activation ($100 Basic / $150 Pro).
