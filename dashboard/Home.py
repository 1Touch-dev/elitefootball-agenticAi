from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import artifact_summary_rows, dashboard_status_message


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
        with st.spinner("Loading dashboard status..."):
            health = client.get_health()
            status_payload = client.get_dashboard_status()
        level, message = dashboard_status_message(status_payload)
        if level == "success":
            st.success(f"API reachable: {health.get('status', 'unknown')}. {message}")
        elif level == "warning":
            st.warning(f"API reachable: {health.get('status', 'unknown')}. {message}")
        elif level == "error":
            st.error(f"API reachable: {health.get('status', 'unknown')}. {message}")
        else:
            st.info(f"API reachable: {health.get('status', 'unknown')}. {message}")

        summary_rows = artifact_summary_rows(status_payload)
        if summary_rows:
            st.dataframe(summary_rows, use_container_width=True, hide_index=True)
    except DashboardAPIError as exc:
        st.error(str(exc))

st.info(
    "Start the backend first, then run the dashboard. "
    "Default API base URL: `http://localhost:8000` or override with `ELITEFOOTBALL_API_BASE_URL`."
)
