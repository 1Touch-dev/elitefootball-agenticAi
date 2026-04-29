# elitefootball-agenticAi

A full-stack football intelligence platform for **Independiente del Valle (IDV)** — combining a Python data pipeline, AI-powered analytics engine, and a Next.js dashboard to surface player valuations, development trajectories, similarity comparisons, and club benchmarking in one place.

---

## What It Does

The platform automates the entire data-to-insight pipeline for IDV's player squad:

1. **Scrapes** player profiles and match statistics from Transfermarkt and FBref
2. **Processes** raw data through a Bronze → Silver → Gold medallion architecture
3. **Computes** advanced analytics: KPI scores, xG/xA/xT/EPV/OBV, valuation, risk, trajectory, similarity
4. **Exposes** all results via a REST API (FastAPI, port 9001)
5. **Visualises** everything in a modern dashboard (Next.js, port 3000)

The system is designed around IDV's specific need to identify, evaluate, and track players for European transfer pathways — inspired by the development models of Benfica, Ajax, and Red Bull Salzburg.

---

## Live Deployment

| Service | URL |
|---|---|
| Frontend Dashboard | `http://54.224.251.181:3000` |
| REST API | `http://54.224.251.181:9001` |
| API Docs (Swagger) | `http://54.224.251.181:9001/docs` |

---

## Tech Stack

### Backend

| Technology | Role |
|---|---|
| **Python 3.14** | Core language for the pipeline and API |
| **FastAPI** | REST API server (port 9001) |
| **Uvicorn** | ASGI server running FastAPI |
| **SQLAlchemy + SQLite** | Persistence layer (`elitefootball.db`) for player, match, and transfer records |
| **Playwright** | Headless browser scraping from Transfermarkt and FBref |
| **Requests** | HTTP fallback for lightweight data fetches |
| **Pydantic** | Request/response schema validation in FastAPI |
| **Celery + Redis** | Background task queue for async pipeline runs (configured, env-optional) |

### Frontend

| Technology | Role |
|---|---|
| **Next.js 16 (App Router)** | Full-stack React framework, server components, port 3000 |
| **TypeScript** | Type-safe frontend code |
| **Tailwind CSS v4** | Utility-first styling, dark theme (`slate-950` base) |
| **Recharts** | Data visualisation (score bars, trend charts) |
| **Heroicons** | SVG icon set |
| **Axios** | HTTP client for client-side API calls |
| **Next.js API Routes** | Server-side proxy to backend (eliminates CORS) |

### Data & Analytics

| Technology | Role |
|---|---|
| **Transfermarkt** (via Playwright) | Player profiles, market valuations, transfer history |
| **FBref** (via Playwright) | Match statistics, per-90 metrics, competition data |
| **Custom KPI Engine** | Weighted composite score from goals, assists, minutes, consistency |
| **Valuation Model v2** | Gaussian-weighted scoring: performance + age + minutes + league + club − risk |
| **Similarity Engine v2** | Role-aware weighted Euclidean distance across normalised feature vectors |
| **Pathway Engine** | Rolling KPI trajectory, development velocity, European pathway recommendations |
| **Advanced Metrics v2** | xG/xA/xT/EPV/OBV estimated from aggregated match stats |
| **Club Benchmark** | IDV vs Benfica vs Ajax vs Salzburg across resale, improvement rate, success rate |
| **League Adjustment** | Coefficient-based normalisation (Premier League=15 down to Liga Pro=5) |
| **Risk Engine** | Injury availability proxy + discipline scoring |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                            │
│   Transfermarkt (player profiles)  FBref (match stats)     │
└────────────────────┬────────────────────────────────────────┘
                     │ Playwright scraper
┌────────────────────▼────────────────────────────────────────┐
│                  Bronze Layer                               │
│   data/raw/        Immutable scraped HTML/JSON              │
│   data/parsed/     Normalised parsed payloads               │
│   data/bronze/manifest.json  Artifact registry             │
└────────────────────┬────────────────────────────────────────┘
                     │ silver.py
┌────────────────────▼────────────────────────────────────────┐
│                  Silver Layer  (data/silver/)               │
│   players.json            player_match_stats.json           │
│   transfers.json          player_per90.json                 │
└────────────────────┬────────────────────────────────────────┘
                     │ gold.py + analysis engines
┌────────────────────▼────────────────────────────────────────┐
│                   Gold Layer  (data/gold/)                  │
│   player_features.json    kpi_engine.json                   │
│   player_valuation.json   player_similarity.json            │
│   player_pathway.json     advanced_metrics.json             │
│   club_benchmark.json     player_risk.json                  │
│   transfer_features.json  match_features.json               │
└────────────────────┬────────────────────────────────────────┘
                     │ FastAPI routes
