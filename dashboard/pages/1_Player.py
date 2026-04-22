from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError


st.set_page_config(page_title="Player Dashboard", layout="wide")
st.title("Player")

client = DashboardAPIClient()

try:
    player_payload = client.get_players(limit=200)
except DashboardAPIError as exc:
    st.error(str(exc))
    st.stop()

players = player_payload.get("items", [])
if not players:
    st.warning("No player data is available yet. Run the backend pipeline and refresh.")
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
    stats_payload = client.get_player_stats(selected_player, limit=20)
    stats_rows = stats_payload.get("items", [])
    if stats_rows:
        st.dataframe(stats_rows, use_container_width=True)
    else:
        st.info("No match stats available for this player yet.")
except DashboardAPIError as exc:
    st.warning(str(exc))
