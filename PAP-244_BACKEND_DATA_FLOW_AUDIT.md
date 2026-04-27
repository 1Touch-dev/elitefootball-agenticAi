# PAP-244 Backend Data Flow Audit

## Root Cause Found
The dashboard is API-backed and the endpoint shapes are broadly correct. The immediate no-data symptom is primarily caused by empty or unavailable Silver/Gold artifacts, not by the dashboard bypassing the backend or expecting a different payload structure.

## What Was Audited
- dashboard data source in `dashboard/api_client.py`
- backend endpoints in `app/api/routes.py`
- artifact-backed query layer in `app/api/data_access.py`
- current checked-in Silver/Gold artifact state under `data/`

## What Was Implemented

### Dashboard status endpoint
Added:
- `GET /dashboard/status`

This endpoint reports:
- top-level status (`ready`, `partial`, `empty`, `artifact_missing`, `artifact_invalid`)
- per-artifact state
- row counts
- sample rows
- validation errors

### Artifact validation improvements
Added artifact inspection logic so the backend now distinguishes:
- missing artifact
- empty artifact
- invalid artifact payload
- ready artifact with usable rows

### Error handling improvements
Existing data endpoints now:
- return `503` for missing required artifacts
- return `500` for invalid artifact payloads instead of quietly degrading to empty data

## Sample Working Response Payload

### `GET /dashboard/status`
```json
{
  "status": "empty",
  "artifacts": {
    "players": {
      "path": "data/silver/players.json",
      "exists": true,
      "required": true,
      "valid": true,
      "state": "empty",
      "row_count": 0,
      "error": null
    }
  },
  "samples": {
    "players": []
  }
}
```

### `GET /players`
```json
{
  "count": 1,
  "items": [
    {
      "player_name": "Patrik Mercado",
      "preferred_name": "Patrik Mercado",
      "position": "Attacking Midfield",
      "current_club": "Independiente del Valle",
      "nationality": "Ecuador",
      "date_of_birth": "2003-01-01",
      "features": {"matches": 20, "goal_contribution_per_90": 0.82},
      "kpi": {"base_kpi_score": 68.4, "consistency_score": 72.1},
      "valuation": {"valuation_score": 71.2, "valuation_tier": "strong_mvp", "model_version": "mvp_v1"}
    }
  ]
}
```

## Files Changed
- `app/api/data_access.py`
- `app/api/routes.py`
- `tests/test_api_routes.py`
- `tests/test_data_access.py`

## Next Recommended Issue
PAP-245 - surface dashboard status inside the UI and optionally show a friendly explanation when artifacts are empty, missing, or invalid.
