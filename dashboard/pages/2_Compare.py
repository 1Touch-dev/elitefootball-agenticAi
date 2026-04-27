from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import build_dashboard_state, enrich_similarity_rows, explain_compare_issue, explain_players_empty, placeholder_message_lines


st.set_page_config(page_title="Compare Players", layout="wide")
st.title("Compare")

client = DashboardAPIClient()
status_payload = None
player_payload = {"items": []}
backend_error = None

try:
    with st.spinner("Loading comparison data..."):
        status_payload = client.get_dashboard_status()
        player_payload = client.get_players(limit=200)
except DashboardAPIError as exc:
    backend_error = str(exc)

state = build_dashboard_state(status_payload, backend_error=backend_error)
if state["level"] == "warning":
    st.warning(f"{state['title']}: {state['message']}")
elif state["level"] == "info":
    st.info(f"{state['title']}: {state['message']}")
elif state["level"] == "error":
    st.error(f"{state['title']}: {state['message']}")
else:
    st.success(f"{state['title']}: {state['message']}")

for line in placeholder_message_lines(state)[1:]:
    st.caption(line)

if st.button("Retry comparison data", key="retry-compare-page"):
    st.rerun()

players = player_payload.get("items", []) if isinstance(player_payload, dict) else []
if not players:
    empty_state = build_dashboard_state(status_payload, no_records_label="players")
    st.info(explain_players_empty(status_payload))
    for line in placeholder_message_lines(empty_state)[1:]:
        st.caption(line)
    st.stop()

player_names = [row.get("player_name", "unknown-player") for row in players]
selected_player = st.selectbox("Choose a player to compare", player_names, index=0)
limit = st.slider("Similar players to show", min_value=1, max_value=10, value=5)

selected_row = next((row for row in players if row.get("player_name") == selected_player), players[0])
selected_valuation = selected_row.get("valuation") or {}

summary_col, value_col = st.columns(2)
with summary_col:
    st.subheader(selected_player)
    st.write(f"**Position:** {selected_row.get('position') or '—'}")
    st.write(f"**Club:** {selected_row.get('current_club') or '—'}")
with value_col:
    st.subheader("Valuation snapshot")
    if selected_valuation:
        st.metric("Score", selected_valuation.get("valuation_score", "—"))
        st.write(f"**Tier:** {selected_valuation.get('valuation_tier') or '—'}")
    else:
        st.info("No valuation data is available for the selected player.")
        if state.get("last_sync"):
            st.caption(f"Last successful sync: {state['last_sync']}")

st.divider()

compare_payload = None
compare_error = None
try:
    with st.spinner("Loading comparison results..."):
        compare_payload = client.get_compare(selected_player, limit=limit)
except DashboardAPIError as exc:
    compare_error = exc

st.subheader("Comparison features")
if compare_payload is None:
    error_state = build_dashboard_state(status_payload, backend_error=str(compare_error) if compare_error else None)
    st.warning(explain_compare_issue(status_payload))
    for line in placeholder_message_lines(error_state):
        st.caption(line)
else:
    comparison_features = compare_payload.get("comparison_features") or {}
    if comparison_features:
        st.json(comparison_features)
    else:
        no_features_state = build_dashboard_state(status_payload, no_records_label="comparison feature rows")
        st.info("No comparison features are available yet.")
        for line in placeholder_message_lines(no_features_state)[1:]:
            st.caption(line)

st.subheader("Similar players")
if compare_payload is None:
    st.info("Player summary is still available above even though comparison results could not be loaded.")
else:
    similar_rows = compare_payload.get("similar_players") or []
    if not similar_rows:
        no_records_state = build_dashboard_state(status_payload, no_records_label="similar players")
        st.info(explain_compare_issue(status_payload))
        for line in placeholder_message_lines(no_records_state)[1:]:
            st.caption(line)
    else:
        try:
            valuation_lookup_payload = client.get_value(limit=200)
            valuation_lookup = {
                row.get("player_name"): row
                for row in valuation_lookup_payload.get("items", [])
                if isinstance(row, dict)
            }
            if not valuation_lookup:
                st.warning("Similarity rows loaded, but valuation enrichment is unavailable right now.")
        except DashboardAPIError as exc:
            valuation_lookup = {}
            st.warning(f"Similarity rows loaded, but valuation enrichment could not be fetched. {exc}")

        enriched_rows = enrich_similarity_rows(similar_rows, valuation_lookup)
        st.dataframe(enriched_rows, use_container_width=True, hide_index=True)
