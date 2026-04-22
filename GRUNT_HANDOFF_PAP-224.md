# GRUNT_HANDOFF_PAP-224

## Ticket
PAP-224 — Implement Safety + Policy Layer

## What was implemented
A lightweight safety control layer is now in place with explicit allow / require-approval / deny decisions.

### New package
- `app/safety/__init__.py`
- `app/safety/types.py`
- `app/safety/policies.py`
- `app/safety/store.py`
- `app/safety/service.py`
- `app/safety/schemas.py`

### New API surface
- `app/api/safety_routes.py`
  - `POST /safety/evaluate`
  - `GET /approvals/{approval_id}`
  - `POST /approvals/{approval_id}/approve`
  - `POST /approvals/{approval_id}/reject`

### Integration changes
- `app/main.py`
  - safety router is registered
- `app/api/routes.py`
  - `/summary` now exposes safety capabilities
- `app/agents/orchestrator.py`
  - task execution now runs through a safety preflight
- `app/config.py`
  - added `repo_root`
  - added `safety_approval_ttl_seconds`
- `README.md`
  - documented the safety/approval layer
- `memory/safety_policy.md`
  - added policy notes

## Policy behavior implemented
### Hard deny
- explicit repo-delete style operations
- destructive shell commands targeting the repo
- `rm -rf .`
- `rm -rf /tmp/zero-human-sandbox`
- `git clean -fdx`
- `.git` mutation via shell commands
- `curl ... | sh` / `wget ... | bash` style remote script execution

### Require approval
- mutating shell commands
- history/workspace rewrite commands (`git reset --hard`, `git checkout -- ...`)
- compound mutating shell commands

### Allow
- read-only shell commands
- existing orchestrator task kinds
- ordinary safe actions

## Approval model
- in-memory approval store
- approval records include fingerprint, timestamps, status, approver, and note
- approvals are bound to action fingerprints
- approved records can be consumed through `resolve_approval(...)`

## Stability fixes made while implementing
The current tree already contained partial PAP-223 queue files with a few broken seams. I applied minimal fixes so the repo remains internally coherent:
- `app/agents/orchestrator.py` now exposes `run_task_dict(...)`
- `app/tasks/jobs.py` now defines `TASK_NAME`
- `app/tasks/celery_app.py` now degrades gracefully when Celery is not installed
- `app/tasks/schemas.py` now includes `metadata` and safe default factories
- `tests/test_tasks.py` now skips cleanly when FastAPI is unavailable and uses `/api/tasks`

## Tests added
- `tests/test_safety_policies.py`
- `tests/test_safety_service.py`
- `tests/test_safety_routes.py`

## Validation run
- `python3 -m unittest discover -s tests` ✅

## Pedant review focus
1. **Rule accuracy**
   - confirm hard-deny vs approval-required boundaries are sensible and not too broad
2. **Approval semantics**
   - confirm fingerprint matching / consume behavior is correct and not reusable in unsafe ways
3. **Timezone correctness**
   - approval timestamps now use timezone-aware UTC datetimes; confirm response handling is clean
4. **API semantics**
   - confirm `POST /safety/evaluate` returning 403 for deny and 200 for approval-required is acceptable for MVP
5. **PAP-223 incidental fixes**
   - ensure the queue-related cleanup did not introduce regressions outside PAP-224 scope
