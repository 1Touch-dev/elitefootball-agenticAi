# elitefootball-agenticAi ⚽🧠

An elite, production-grade **AI Recruitment & Football Intelligence Platform** designed for professional clubs. This system transforms multi-source scouting data into acquisition decisions through a high-fidelity data pipeline and decision-first scout interface.

---

## 🚀 Overview: Implementation Status

| Feature | Status | Description |
| :--- | :--- | :--- |
| **Shortlist Engine** | ✅ **Implemented** | Real-world algorithmic ranking (Performance + Value + Probability). |
| **Decision Engine** | ✅ **Implemented** | Robust BUY/HOLD/SELL logic with weighted risk/return factors. |
| **Club Fit (DNA)** | ✅ **Implemented** | Deep tactical profiling against 15+ elite club archetypes. |
| **Form Trends** | ✅ **Implemented** | Temporal "Last 5 vs Season" minutes and output trajectory. |
| **Multi-Source Scraping** | ✅ **Implemented** | Real-time extraction from Transfermarkt, FBref, and Sofascore. |
| **Video Integration** | 🟡 **Structural** | Automated YouTube scouting searches and event-linked clip metadata. |
| **Reports** | 🟡 **Partial** | Automated summaries and decisions; strengths/risks use template logic. |

---

## 🧠 Core Recruitment Workflow

### 1. Discovery (Shortlist Engine)
Rank players across global leagues based on the **Transfer Efficiency Formula**:
`Score = (Perf_Percentile * 0.4) + (Value_Gap * 0.3) + (Transfer_Prob * 0.3)`
*   **Performance**: Derived from 50+ match metrics via FBref and Sofascore.
*   **Undervaluation**: Automated gap analysis between Transfermarkt MV and our AI Computed Value.
*   **Probability**: Predictive model for transfer likelihood in the next 12 months.

### 2. Intelligence (Player Profiling)
*   **Decision Engine**: Deep-dive into technical KPIs and algorithmic BUY/HOLD/SELL recommendations.
*   **Form Analytics**: Temporal trend detection (Form Spike vs Declining Trajectory).
*   **Risk Engine**: 0–100 risk score based on availability, discipline, and age curve.

### 3. Validation (Scouting Clips)
*   **Visual Highlights**: Automated highlights search for visual verification.
*   **Event Metadata**: Structured event clip anchoring (Shots, Key Passes, Duels) tied to Sofascore event IDs and timestamps for precision video review.

### 4. Decision (Club Fit & Reports)
*   **Tactical DNA Matching**: Score players against specific club profiles (e.g., Brighton's data-led model, Ajax's technical youth model).
*   **Recruitment Reports**: Automated scouting reports synthesizing performance, valuation, and tactical fit.

---

## 🏗️ Data Architecture

### 📥 Real-World Scraping Only
No synthetic data. We bypass anti-bot measures using:
*   **Transfermarkt**: Playwright/Requests for bio and valuation history.
*   **FBref**: Playwright/Apify for advanced advanced match statistics (xG, xA, Progressions).
*   **Sofascore**: Direct API Extraction for granular event stats and heatmaps.

### 📂 Medallion Pipeline
*   **Bronze**: Immutable raw responses and normalized parsed payloads.
*   **Silver**: Cleaned, cross-source joined player and match records.
*   **Gold**: Analytical artifacts (KPIs, Valuation v2, Club Fit, Decisions).

---

## 🛠️ Tech Stack

*   **Backend**: Python 3.14, FastAPI, Playwright, Scikit-learn (Logistic Regression, Gaussian Scaling).
*   **Frontend**: Next.js 16, Tailwind CSS (Elite Dark Theme), Recharts (Performance Radars).
*   **Pipeline**: Custom Medallion architecture with deterministic incremental updates.

---

## 📡 API Reference

| Endpoint | Method | Status |
| :--- | :--- | :--- |
| `/api/shortlist` | `POST` | **Full** | Ranking Engine. |
| `/api/player/{slug}` | `GET` | **Full** | Bio, Trends, and Video/Event structures. |
| `/api/player/{slug}/decision`| `GET` | **Full** | BUY/HOLD/SELL reasoning. |
| `/api/compare` | `POST` | **Full** | Head-to-head radar comparisons. |
| `/api/alerts` | `GET` | **Full** | Breakout & Undervalued triggers. |
| `/api/club-fit` | `POST` | **Full** | Tactical DNA matching. |

---
*Honest, production-ready engineering for the next generation of football recruitment.*
