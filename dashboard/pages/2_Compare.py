from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import dashboard_status_message, enrich_similarity_rows, explain_compare_issue, explain_players_empty


st.set_page_config(page_title="Compare Players", layout="wide")
st.title("Compare")

client = DashboardAPIClient()
status_payload = None

try:
    with st.spinner("Loading comparison data..."):
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

compare_payload = None
compare_error = None
try:
    with st.spinner("Loading comparison results..."):
        compare_payload = client.get_compare(selected_player, limit=limit)
except DashboardAPIError as exc:
    compare_error = exc

st.subheader("Comparison features")
if compare_payload is None:
    st.warning(f"{explain_compare_issue(status_payload)} {compare_error}")
else:
    comparison_features = compare_payload.get("comparison_features") or {}
    if comparison_features:
        st.json(comparison_features)
    else:
        st.info("No comparison features are available yet.")

st.subheader("Similar players")
if compare_payload is None:
    st.info("Player summary is still available above even though comparison results could not be loaded.")
else:
    similar_rows = compare_payload.get("similar_players") or []
    if not similar_rows:
        st.info(explain_compare_issue(status_payload))
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

        enriched_rows = enrich_similarity_rows(similar_rows, valuation_lookup)
        st.dataframe(enriched_rows, use_container_width=True, hide_index=True)