┌────────────────────▼────────────────────────────────────────┐
│              REST API  (FastAPI, port 9001)                 │
└────────────────────┬────────────────────────────────────────┘
                     │ Next.js API proxy (no CORS)
┌────────────────────▼────────────────────────────────────────┐
│         Next.js Dashboard  (port 3000)                      │
│   Dashboard · Players · Valuation · Compare                 │
│   Pathway · Benchmark · Admin                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Dashboard Pages

### Dashboard (/)
The home page shows the overall system health at a glance.

- **API status** — live green/red indicator
- **Artifact count** — how many of the 11 Gold artifacts are populated and ready
- **Last sync timestamp** — when the pipeline last ran successfully
- **Artifact status table** — per-artifact row counts and ready/missing/empty state
- **Quick-nav cards** — one-click access to every section

### Players (/players)
Browse and search the full IDV squad.

- Search by player name or filter by position (Forward, Midfielder, Defender, Goalkeeper)
- Each player card shows name, position, club, nationality, age, and key stats
- Click any player to open the **detail page** (`/players/{name}`) which shows:
  - Valuation score with component breakdown (performance, age curve, league factor, etc.)
  - Future value projections at 2-year and 5-year horizons
  - Advanced metrics: xG, xA, EPV per 90, OBV, progression score
  - KPI score with consistency and risk sub-scores
  - Full match-by-match statistics table
  - Similar players panel with similarity scores and comp classifications (successful / neutral / failed)

### Valuation (/valuation)
Ranked list of all players by valuation score.

- Filter by tier: **high** (≥65), **mid** (40–65), **low** (<40)
- Each row shows: player name, position, club, valuation score with a colour-coded score bar, and tier badge
- Scores are computed by the **Valuation Model v2**:
  ```
  score = performance×0.35 + age_curve×0.20 + minutes×0.15
        + league_adj×0.15 + club_dev×0.10 − risk×0.05
  ```
  where `age_curve` is a Gaussian peaked at age 25

### Compare (/compare)
Role-aware similarity search powered by weighted Euclidean distance.

- Type any player name into the live search box
- Results show the top 5 most similar players with:
  - Similarity score (0–1)
  - Distance metric
  - Comp classification: **successful** (comp outperformed target), **neutral**, or **failed** (comp underperformed)
- Similarity is computed on 9 features (goals/90, shots, minutes, KPI, consistency, discipline, xG/90, xA/90, progression) weighted by the player's role profile

### Pathway (/pathway)
Career development intelligence for the whole squad.

- Lists all players ranked by success probability
- Each row shows:
  - **Development stage**: Prospect (<21) · Emerging (21–24) · Peak (24–29) · Veteran (29+)
  - **Trajectory**: Ascending / Stable / Declining (derived from rolling KPI history)
  - **Success probability**: 0–1 composite score from trajectory, age, valuation, and age-vs-league percentile
  - **Best pathway**: recommended next leagues (e.g. "primeira liga", "eredivisie", "bundesliga")
- Trajectory is computed from rolling 3-match KPI contribution windows. Young players (≤22) with single-point history default to ascending

### Benchmark (/benchmark)
Club development comparison: IDV vs Benfica vs Ajax vs Salzburg.

- Card per club showing:
  - **Development score**: Ajax=95 · Benfica=90 · Salzburg=88 · IDV=75
  - **Reference benchmarks** (seeded historical data): avg improvement rate, resale multiplier, success rate, avg age at breakout, players exported to Europe
  - **Live metrics** (from current pipeline data): player count, avg KPI score, avg consistency score
  - **Delta vs IDV**: how each club's metrics compare to IDV as the baseline
- Helps IDV understand the gap to replicate Benfica/Ajax/Salzburg development outcomes

### Admin (/admin)
Pipeline control and system diagnostics.

- **Run Pipeline** button — triggers a full Bronze→Silver→Gold pipeline rebuild via `POST /admin/pipeline/run`
- **Artifact status panel** — per-artifact state, row counts, last modified timestamps, error messages
- **System info** — API base URL, environment, backend health

---

## API Reference

All endpoints are served from port 9001. The frontend proxies them via `/api/*` (no CORS required).

### Core Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `GET` | `/summary` | Pipeline + artifact summary |
| `GET` | `/dashboard/status` | Full artifact health report with diagnostics |

