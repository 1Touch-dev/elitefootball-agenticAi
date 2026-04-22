# Safety Policy

## Scope
The PAP-224 safety layer is a lightweight control plane for evaluating actions before execution.

## Decision Types
- `allow` — action may proceed immediately
- `require_approval` — action is not blocked, but must be explicitly approved first
- `deny` — action is blocked and must not execute

## MVP Rules
### Hard deny
- repo deletion operations (`delete_repo`, `destroy_repo`, etc.)
- destructive shell commands that target the repo root
- `rm -rf .`
- `git clean -fdx`
- remote fetch-and-execute shell patterns like `curl ... | sh`
- mutation of `.git/` via shell commands

### Approval required
- mutating shell commands that are not explicitly catastrophic
- compound shell commands with mutation
- rewrite-style git commands such as `git reset --hard` and `git checkout -- ...`

### Allow
- read-only shell commands
- ordinary API requests
- current safe orchestrator task kinds

## Approval Store
The MVP uses an in-memory approval store. Approvals are bound to a normalized action fingerprint and are intended to be short-lived/single-use.
