# PEDANT HANDOFF — PAP-245

## Review Targets
Please verify both backend readiness support and UI correctness.

## Root Cause Confirmed
- current dashboard artifacts are genuinely empty in this checkout
- the dashboard previously treated readiness too shallowly and did not cleanly separate empty vs fetch failure
- the Compare page previously risked dropping `distance` / `similarity_score` when valuation enrichment existed

## Implementation Summary
### Backend
- added artifact inspection and `ArtifactInvalidError` in `app/api/data_access.py`
- added `GET /dashboard/status` in `app/api/routes.py`
- required missing artifacts now surface as 503; invalid artifacts as 500

### Dashboard
- Home now uses dashboard status, not just `/health`
- Player page uses explicit loading, empty, and section-level stats error messaging
- Compare page keeps player summary visible if compare fetch fails
- similarity rows are now merged with valuation fields instead of replaced

## Things To Check Closely
1. **Status classification**
   - `empty` vs `partial` vs `artifact_missing` vs `artifact_invalid`
2. **Compare enrichment correctness**
   - `distance` and `similarity_score` must remain present after valuation enrichment
3. **Partial rendering behavior**
   - Player page should still render profile/cards even if stats fail
   - Compare page should still render selected-player summary even if compare fails
4. **No architecture breakage**
   - dashboard must remain API-first with no raw artifact reads
5. **Optional artifact semantics**
   - confirm `player_features` and `kpi` being optional does not incorrectly downgrade overall readiness

## Verification Already Run
- `python3 -m unittest tests.test_data_access tests.test_dashboard_api_client` ✅
- `python3 -m unittest tests.test_api_routes` ✅ skipped in this sandbox because FastAPI is unavailable
- `python3 -m py_compile ...` ✅
- live `inspect_dashboard_artifacts()` check shows `status: "empty"`

## Recommended Pedant Additions If Needed
- tighten helper wording if the status messages feel too repetitive
- add more focused tests if you spot edge cases around partial artifacts or compare-row merge behavior

## Next Recommended Issue
PAP-246 - dashboard smoke or screenshot-based verification against a seeded non-empty backend.