### Player Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/players` | List all players. Query params: `limit`, `offset`, `position`, `search` |
| `GET` | `/players/{player_name}/stats` | Full stats for one player including features, KPI, advanced metrics |

### Analysis Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/compare?player_name=...` | Top-5 similar players for a given player |
| `GET` | `/value` | Ranked valuation list. Optional: `player_name`, `limit`, `offset`, `tier` |
| `GET` | `/pathway` | All players ranked by success probability. Optional: `limit`, `offset` |
| `GET` | `/pathway/{player_name}` | Pathway detail for one player |
| `GET` | `/benchmark` | Club benchmark data for IDV, Benfica, Ajax, Salzburg |
| `GET` | `/advanced-metrics` | xG/xA/xT/EPV/OBV for all players. Optional: `player_name`, `limit` |

### Admin Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/admin/pipeline/run` | Trigger full pipeline rebuild |
| `GET` | `/admin/status` | Artifact states, row counts, error messages |

### Safety Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/safety/evaluate` | Evaluate a proposed action against the safety policy |
| `GET` | `/approvals/{id}` | Check approval status |
| `POST` | `/approvals/{id}/approve` | Approve a pending action |
| `POST` | `/approvals/{id}/reject` | Reject a pending action |

---

## Data Pipeline

### Bronze Layer
Raw and parsed scraped artifacts stored immutably.

- `data/raw/transfermarkt/` — raw HTML/JSON from Transfermarkt scrapes
- `data/raw/fbref/` — raw HTML/JSON from FBref scrapes
- `data/parsed/transfermarkt/*.json` — normalised player profile payloads
- `data/parsed/fbref/*.json` — normalised per-match stat payloads
- `data/bronze/manifest.json` — registry of all ingested artifacts with timestamps

### Silver Layer
Clean, cross-source joined records.

- `players.json` — 18 IDV players with profile data merged from Transfermarkt
- `player_match_stats.json` — 91 match records merged from FBref
- `transfers.json` — 23 transfer events with parsed fees
- `player_per90.json` — per-90-minute rate stats for each player

### Gold Layer
Analytical outputs, one JSON file per model.

| File | Contents |
|---|---|
| `player_features.json` | Aggregated per-player feature vectors |
| `kpi_engine.json` | KPI scores: base_kpi_score, consistency_score, etc. |
| `player_valuation.json` | Valuation scores with component breakdown and future projections |
| `player_similarity.json` | Top-5 similar players per player with distance and comp classification |
| `player_pathway.json` | Trajectory, development stage, success probability, pathway recommendations |
| `advanced_metrics.json` | xG/xA/xT/EPV/OBV per player |
| `club_benchmark.json` | Club development metrics for IDV, Benfica, Ajax, Salzburg |
| `player_risk.json` | Injury availability proxy + discipline risk |
| `transfer_features.json` | Transfer fee features and resale metrics |
| `match_features.json` | Per-match derived features |

---

## Analytics Models

### KPI Engine
Weighted composite of: goals, assists, shots, minutes, yellow/red cards, xG, xA. Produces `base_kpi_score` and `consistency_score`.

### Valuation Model v2
```
score = performance×0.35 + age_curve×0.20 + minutes_probability×0.15
      + league_adjustment×0.15 + club_development×0.10 − risk_discount×0.05
```
- **Age curve**: Gaussian peaked at 25, sigma=5 — younger players near peak age score highest
- **League adjustment**: Premier League=15, La Liga=14, Bundesliga=13, Liga Pro Ecuador=5
- **Club development**: Ajax=95, Benfica=90, Salzburg=88, IDV=75
- **Future projections**: 2-year and 5-year value estimates adjusted by trajectory multiplier

### Similarity Engine v2 (Role-Aware)
Weighted Euclidean distance across 9 normalised features. Feature weights are role-specific:

| Role | Top-weighted features |
|---|---|
| Forward | goal_contribution_per_90 (0.35), shots (0.20), xg_per_90 (0.20) |
| Midfielder | progression_score (0.25), base_kpi_score (0.20), goal_contribution (0.15) |
| Defender | minutes (0.25), consistency_score (0.25), base_kpi_score (0.20) |
| Goalkeeper | minutes (0.35), consistency_score (0.30), base_kpi_score (0.25) |

Trajectory similarity adds a bonus term: same trajectory = 0 penalty, ascending↔stable = 0.15×0.3 penalty, opposing = 0.15×0.7 penalty.

