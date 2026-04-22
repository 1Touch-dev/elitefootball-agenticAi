from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError


st.set_page_config(page_title="Compare Players", layout="wide")
st.title("Compare")

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
        st.info("No valuation data available for the selected player.")

st.divider()

try:
    compare_payload = client.get_compare(selected_player, limit=limit)
except DashboardAPIError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Comparison features")
comparison_features = compare_payload.get("comparison_features") or {}
if comparison_features:
    st.json(comparison_features)
else:
    st.info("No comparison features are available yet.")

st.subheader("Similar players")
similar_rows = compare_payload.get("similar_players") or []
if not similar_rows:
    st.info("No comparison results are available yet.")
else:
    try:
        valuation_lookup_payload = client.get_value(limit=200)
        valuation_lookup = {
            row.get("player_name"): row
            for row in valuation_lookup_payload.get("items", [])
            if isinstance(row, dict)
        }
    except DashboardAPIError:
        valuation_lookup = {}

    enriched_rows = []
    for row in similar_rows:
        enriched_rows.append(valuation_lookup.get(row.get("player_name"), {**row}))

    st.dataframe(enriched_rows, use_container_width=True)
