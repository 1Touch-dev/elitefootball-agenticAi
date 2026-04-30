# elitefootball-agenticAi — Global Project Context

> **RULE**: Every agent and every major change MUST read this file first and update it after.

---

## 1. System Purpose

Football Player Valuation + Development Intelligence Platform for Independiente del Valle (IDV).

Converts fragmented multi-source football data into a consistent analytics system that:
- Values players with a true weighted model + potential score
- Identifies undervalued players (computed value vs market price)
- Projects development pathways
- Benchmarks clubs (IDV vs Benfica vs Ajax vs Salzburg)
- Serves a production-grade Next.js frontend
- Uses real scraped data; seed data is fallback only

---

## 2. Architecture

```
Data Sources → Scraping Layer → Bronze → Silver → Gold → API → Frontend
                                                        ↘ Agents
```

### Layers

| Layer | Location | Purpose |
|-------|----------|---------|
| Scraping | `app/scraping/` | Transfermarkt + FBref via Playwright; Crawl4AI optional (falls back to Playwright) |
| Bronze | `data/bronze/` | Raw HTML + parsed JSON per player/match |
| Silver | `data/silver/` | Normalised tables: players, matches, player_match_stats (incl. competition), player_per90, transfers |
| Gold | `data/gold/` | All analysis outputs: features, KPI, advanced metrics, risk, valuation, pathway, similarity, club benchmark |
| API | `app/api/routes.py` | FastAPI, port 9001. All endpoints incl. /undervalued |
| Frontend | `frontend/` | Next.js 15 App Router, port 3000. 8 pages: Dashboard, Players, Valuation, Undervalued, Compare, Pathway, Benchmark, Admin |
| Agents | `app/agents/` | Orchestrator → Analyst/Scraper/DataCleaner/ReportGenerator (all using v2 engines) |

---

## 3. Current State (as of 2026-04-30)

### Data
- **18 IDV players** with seeded Bronze/Silver data (real URLs registered but not yet scraped live)
- **91 match records** in Silver with competition field populated
- **0 external comparable players** scraped (Liga Pro rivals + graduates are URL-registered, not yet scraped)

### Fixes Applied This Session
1. ✅ competition field joined into player_match_stats in silver.py (was always null)
2. ✅ IDV pathway alias fixed ("independiente del valle" key added to PATHWAY_TEMPLATES)
3. ✅ xT now computed from real progressive carry/pass fields (was always null)
4. ✅ xG/xA now uses FBref source data when available; falls back to estimate
5. ✅ potential_score added to valuation (age-based ceiling multiplier)
6. ✅ market_value_eur parsed from raw string (€1.5m → 1500000)
7. ✅ undervalued flag + computed_value_eur added to valuation output
8. ✅ _expected_kpi() calibrated to real KPI scale (8-14, was 40-70)
9. ✅ analyst_agent.py updated to use all v2 engines
10. ✅ fbref.py log_event keyword collision fixed (source key conflict)
11. ✅ v1 analysis modules moved to app/analysis/legacy/
12. ✅ All test imports updated to use legacy paths
13. ✅ 144 tests passing, 0 failing
14. ✅ persistence _finalize_status uses core entity logic (excludes clubs from "nothing succeeded" check)
15. ✅ dashboard helpers handles empty dict correctly for no_sync state

### Remaining Known Gaps
- No real live scraping (Playwright blocked by anti-bot on Transfermarkt/FBref without proxies)
- market_value data in Bronze is seeded as None → undervalued detection uses "no market data" path
- Liga Pro rivals + IDV graduates not yet scraped (URLs registered in scripts/player_urls.py)
- EPV/OBV are labelled proxy metrics (not true StatsBomb event-level models)
- Success probability calibrated better but pathway percentile still approximate

---

## 4. Key Files