### Pathway Engine
- **Trajectory**: derived from rolling 3-match KPI contribution windows using linear regression slope
- **Development velocity**: improvement rate weighted by age (young players with same rate score higher)
- **Success probability**: `base × trajectory_mult × age_mult × percentile_mult`
- **Pathway recommendations**: based on current club and tier, e.g. IDV → primera liga → eredivisie → bundesliga

### Advanced Metrics v2
Estimated from aggregated stats (no event-level data required):
- **xG** = goals × 0.55 + shots × 0.08 (per total and per 90)
- **xA** = assists × 0.70 + (xG × 0.20) (per total and per 90)
- **EPV per 90** = (goals × 3 + assists × 2 + shots × 0.4) / (minutes / 90)
- **OBV** = goals × 2.5 + assists × 2 + shots × 0.5 + minutes × 0.01
- **Progression score**: 0–10 composite of passing and carry contributions

---

## Multi-Agent System

The platform includes a lightweight multi-agent orchestration layer for complex automated workflows:

| Agent | Responsibility |
|---|---|
| **Orchestrator** | Routes tasks across agents, enforces safety policy |
| **Scraper Agent** | Collects and normalises player data from Transfermarkt + FBref |
| **Data Cleaner Agent** | Builds Bronze, Silver, and Gold artifacts |
| **Analyst Agent** | Runs KPI, risk, similarity, valuation, and advanced metric computations |
| **Report Generator Agent** | Builds operator-facing summaries from Gold artifacts |

### Safety Policy Layer
All destructive or external-facing actions are evaluated before execution:

- **allow** — safe read/analysis operations
- **require_approval** — pipeline writes, data mutations (held in-memory, 15-min TTL)
- **deny** — delete-repo, `rm -rf`, `git clean -fdx`, `curl ... | sh`

---

## Running Locally

### Prerequisites
- Python 3.11+ (3.14 recommended)
- Node.js 20+
- `playwright install` (for live scraping; not required for seeded data)

### Backend setup
```bash
python3.14 -m venv /home/ubuntu/venv
source /home/ubuntu/venv/bin/activate
pip install -r requirements.txt

# Seed IDV player data (18 players, 91 match records)
python scripts/seed_idv_data.py

# Run the full pipeline (generates all Gold artifacts)
python -m app.pipeline.run_pipeline

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 9001
```

### Frontend setup
```bash
cd frontend
npm install
npm run dev      # development server on port 3000
npm run build && npm start   # production build
```

### Environment variables (optional)
```bash
APP_ENV=production
DATABASE_URL=sqlite:///./elitefootball.db
LOG_LEVEL=INFO
LOG_DEBUG_ENABLED=false
LOG_FILE_ENABLED=false
LOG_FILE_PATH=/path/to/scrape.log
SCRAPE_DELAY_SECONDS=2.0
SCRAPE_TIMEOUT_MS=30000
SAFETY_APPROVAL_TTL_SECONDS=900
```

---

## Project Structure

