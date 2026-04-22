# ARCHITECT PLAN — PAP-207

## Ticket
Initialize repo + setup memory system + base architecture.

## Requested Outcomes
Set up:
- project structure
- Python backend
- scraping module
- database
- memory system

Must create during implementation:
- `/memory/project_context.md`
- `/memory/architecture.md`
- `/memory/progress.md`
- `/memory/decisions.md`

Must include initial content covering:
- project goal
- system design (multi-agent)
- MVP scope (IDV players)

Critical rule to embed in memory:
- All future tasks MUST read memory before work
- All future tasks MUST update memory after work

---

## Current Repository State
Observed repo contents are minimal:
- `README.md`
- prior ticket handoff artifacts for PAP-206
- no Python package structure yet
- no backend code
- no scraper module
- no database layer
- no memory directory

Implication:
This ticket should be treated as an **initial foundation ticket**. The next role should create a clean project skeleton rather than attempting feature-complete implementation.

---

## High-Level Recommendation
Implement this as a small but opinionated Python project bootstrap with a first-class memory system.

### Primary objective
Create a repo shape that makes future work predictable.

### Secondary objective
Establish the memory system as a mandatory operating rule for all future tasks.

Because the repository is currently nearly empty, the most important deliverable is **clear structure plus high-signal starter documents**.

---

## Recommended Repository Structure
Grunt should create a minimal structure like this:

```text
/tmp/zero-human-sandbox/
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   ├── scraping/
│   │   ├── __init__.py
│   │   └── players.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── models.py
│   └── services/
│       ├── __init__.py
│       └── memory_service.py
├── memory/
│   ├── project_context.md
│   ├── architecture.md
│   ├── progress.md
│   └── decisions.md
├── tests/
│   └── __init__.py
├── requirements.txt
└── .gitignore
```

This is intentionally modest. It creates clear boundaries without overcommitting to a framework-heavy stack.

---

## Recommended Technical Direction

### 1) Python backend
Use a lightweight backend entrypoint.

Recommended implementation approach:
- create a simple app bootstrap in `app/main.py`
- if Grunt wants to keep things maximally safe, even a minimal placeholder backend is acceptable
- avoid overengineering the API at this stage

Recommended backend role:
- future API/service entrypoint
- coordination layer for scraping, storage, and memory-aware agent workflows

### 2) Scraping module
Create a dedicated scraping package.

Recommended first file:
- `app/scraping/players.py`

Responsibilities:
- placeholder interfaces for fetching/scanning player data
- clear naming around the MVP target: **IDV players**

Do not overbuild scraping logic yet; define the module boundary and a simple starter function/class instead.

### 3) Database layer
Create a lightweight database abstraction package.

Recommended starter files:
- `app/db/base.py`
- `app/db/models.py`

Purpose:
- establish where models and session/connection code will live
- enable future persistence for scraped entities and agent memory references

Implementation guidance:
- a simple SQLite-oriented starting point is sufficient for bootstrap work
- prefer clarity over premature ORM complexity

### 4) Memory system
This is the most important deliverable.

The next role must create the `memory/` directory and the four required markdown files.

The memory system should be treated as operational infrastructure, not optional documentation.

---

## Required Memory File Content Plan

### `/memory/project_context.md`
Should answer:
- what the project is
- what problem it solves
- who it serves
- what the MVP focuses on

Required initial topics:
- project goal
- MVP scope focused on IDV players
- broad product framing

### `/memory/architecture.md`
Should answer:
- how the system is organized
- what the backend, scraping, DB, and agents do
- how multi-agent responsibilities are divided

Required initial topics:
- system design (multi-agent)
- base backend architecture
- scraping flow
- persistence role

### `/memory/progress.md`
Should answer:
- what has been completed so far
- what is scaffolded
- what is intentionally deferred

Required initial topics:
- repo initialization status
- base architecture setup status
- remaining next steps

### `/memory/decisions.md`
Should capture:
- initial technical decisions
- rationale for those decisions
- operational rules for future tasks

This file must include the critical rule:

> All future tasks MUST read memory before work.
>
> All future tasks MUST update memory after work.

It should also record decisions such as:
- Python chosen for backend foundation
- scraping isolated into its own module
- DB layer created early for future persistence
- memory treated as a mandatory workflow artifact

---

## Multi-Agent System Design Recommendation
The ticket explicitly asks for system design (multi-agent). The memory files should define this at a practical level.

Recommended starter agent model:
- **Coordinator Agent**
  - decides what task to run next
  - routes work to specialized modules
- **Scraper Agent**
  - gathers player data
  - normalizes inputs before persistence
- **Memory Agent**
  - reads project memory before tasks
  - updates memory after tasks
- **Analysis Agent**
  - interprets scraped data and surfaces useful outputs

This should be documented as conceptual architecture rather than fully implemented autonomous agents at this stage.

---

## MVP Scope Recommendation
The memory documents should define MVP scope narrowly.

Recommended MVP framing:
- focus on **IDV players** only
- support collecting and storing core player data
- support a future workflow where agents can scrape, persist, and summarize data

Suggested MVP data categories:
- player name
- position
- team association/context
- basic profile metadata
- source/provenance

Avoid broadening MVP to multiple clubs, full analytics pipelines, or advanced dashboards in this ticket.

---

## Implementation Boundaries for Grunt
Grunt should:
- create the directory structure
- create placeholder Python modules
- create required memory files with meaningful initial content
- add minimal project bootstrap files like `requirements.txt` and `.gitignore`
- keep code safe, minimal, and easy to extend

Grunt should not:
- implement full scraping logic
- build a full production API
- build advanced DB migrations
- create large speculative subsystems
- skip memory initialization

---

## Suggested File-Level Responsibilities

### `README.md`
Optional to expand if helpful, but not required by this ticket unless needed to explain startup.

### `app/main.py`
- backend bootstrap / application entrypoint
- simple starter app or placeholder

### `app/config.py`
- central location for future settings

### `app/api/routes.py`
- starter route definitions or placeholders

### `app/agents/orchestrator.py`
- conceptual coordination layer for multi-agent workflows

### `app/scraping/players.py`
- starter scraping interfaces focused on IDV players

### `app/db/base.py`
- DB connection/session placeholder or base setup

### `app/db/models.py`
- starter data models or schema placeholders

### `app/services/memory_service.py`
- helper logic or documented hooks for reading/updating memory files

---

## Risks / Watchouts
- creating too much framework code for an initialization ticket
- under-delivering on memory content quality
- forgetting the required operational memory rule
- choosing a structure that is unclear or too clever
- allowing scraping/database placeholders to look "finished" when they are only scaffolds

---

## QA Checklist for Pedant
Pedant should verify:
- required `memory/` directory exists
- all four required memory markdown files exist
- each memory file contains meaningful initial content
- memory includes the mandatory future-task rule
- Python backend structure exists
- scraping module exists
- database module exists
- project skeleton is coherent and minimal
- no unnecessary complexity was introduced

---

## Files Expected to Change in Grunt Phase
Expected new files/directories include at least:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`
- Python backend skeleton files
- scraping module files
- database files
- support files such as `.gitignore` and `requirements.txt`

---

## Artifact for Next Role
Grunt should bootstrap a minimal Python project with backend, scraping, DB, and mandatory memory infrastructure, with the memory system treated as a first-class operational requirement and seeded with project goal, multi-agent design, MVP scope for IDV players, and the mandatory memory-read/memory-update rule.
