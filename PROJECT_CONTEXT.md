# elitefootball-agenticAi — Global Project Context

> **RULE**: Every agent and every major change MUST read this file first and update it after.

---

## 1. System Purpose

Football Player Valuation + Development Intelligence Platform for Independiente del Valle (IDV).

Converts fragmented multi-source football data into a consistent analytics system that:
- Values players with a true weighted model
- Projects development pathways
- Benchmarks clubs (IDV vs Benfica vs Ajax vs Salzburg)
- Serves a production-grade Next.js frontend

---

## 2. Architecture

```
Data Sources → Scraping Layer → Bronze → Silver → Gold → API → Frontend
                                                        ↘ Agents
```

### Layers

| Layer | Location | Purpose |
|-------|----------|---------|
| Scraping | `app/scraping/` | Transfermarkt, Sofascore, FBref (blocked), Tavily |
| Bronze | `data/bronze/` | Raw source artifacts + manifest |
| Silver | `data/silver/` | Cleaned tabular: players, player_match_stats, matches, transfers |
| Gold | `data/gold/` | Derived analytics: kpi, risk, similarity, valuation, pathways, club_benchmark |
| Analysis | `app/analysis/` | KPI, risk, similarity, valuation_v2, pathway, league_adjustment, club_benchmark, advanced_metrics |
| API | `app/api/` | FastAPI — port 9001 (dev) |
| Frontend | `frontend/` | Next.js App Router — port 3000 |
| Agents | `app/agents/` | orchestrator, scraper, data_cleaner, analyst, report_generator |

---

## 3. Data Pipeline Design

### Bronze
- Manifest: `data/bronze/manifest.json`
- Raw scrape artifacts stored per source

### Silver (cleaned tables)
- `players.json` — profile rows: name, dob, position, current_club, nationality
- `player_match_stats.json` — per-match rows: goals, assists, minutes, shots, cards
- `matches.json` — match metadata
- `transfers.json` — transfer history: fee, from_club, to_club, season

### Gold (derived)
- `kpi_engine.json` — base KPI, consistency score, age
- `player_risk.json` — risk score, tier, components
- `player_similarity.json` — nearest comps per player
- `player_valuation.json` — valuation_v2 output
- `player_features.json` — derived features: gc_per_90, shots, minutes
- `advanced_metrics.json` — xG, xA, xT, EPV, OBV estimates
- `club_development_rankings.json` — IDV vs Benfica vs Ajax vs Salzburg
- `player_pathway.json` — development trajectory and career pathway output

---

## 4. Valuation Formula (v2)

```
Player Value Score = clamp(
  Performance Score × 0.35
  + Age Curve × 0.20
  + Minutes Probability × 0.15
  + League Adjustment × 0.15
  + Club Development Factor × 0.10
  - Risk Discount × 0.05
, min=0, max=100)
```

### Component definitions
- **Performance Score** (0–100): weighted KPI + advanced metrics (xG, xA, progression)
- **Age Curve** (0–100): peaks at 24–26, decays exponentially after 30
- **Minutes Probability** (0–100): availability signal from minutes / (matches × 90)
- **League Adjustment** (−10 to +15): coefficient per competition tier
- **Club Development Factor** (0–20): IDV historically +12 (proven pathway)
- **Risk Discount** (0–25): composite risk score penalty

### Configurable weights
Stored in `app/analysis/valuation_v2.py` as `ValuationWeights` dataclass — overridable at runtime.

---

## 5. KPI Definitions

| KPI | Formula |
|-----|---------|
| base_kpi_score | weighted sum of gc_per_90, shots_per_90, minutes_share |
| consistency_score | 1 − coefficient_of_variation(minutes_series) |
| age_score | peak curve centered at 25 |
| minutes_score | minutes / (matches × 90), capped at 1.0 |
| discipline_risk | yellow_cards + 2×red_cards, normalized |

---

## 6. Scraping Strategy

### Priority order
1. **Transfermarkt** — primary: squad lists, player profiles, transfer history
2. **Sofascore** — secondary: per-match stats enrichment
3. **FBref** — tertiary (Cloudflare-blocked in this env; handled with graceful fallback)
4. **Tavily** — URL discovery and source prioritization

### Architecture
- Queue-based: `app/scraping/queue.py` — priority scheduling + incremental updates
- Browser abstraction: `app/scraping/browser.py` — Playwright with graceful unavailability
- Caching: raw HTML cached per slug to avoid redundant fetches

---

## 7. League Coefficients

| League | Coefficient |
|--------|------------|
| Premier League | +15 |
| La Liga | +14 |
| Bundesliga | +13 |
| Serie A | +13 |
| Ligue 1 | +12 |
| Eredivisie | +10 |
| Primeira Liga | +10 |
| Copa Libertadores | +8 |
| Liga Pro (Ecuador) | +5 |
| Other South America | +3 |
| Unknown | 0 |

---

## 8. Development Pathway Model

Output per player:
- `development_stage`: prospect / emerging / peak / veteran
- `trajectory`: ascending / stable / declining
- `improvement_rate`: δ(KPI) / season
- `development_velocity`: weighted rate vs age peers
- `best_pathway`: recommended next club tier
- `success_probability`: 0–1 based on comparable player outcomes

---

## 9. Club Benchmarking

Tracked clubs: IDV, Benfica, Ajax, Salzburg

Metrics:
- `player_improvement_rate`: avg KPI delta during club tenure
- `resale_multiplier`: avg exit value / entry value
- `success_rate`: % players who progressed to higher league

---

## 10. Advanced Metrics (Simplified Models)

These are model-estimated from available stats (no event-level data required):

| Metric | Estimation method |
|--------|-----------------|
| xG | shots × positional_factor (header/open-play/set-piece) |
| xA | key_passes × conversion_rate_of_chances |
| xT | progressive_actions × threat_multiplier |
| EPV | expected possession value change per action |
| OBV | on-ball value: sum of xT contributions |

---

## 11. Multi-Agent System

| Agent | Role |
|-------|------|
| orchestrator | Routes tasks: scrape → clean → analyse → report |
| scraper_agent | Calls scraping layer, logs to DB |
| data_cleaner_agent | Bronze→Silver→Gold pipeline run |
| analyst_agent | KPI, risk, similarity, valuation, pathway |
| report_generator_agent | Operator summaries |

---

## 12. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /summary | System summary |
| GET | /dashboard/status | Artifact readiness |
| GET | /players | Player list (filterable) |
| GET | /players/{name}/stats | Per-player match stats |
| GET | /compare | Similarity results |
| GET | /value | Valuation scores |
| GET | /pathway/{name} | Development pathway |
| GET | /benchmark | Club benchmarks |
| POST | /safety/evaluate | Safety policy check |
| POST | /api/tasks | Trigger agent task |

---

## 13. Frontend (Next.js)

- Location: `frontend/`
- Port: 3000
- EC2 URL: http://54.224.251.181:3000
- Stack: Next.js App Router, TypeScript, Tailwind CSS
- Pages: `/` (dashboard), `/player/[name]`, `/compare`, `/valuation`, `/admin`

---

## 14. Environment Variables

```
APP_ENV=development
SCRAPE_HEADLESS=false
TAVILY_API_KEY=tvly-dev-...
ELITEFOOTBALL_API_BASE_URL=http://127.0.0.1:9001
```

---

## 15. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-04-29 | Initial PROJECT_CONTEXT.md created | pap-247-full-intelligence-upgrade |
