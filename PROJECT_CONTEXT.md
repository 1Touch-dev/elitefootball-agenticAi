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
- **150+ players** URL-registered across IDV, Liga Pro rivals, Brazilian clubs, Argentine clubs, and IDV graduates
- **0 external comparable players** scraped live (Playwright blocked by anti-bot without proxies)

### Fixes Applied (Intelligence Upgrade)
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

### Intelligence Layer (Phase 3–6, 2026-04-30)
24. ✅ app/validation/cross_source_validator.py — confidence_score per player (cross-source × 0.45 + internal × 0.35 + coverage × 0.20)
25. ✅ app/validation/drift_detector.py — z-score spike/drop detection, career drift (improving/stable/declining)
26. ✅ KPI engine + valuation v2 now accept confidence_index → confidence_weighted_kpi / confidence_weighted_score
27. ✅ app/analysis/transfer_probability.py — logistic regression: perf × age × trajectory × league_vis × club_export × contract
28. ✅ app/analysis/club_fit.py — 16 target clubs, 5 components (role/age/league/value/pathway), top-5 output
29. ✅ app/analysis/market_value_model.py — base_league × performance^1.4 × age_gaussian × demand; blended with real TM value
30. ✅ app/analysis/clustering_engine.py — pure-Python k-means++, k=5 archetypes (clinical_striker/playmaker/engine/wide_creator/workhorse)
31. ✅ app/analysis/alert_system.py — UNDERVALUED / BREAKOUT / DECLINE alerts with severity tiers
32. ✅ app/analysis/feature_store.py — consolidated normalized feature record per player → data/gold/feature_store.json
33. ✅ scripts/player_urls.py — expanded to 187 players: +Portugal(12) +Eredivisie(10) +Belgium(8) +Austria(6) +BrazilSerieA(8) +Argentina(8)
34. ✅ app/scraping/discovery_engine.py — AsyncWebCrawler.arun_many() across 6 league pages, entity_resolution dedup, auto-enqueue
35. ✅ API: /transfer-probability /club-fit /club-fit/{name} /market-value /clusters /alerts /feature-store /admin/discover
36. ✅ Frontend: /intelligence (transfer prob + club fit) /alerts /market-value pages; Nav + Dashboard updated
37. ✅ 17 Gold artifacts, 144 tests passing

### Scraping Infrastructure (Continuous Pipeline)
16. ✅ app/scraping/job_queue.py — Persistent JSON priority queue (HIGH/IDV, MEDIUM/Liga Pro, LOW/discovery)
17. ✅ app/scraping/entity_resolution.py — Cross-source player matching (name sim + age + club + position)
18. ✅ app/scraping/browser.py — Hardened with retry (3× exp backoff), rate limiting (1–5s random), proxy support, fake-useragent UA rotation
19. ✅ app/orchestration/scrape_runner.py — run_full_scrape_cycle() + run_scrape_batch() + change detection (SHA-256 HTML hash)
20. ✅ app/orchestration/scheduler.py — APScheduler: daily IDV (03:00 ECT), weekly tracked (Mon 04:00), monthly discovery (1st 05:00)
21. ✅ app/pipeline/run_pipeline.py — run_incremental_pipeline(player_slugs) for targeted Silver+Gold rebuild
22. ✅ app/pipeline/silver.py — build_silver_tables_for_players(slugs) for incremental filtering
23. ✅ /admin/status now includes job_queue stats + scheduler status

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

### Engines
- **Crawl4AI** (`app/scraping/crawl4ai_engine.py`): preferred — structured JSON/Markdown, async, anti-bot bypass
- **Playwright** (`app/scraping/browser.py`): fallback — hardened with retry (3× exp backoff), random rate limit (1–5s), proxy support, UA rotation via fake-useragent

### Job Queue (`app/scraping/job_queue.py`)
- Persists to `data/bronze/job_queue.json`
- Priority tiers: HIGH=1 (IDV), MEDIUM=5 (Liga Pro rivals), LOW=10 (discovery)
- 24h TTL freshness check — skips jobs already scraped recently
- `reset_in_progress()` — crash recovery for stuck jobs
- Helpers: `build_idv_jobs()`, `build_liga_pro_jobs()`, `build_discovery_jobs()`

### Scrape Runner (`app/orchestration/scrape_runner.py`)
- `run_full_scrape_cycle(tiers, force_refresh)` — enqueues + processes all batches
- `run_scrape_batch(queue, batch_size, trigger_pipeline)` — one batch of up to N jobs
- **Change detection**: SHA-256 hash of HTML stored in `data/bronze/change_hashes/`; pipeline only triggered when content actually changed
- Triggers `run_incremental_pipeline(slugs)` automatically after each changed batch

### Scheduler (`app/orchestration/scheduler.py`)
- APScheduler BackgroundScheduler in America/Guayaquil (IDV timezone, UTC-5)
- **Daily** 03:00 ECT — IDV players only
- **Weekly** Monday 04:00 ECT — IDV + Liga Pro rivals
- **Monthly** 1st 05:00 ECT — full discovery (all 150+ players)
- **Weekly** Sunday 02:00 ECT — queue cleanup (purge DONE/SKIPPED)
- Start: `python -m app.orchestration.scheduler`
- Status visible at: `GET /admin/status` → `scheduler` key

### Entity Resolution (`app/scraping/entity_resolution.py`)
- `compute_match_score(record_a, record_b)`: name similarity (60%) + age (20%) + club (12%) + position (8%)
- `resolve_player_slug(record, known_players)`: returns (slug, confidence) — 0.88+ = confident, 0.80+ = low-confidence warning
- `deduplicate_player_list(players)`: merges records by slug after cross-source ingestion

### Cache + Change Detection
- **Crawl4AI cache**: MD5-keyed, 24h TTL in `data/bronze/crawl_cache/`
- **Change hash**: SHA-256 of raw HTML in `data/bronze/change_hashes/{job_id}.hash`
- **Job queue TTL**: 24h — `is_fresh()` check prevents redundant re-enqueue

### Player URL Registry
- `scripts/player_urls.py` — 150 players: IDV(18) + Liga Pro(26) + Brazil(27) + Argentina(23) + Copa Lib(8) + IDV Graduates(11) + European Youth(22) + others
- Sections: `IDV_PLAYER_URLS`, `LIGA_PRO_RIVAL_URLS`, `ALL_PLAYER_URLS`

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