```
elitefootball-agenticAi/
├── app/
│   ├── agents/               # Multi-agent orchestration system
│   │   ├── orchestrator.py
│   │   ├── scraper_agent.py
│   │   ├── analyst_agent.py
│   │   ├── data_cleaner_agent.py
│   │   └── report_generator_agent.py
│   ├── analysis/             # Analytics engine modules
│   │   ├── valuation_v2.py         # Weighted valuation model
│   │   ├── similarity_v2.py        # Role-aware Euclidean similarity
│   │   ├── pathway_engine.py       # Development trajectory + pathway
│   │   ├── advanced_metrics_v2.py  # xG/xA/xT/EPV/OBV
│   │   ├── club_benchmark.py       # Club development benchmarking
│   │   ├── league_adjustment.py    # League coefficient normalisation
│   │   ├── kpi_engine.py           # Base KPI scoring
│   │   └── risk_engine.py          # Injury + discipline risk
│   ├── api/
│   │   ├── routes.py         # FastAPI route handlers
│   │   ├── data_access.py    # Artifact loading + inspection
│   │   ├── schemas.py        # Pydantic response models
│   │   └── safety_routes.py  # Safety evaluation endpoints
│   ├── pipeline/
│   │   ├── run_pipeline.py   # Full pipeline runner
│   │   ├── bronze.py         # Bronze artifact management
│   │   ├── silver.py         # Silver layer builder
│   │   ├── gold.py           # Gold layer orchestrator
│   │   ├── transfers.py      # Transfer data layer
│   │   └── io.py             # JSON read/write utilities
│   ├── scraping/
│   │   ├── transfermarkt.py  # Transfermarkt scraper
│   │   ├── fbref.py          # FBref scraper
│   │   ├── browser.py        # Playwright browser wrapper
│   │   ├── queue.py          # Priority scrape queue with caching
│   │   └── storage.py        # Scrape artifact storage
│   ├── db/                   # SQLAlchemy models + session
│   ├── safety/               # Safety policy engine
│   ├── config.py             # Runtime settings
│   └── main.py               # FastAPI application entry point
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Dashboard
│   │   ├── players/page.tsx      # Player list
│   │   ├── players/[name]/page.tsx  # Player detail
│   │   ├── valuation/page.tsx    # Valuation rankings
│   │   ├── compare/page.tsx      # Similarity search
│   │   ├── pathway/page.tsx      # Career pathways
│   │   ├── benchmark/page.tsx    # Club benchmarking
│   │   ├── admin/page.tsx        # Admin panel
│   │   └── api/[...path]/route.ts  # Backend proxy (no CORS)
│   ├── components/
│   │   ├── Nav.tsx           # Sticky navigation bar
│   │   └── ui.tsx            # Shared UI components
│   └── lib/
│       └── api.ts            # Typed API client
├── data/
│   ├── parsed/               # Normalised scrape payloads (Bronze input)
│   ├── silver/               # Silver layer JSON artifacts
│   └── gold/                 # Gold layer analytical artifacts
├── scripts/
│   └── seed_idv_data.py      # Seeds 18 IDV players + 91 match records
├── tests/                    # Test suite (pytest)
│   ├── test_valuation_v2.py
│   ├── test_similarity_v2.py
│   ├── test_pathway_engine.py
│   ├── test_advanced_metrics_v2.py
│   ├── test_league_adjustment.py
│   ├── test_transfers.py
│   └── test_e2e_full_system.py
├── PROJECT_CONTEXT.md        # Global memory for AI agents
├── requirements.txt          # Python dependencies
└── elitefootball.db          # SQLite persistence store
```

---

## Testing

```bash
# Run all tests
source /home/ubuntu/venv/bin/activate
python -m pytest tests/ -v

# End-to-end validation
python -m unittest tests.test_e2e_full_system
python -m unittest tests.test_e2e_dashboard_flow

# Operator verification scripts
python scripts/verify_full_system_flow.py
python scripts/verify_dashboard_flow.py
```

Test readiness outcomes:
- `READY` — all stages passed
- `READY_WITH_LIMITATIONS` — core pipeline passed; DB or browser deps missing
- `NOT_READY` — a required stage failed

---

## Scraping Architecture

The scraping layer uses **Playwright** (headless Chromium) to scrape:

- **Transfermarkt** — player profiles, positions, nationalities, transfer history, market values
- **FBref** — per-match statistics including goals, assists, shots, minutes, xG, xA

The **priority scrape queue** (`app/scraping/queue.py`) manages jobs with three priority tiers:
- `HIGH (1)` — active squad players, current season
- `MEDIUM (5)` — transfer targets, loan players
- `LOW (10)` — historical / background enrichment

An MD5-keyed JSON cache prevents redundant fetches. The Silver pipeline emits structured logs for every `scrape.start`, `parse.partial_result`, `scrape.empty_result`, and `silver.empty_output` event.

> **Note**: Playwright requires `playwright install` to download browser binaries. The platform functions fully without live scraping using the seeded fixture data in `data/parsed/`.

---

## Structured Logging

All scraping and pipeline stages emit structured JSON-compatible log lines:

```
2026-04-29T09:31:59Z INFO app.pipeline.silver silver.load.complete
    directory=data/parsed/transfermarkt files_discovered=18 payloads_loaded=18
```

| Flag | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Set to `DEBUG` for verbose output |
| `LOG_DEBUG_ENABLED` | `false` | Include extra diagnostic context |
| `LOG_FILE_ENABLED` | `false` | Write logs to a file in addition to stdout |
| `LOG_FILE_PATH` | — | File path when file logging is enabled |

---

## Seeded Data

The repository ships with pre-seeded data for **18 IDV players** including:

Kendry Páez · Moisés Caicedo · Piero Hincapié · Dylan Borrero · Luis Segovia · Alan Minda · Willian Pacho · Óscar Zambrano · Jorge Guagua · Renato Ibarra · Jordy Caicedo · Alexis Zapata · Carlos Gutiérrez · Gabriel Villamil · Michael Espinoza · Sebastián Rodríguez · Tomás Molina · Pedro Velasco

Each player has 4–8 match records across Liga Pro Ecuador and Copa Libertadores. Run `scripts/seed_idv_data.py` to regenerate these fixtures.
