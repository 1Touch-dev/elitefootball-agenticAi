# ARCHITECT_PLAN_PAP-224 — Implement Safety + Policy Layer

## Ticket
PAP-224

## Role
Architect — planning/design only. No application code implemented in this phase.

## Goal
Add a safety + policy layer that can:
- block destructive repo actions such as delete-repo style requests
- block unsafe command execution requests
- support an approval flow for actions that are sensitive but not outright forbidden

The implementation must preserve the current repository architecture, remain lightweight, and sit cleanly between request intake and action execution.

---

## 1) Current System State

### What is actually present in this checkout
This repo currently contains:
- a FastAPI app with read-oriented endpoints in `app/api/routes.py`
- an in-process orchestrator in `app/agents/orchestrator.py`
- agent wrappers in `app/agents/`
- pipeline and analysis modules under `app/pipeline/` and `app/analysis/`
- no current command-execution API
- no current repo-deletion API
- no current approval system
- no `app/tasks/` or `app/api/task_routes.py` in this checkout

### Important repo-state note
Memory files mention PAP-223 queue infrastructure, but this working tree does not contain those files. Planning for PAP-224 should therefore target the **actual current codebase** and leave extension seams for later async/task work instead of assuming queue endpoints already exist.

### Existing architecture boundaries to preserve
The current architecture is already sensibly separated:
- `app/api/` handles HTTP surface
- `app/agents/` handles orchestration and task routing
- `app/scraping/`, `app/pipeline/`, and `app/analysis/` own domain work
- `memory/` stores continuity and operating notes

The safety layer should become a cross-cutting control plane, not a place where business logic gets duplicated.

---

## 2) Problem Framing

The ticket description is intentionally narrow:
- block delete repo
- block unsafe commands
- approval flow

That suggests three policy outcomes are needed:
1. **allow** — safe request can proceed immediately
2. **require approval** — potentially dangerous but not categorically forbidden
3. **deny** — destructive or explicitly forbidden action must not execute

### Examples implied by the ticket
#### Must deny
- delete the repository
- remove the repo contents
- destructive shell patterns aimed at repo loss
- requests that combine repo deletion with forced cleanup

#### Should require approval
- commands that mutate many files
- commands that invoke package installers, environment changes, or shell scripts with broad side effects
- high-risk git operations that rewrite history or discard work

#### Can allow
- read-only operations
- normal analysis/pipeline execution
- ordinary API summary/status calls
- safe internal orchestration that does not invoke dangerous shell behavior

---

## 3) Design Decision

### Decision summary
Implement PAP-224 as a **small policy engine plus approval-state service** under a new `app/safety/` package, with thin integration points in the API/orchestrator layers.

### Why this is the right fit
This design:
- preserves current module boundaries
- avoids hard-coding safety checks across route handlers and agents
- creates a reusable seam for future command/task endpoints
- supports both immediate denial and approval-based gating
- keeps policy behavior testable without needing real shell execution

### Explicit non-goals for PAP-224
Do **not** in this ticket:
- build a full authn/authz user system
- add a distributed approval workflow or email/chat approval service
- introduce external policy engines or SaaS dependencies
- implement real command execution if the repo does not already have it
- add background queue infrastructure just for approvals

---

## 4) Proposed Architecture

## 4.1 New package: `app/safety/`
Create a focused package for safety and policy concerns.

### Proposed files
1. `app/safety/types.py`
   - typed models / dataclasses / enums for policy evaluation
   - recommended types:
     - `PolicyDecision` (`allow`, `require_approval`, `deny`)
     - `ActionKind` (`repo_operation`, `shell_command`, `agent_task`, `api_request`)
     - `SafetyEvaluation`
     - `ApprovalRequestRecord`

2. `app/safety/policies.py`
   - pure policy rules
   - string/pattern checks for dangerous requests
   - helpers for evaluating repo-deletion intent and unsafe shell patterns

3. `app/safety/service.py`
   - orchestration layer around policy evaluation
   - public entrypoints such as:
     - `evaluate_action(...)`
     - `assert_allowed(...)`
     - `create_approval_request(...)`
     - `approve_request(...)`
     - `reject_request(...)`
     - `resolve_approval(...)`

4. `app/safety/store.py`
   - lightweight in-memory approval state for the MVP
   - optional TTL or timestamp metadata
   - isolated so future persistence can replace it cleanly

5. `app/safety/schemas.py`
   - if HTTP approval endpoints are added, hold FastAPI request/response schemas here

6. `app/safety/__init__.py`
   - exports the public safety surface

---

## 4.2 Policy evaluation model
Every candidate action should be normalized into a common structure before execution:
- `action_kind`
- `action_name`
- `command` or `operation`
- `target_path` or `resource`
- `requested_by`
- `metadata`

