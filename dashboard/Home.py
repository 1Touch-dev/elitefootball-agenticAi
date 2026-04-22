from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError


st.set_page_config(page_title="elitefootball-agenticAi Dashboard", layout="wide")

st.title("elitefootball-agenticAi Dashboard")
st.caption("MVP internal dashboard for IDV player exploration and comparison.")

client = DashboardAPIClient()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(
        """
        ### Available pages
        - **Player** — inspect one player's profile, valuation, and recent match stats
        - **Compare** — inspect similarity results and related valuation context
        """
    )
with col2:
    st.markdown("### Backend status")
    try:
        health = client.get_health()
        st.success(f"API reachable: {health.get('status', 'unknown')}")
    except DashboardAPIError as exc:
        st.error(str(exc))

st.info(
    "Start the backend first, then run the dashboard. "
    "Default API base URL: `http://localhost:8000` or override with `ELITEFOOTBALL_API_BASE_URL`."
)
