from __future__ import annotations

import streamlit as st

from dashboard.api_client import DashboardAPIClient, DashboardAPIError
from dashboard.helpers import artifact_summary_rows, build_dashboard_state, placeholder_message_lines


st.set_page_config(page_title="elitefootball-agenticAi Dashboard", layout="wide")

st.title("elitefootball-agenticAi Dashboard")
st.caption("MVP internal dashboard for IDV player exploration and comparison.")

client = DashboardAPIClient()
health = None
status_payload = None
backend_error = None

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
    except DashboardAPIError as exc:
        backend_error = str(exc)

    state = build_dashboard_state(status_payload, backend_error=backend_error)
    if state["level"] == "success":
        st.success(f"{state['title']}: {state['message']}")
    elif state["level"] == "warning":
        st.warning(f"{state['title']}: {state['message']}")
    elif state["level"] == "error":
        st.error(f"{state['title']}: {state['message']}")
    else:
        st.info(f"{state['title']}: {state['message']}")

    if health and isinstance(health, dict):
        st.caption(f"API health: {health.get('status', 'unknown')}")
    for line in placeholder_message_lines(state)[1:]:
        st.caption(line)

    if st.button("Retry status check", key="retry-home-status"):
        st.rerun()

    if status_payload:
        summary_rows = artifact_summary_rows(status_payload)
        if summary_rows:
            st.dataframe(summary_rows, use_container_width=True, hide_index=True)

st.info(
    "Start the backend first, then run the dashboard. "
    "Default API base URL: `http://localhost:8000` or override with `ELITEFOOTBALL_API_BASE_URL`."
)