The safety service returns a structured evaluation:
- `decision`: allow / require_approval / deny
- `reason_code`
- `message`
- `matched_rules`
- `approval_id` when applicable

This is better than ad hoc booleans because API and orchestrator callers can respond consistently.

---

## 5) Policy Rules

## 5.1 Hard deny rules
These should block immediately with no approval path.

### Repository deletion / destruction
Deny requests that clearly attempt to remove the repo or its contents, such as:
- `rm -rf .`
- `rm -rf /tmp/zero-human-sandbox`
- `git clean -fdx` when aimed at wiping the working tree
- explicit operation names like `delete_repo`, `remove_repository`, `destroy_repo`
- path-targeted recursive deletion of the repo root

### Unsafe command categories
Deny commands that are plainly too dangerous for this project’s needs, especially if they:
- recursively delete the repository or parent directories
- fetch and execute remote scripts directly
- chain destructive shell operators with force flags
- overwrite critical git metadata in `.git/`

### Why hard deny matters
Approval should not be used to bless clearly catastrophic actions. The system needs a category that simply says “no”.

## 5.2 Approval-required rules
Require explicit approval for actions that might be legitimate but carry meaningful risk.

Examples:
- `git reset --hard`
- `git checkout -- .`
- broad file deletions outside trash-safe patterns
- commands containing shell metacharacter chains (`&&`, `||`, `;`, pipes) when combined with mutation
- install/update commands that change the runtime substantially
- future command/task endpoints that execute arbitrary shell input

## 5.3 Allow rules
Allow by default only when the action is clearly in a safe class:
- read-only API calls
- orchestrator tasks that do not map to dangerous shell execution
- deterministic data/pipeline/analysis functions already inside the codebase

### Default posture
For arbitrary shell commands, the default should lean conservative:
- known-safe read-only commands can be allowed
- ambiguous or mutating commands should require approval
- explicitly destructive commands should be denied

---

## 6) Approval Flow Design

## 6.1 MVP approval mechanics
Use an in-memory approval registry for the MVP.

Each approval record should include:
- `approval_id`
- `status` (`pending`, `approved`, `rejected`, `expired`)
- normalized action payload
- decision rationale
- creation timestamp
- optional expiry timestamp
- optional approver identity / note

### Why in-memory first
This repo does not yet need durable workflow infrastructure. An isolated store keeps the implementation small and easy to replace later.

## 6.2 Approval lifecycle
1. caller submits an action
2. safety service evaluates it
3. if `allow` → continue immediately
4. if `deny` → return structured error/denial response
5. if `require_approval` → create pending approval record and return it
6. caller later submits approval decision
7. action may be re-attempted or resumed using the approval record

## 6.3 Token model
Do not use vague “approved once forever” semantics.

Recommended MVP behavior:
- approvals are bound to a single normalized action payload
- approvals are single-use or short-lived
- approval records become invalid if the action materially changes

That prevents approving one thing and executing another.

---

## 7) Integration Plan

## 7.1 Orchestrator integration
Add an optional safety check before task execution in `app/agents/orchestrator.py`.

### Intended behavior
- safe internal tasks like `run_analysis` continue normally
- future task kinds that imply destructive repo or shell behavior are evaluated first
- orchestrator remains responsible for routing, not policy logic itself

### Recommended pattern
The orchestrator should call a safety service method, not embed keyword matching inline.

## 7.2 API integration
There are two reasonable integration points.

### Option A — immediate foundation only
Add safety-aware service hooks but do not expose approval endpoints until a command/task mutation route exists.

### Option B — include approval endpoints now
Add a small router such as `app/api/safety_routes.py` with endpoints like:
- `POST /approvals`
- `POST /approvals/{approval_id}/approve`
- `POST /approvals/{approval_id}/reject`
- `GET /approvals/{approval_id}`

### Recommendation
Use **Option B** if PAP-224 is expected to deliver a visible approval flow now. Use **Option A** only if the product owner wants safety internals first and HTTP exposure later.

Given the ticket explicitly says “approval flow,” I recommend **Option B** so the flow is testable and real.

## 7.3 Future command/task endpoint compatibility
Even though this checkout has no command execution API, the safety layer should be designed so future endpoints can do:
1. normalize request
2. evaluate policy
3. either deny, require approval, or execute

This is the real architectural win of PAP-224.

---

## 8) Proposed File-Level Changes

