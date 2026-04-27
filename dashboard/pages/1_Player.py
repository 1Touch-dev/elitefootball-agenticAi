from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import dashboard_status_message, explain_players_empty, explain_stats_issue


st.set_page_config(page_title="Player Dashboard", layout="wide")
st.title("Player")

client = DashboardAPIClient()
status_payload = None

try:
    with st.spinner("Loading player data..."):
        status_payload = client.get_dashboard_status()
        player_payload = client.get_players(limit=200)
except DashboardAPIError as exc:
    st.error(str(exc))
    st.stop()

level, message = dashboard_status_message(status_payload)
if level == "warning":
    st.warning(message)
elif level == "info":
    st.info(message)
elif level == "error":
    st.error(message)
else:
    st.success(message)

players = player_payload.get("items", [])
if not players:
    st.warning(explain_players_empty(status_payload))
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
        st.info("No valuation data available for this player yet.")

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
        st.info("No KPI or feature data available for this player yet.")

st.divider()
st.subheader("Recent match stats")
try:
    with st.spinner("Loading recent match stats..."):
        stats_payload = client.get_player_stats(selected_player, limit=20)
    stats_rows = stats_payload.get("items", [])
    if stats_rows:
        st.dataframe(stats_rows, use_container_width=True, hide_index=True)
    else:
        st.info(explain_stats_issue(status_payload))
except DashboardAPIError as exc:
    st.warning(f"{explain_stats_issue(status_payload)} {exc}")