| File | Purpose |
|------|---------|
| `app/pipeline/silver.py` | Silver builder — includes competition field in player_match_stats |
| `app/pipeline/gold.py` | Gold features builder |
| `app/pipeline/run_pipeline.py` | Full pipeline (v2 only) |
| `app/analysis/advanced_metrics_v2.py` | xG (FBref), xA (FBref), xT (progressive actions), EPV proxy, OBV proxy |
| `app/analysis/valuation_v2.py` | Weighted model + potential_score + parse_market_value + undervalued flag |
| `app/analysis/pathway_engine.py` | Trajectory, pathway recommendation (IDV alias fixed), calibrated _expected_kpi |
| `app/analysis/similarity_v2.py` | Role-aware weighted Euclidean distance |
| `app/analysis/risk_engine.py` | Composite risk: injury × 0.45 + volatility × 0.40 + discipline × 0.15 |
| `app/analysis/kpi_engine.py` | Base KPI with age multiplier |
| `app/analysis/legacy/` | v1 modules — kept for test coverage only, not used in production pipeline |
| `app/agents/analyst_agent.py` | Uses v2 engines only |
| `app/api/routes.py` | All REST endpoints including GET /undervalued |
| `app/scraping/crawl4ai_engine.py` | Crawl4AI engine with Playwright fallback, 24h cache, retry logic |
| `scripts/player_urls.py` | Registry: 18 IDV players + 15 Liga Pro rivals + 10 IDV graduates |
| `frontend/lib/api.ts` | API client — server-side: direct, client-side: /api proxy |
| `frontend/app/undervalued/page.tsx` | Undervalued players page |

---

## 5. Run Commands

```bash
# Backend
/home/ubuntu/venv/bin/python -m uvicorn app.main:app --port 9001 --reload

# Frontend
cd frontend && npm run dev  # port 3000

# Full pipeline
/home/ubuntu/venv/bin/python -c "from app.pipeline.run_pipeline import run_pipeline; run_pipeline()"

# Tests (144 passing)
/home/ubuntu/venv/bin/python -m pytest tests/ -q
```

---

## 6. Valuation Formula

```
score = perf × 0.35 + age_curve × 0.20 + minutes_prob × 0.15
      + league_adj × 0.15 + club_dev × 0.10 − risk_disc × 0.05

potential_score = score × potential_multiplier(age)
  where: ≤19 → ×1.35 | ≤21 → ×1.20 | ≤23 → ×1.10 | ≤25 → ×1.05 | >25 → ×1.0

computed_value_eur = max(0, (score - 40) × €500k)
undervalued = computed_value_eur > market_value_eur × 1.25
```

---

## 7. Scraping Architecture

- **Crawl4AI** (`app/scraping/crawl4ai_engine.py`): preferred engine — structured JSON/Markdown, async, anti-bot
- **Playwright** (`app/scraping/browser.py`): fallback when Crawl4AI unavailable or for precise table scraping
- **Queue** (`app/scraping/queue.py`): HIGH (IDV), MEDIUM (tracked), LOW (discovery)
- **Retry**: 3 attempts, exponential backoff (1s, 2s, 4s)
- **Cache**: MD5 hash, 24h TTL in `data/bronze/crawl_cache/`
- **Player URL Registry**: `scripts/player_urls.py` — real Transfermarkt + FBref + Sofascore URLs

---

## 8. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /players | Player list with features/KPI/valuation |
| GET | /players/{name}/stats | Match stats for player |
| GET | /value | Valuation list or single player |
| GET | /undervalued | Players where model > market price |
| GET | /compare?player_name= | Similar players (v2 similarity) |
| GET | /pathway | All pathway recommendations |
| GET | /pathway/{name} | Single player pathway |
| GET | /benchmark | Club development benchmark |
| GET | /advanced-metrics | xG, xA, xT, EPV proxy, OBV proxy |
| POST | /admin/pipeline/run | Trigger full pipeline |
| GET | /admin/status | Artifact health check |