### New files
1. `app/safety/types.py`
2. `app/safety/policies.py`
3. `app/safety/service.py`
4. `app/safety/store.py`
5. `app/safety/schemas.py` (if HTTP flow is included)
6. `app/api/safety_routes.py` (recommended)
7. `tests/test_safety_policies.py`
8. `tests/test_safety_service.py`
9. `tests/test_safety_routes.py` (if HTTP flow is included)
10. `memory/safety_policy.md`

### Existing files to update
1. `app/main.py`
   - include the safety router if approval endpoints are added

2. `app/api/routes.py`
   - optionally expose safety capability summary in `/summary`
   - do not mix approval logic directly into existing read endpoints

3. `app/agents/orchestrator.py`
   - add safety preflight hook for relevant task execution entrypoints
   - keep routing separate from policy logic

4. `app/config.py`
   - add lightweight settings for approval expiry / safety mode if needed
   - keep config minimal

5. `README.md`
   - document what is blocked vs approval-gated
   - document how approval requests work in the MVP

---

## 9) API and Error Semantics

## 9.1 Denied action response
For denied actions, return a structured error payload with fields like:
- `status`: `denied`
- `reason_code`
- `message`
- `matched_rules`

Recommended status code:
- `403` for forbidden/denied actions

## 9.2 Approval-required response
For approval-gated actions, return a structured payload such as:
- `status`: `approval_required`
- `approval_id`
- `message`
- `expires_at`
- normalized action summary

Recommended status code:
- `202` or `409`

I recommend `202 Accepted` for “request accepted but pending approval”.

## 9.3 Approved execution response
Once approved, the actual action endpoint can execute and return its normal success payload. Approval endpoints themselves should return a simple state transition payload.

---

## 10) Testing Plan

## Unit tests for pure policy rules
Add coverage for:
- explicit repo delete commands are denied
- destructive shell patterns are denied
- ambiguous mutating commands require approval
- clearly safe read-only commands are allowed
- path-based repo root deletion detection works

## Service tests
Add coverage for:
- pending approval record creation
- approval resolution by id
- rejection flow
- expired approval handling
- mismatched action payload cannot reuse an approval

## API tests
If approval routes are included, test:
- create approval request
- approve pending request
- reject pending request
- fetch approval status
- denied actions return structured forbidden response

## Regression tests
Ensure:
- existing `/health`, `/summary`, `/players`, `/compare`, `/value` continue to work
- orchestrator behavior is unchanged for safe task kinds
- no test requires real shell execution or external services

---

## 11) Implementation Sequence for Grunt

1. Add `app/safety/types.py` with shared decision/result models
2. Add `app/safety/policies.py` with pure deny/approval/allow classification helpers
3. Add `app/safety/store.py` with in-memory approval registry
4. Add `app/safety/service.py` as the single public evaluation/orchestration layer
5. Add `app/api/safety_routes.py` and schemas if approval flow is exposed over HTTP
6. Wire the router into `app/main.py`
7. Add optional safety preflight integration in `app/agents/orchestrator.py`
8. Update `app/api/routes.py` summary metadata only if useful
9. Add memory docs at `memory/safety_policy.md`
10. Add focused tests for policy/service/routes
11. Update README with safety and approval behavior

---

## 12) Acceptance Criteria

PAP-224 should be considered complete when:
- there is a dedicated safety/policy layer under `app/safety/`
- delete-repo style actions are explicitly denied
- unsafe command patterns are either denied or approval-gated according to rule severity
- there is a working approval flow with inspectable state
- existing architecture remains intact and business logic is not duplicated into the safety layer
- tests cover deny, approval-required, approval resolution, and safe-pass cases
- existing read-only API behavior remains stable

---

## 13) Risks and Design Notes

### Risk: overfitting command matching
If policy rules are too naive, they will be bypassable or noisy.

### Mitigation
Keep the MVP rules explicit and conservative:
- normalize commands before checks
- match both operation names and shell patterns
- focus first on the destructive cases named in the ticket

### Risk: stale approval reused for different action
### Mitigation
Bind approvals to a normalized action fingerprint and make them short-lived/single-use.

### Risk: mixing policy with transport logic
### Mitigation
Keep policy in `app/safety/` and let API/orchestrator call into it.

---

## 14) Suggested Handoff Summary

PAP-224 should be implemented as a lightweight safety control plane, not as scattered inline checks. The right shape for this repo is:
- a new `app/safety/` package
- explicit allow / require-approval / deny decisions
- hard deny for repo deletion and plainly unsafe commands
- in-memory approval registry for MVP flow
- thin integration in API and orchestrator layers
- focused tests for rule evaluation and approval lifecycle

One important caveat: this checkout does **not** currently contain the PAP-223 task queue files mentioned in memory. Grunt should implement PAP-224 against the actual present codebase and only leave clean extension points for future async/task integration.