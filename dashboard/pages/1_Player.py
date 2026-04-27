from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import build_dashboard_state, explain_players_empty, explain_stats_issue, placeholder_message_lines


st.set_page_config(page_title="Player Dashboard", layout="wide")
st.title("Player")

client = DashboardAPIClient()
status_payload = None
player_payload = {"items": []}
backend_error = None

try:
    with st.spinner("Loading player data..."):
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

if st.button("Retry player data", key="retry-player-page"):
    st.rerun()

players = player_payload.get("items", []) if isinstance(player_payload, dict) else []
if not players:
    empty_state = build_dashboard_state(status_payload, no_records_label="players")
    st.info(explain_players_empty(status_payload))
    for line in placeholder_message_lines(empty_state)[1:]:
        st.caption(line)
    st.stop()

player_names = [row.get("player_name", "unknown-player") for row in players]
default_player = player_names[0]
selected_player = st.selectbox("Choose a player", player_names, index=0)
selected_row = next((row for row in players if row.get("player_name") == selected_player), players[0])

profile_col, value_col, kpi_col = st.columns(3)
with profile_col:
    st.subheader(selected_row.get("player_name", default_player))
    st.write(f"**Preferred name:** {selected_row.get('preferred_name') or '—'}")
    st.write(f"**Position:** {selected_row.get('position') or '—'}")
    st.write(f"**Club:** {selected_row.get('current_club') or '—'}")
    st.write(f"**Nationality:** {selected_row.get('nationality') or '—'}")
    st.write(f"**Date of birth:** {selected_row.get('date_of_birth') or '—'}")

valuation = selected_row.get("valuation") or {}
with value_col:
    st.subheader("Valuation")
    if valuation:
        st.metric("Score", valuation.get("valuation_score", "—"))
        st.write(f"**Tier:** {valuation.get('valuation_tier') or '—'}")
        st.write(f"**Model:** {valuation.get('model_version') or '—'}")
    else:
        st.info("No valuation data is available for this player yet.")
        if state.get("last_sync"):
            st.caption(f"Last successful sync: {state['last_sync']}")

kpi = selected_row.get("kpi") or {}
features = selected_row.get("features") or {}
with kpi_col:
    st.subheader("Performance")
    if kpi:
        st.metric("Base KPI", kpi.get("base_kpi_score", "—"))
        st.metric("Consistency", kpi.get("consistency_score", "—"))
    elif features:
        st.metric("Matches", features.get("matches", "—"))
        st.metric("Goal contribution/90", features.get("goal_contribution_per_90", "—"))
    else:
        st.info("No KPI or feature data is available for this player yet.")
        if state.get("last_sync"):
            st.caption(f"Last successful sync: {state['last_sync']}")

st.divider()
st.subheader("Recent match stats")
try:
    with st.spinner("Loading recent match stats..."):
        stats_payload = client.get_player_stats(selected_player, limit=20)
    stats_rows = stats_payload.get("items", [])
    if stats_rows:
        st.dataframe(stats_rows, use_container_width=True, hide_index=True)
    else:
        no_records_state = build_dashboard_state(status_payload, no_records_label="recent match records")
        st.info(explain_stats_issue(status_payload))
        for line in placeholder_message_lines(no_records_state)[1:]:
            st.caption(line)
except DashboardAPIError as exc:
    error_state = build_dashboard_state(status_payload, backend_error=str(exc))
    st.warning(explain_stats_issue(status_payload))
    for line in placeholder_message_lines(error_state):
        st.caption(line)
