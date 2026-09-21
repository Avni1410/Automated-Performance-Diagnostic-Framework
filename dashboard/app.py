"""
app.py

Streamlit dashboard - Overview page.

Shows live CPU / Memory / Disk / Process / Thread status
using the existing collectors, plus historical CPU/Memory
data from the SQLite database.

backend/main.py must run separately to keep the database updated.
"""

import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backend.collector.cpu import get_cpu_metrics
from backend.collector.memory import get_memory_metrics
from backend.collector.disk import get_disk_metrics
from backend.collector.process import get_all_processes
from backend.database.database import get_recent_metrics


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="System Resource Monitor",
    layout="wide"
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("🖥️ System Resource Monitoring Dashboard")
st.caption("Overview — live metrics and recent history")


# ---------------------------------------------------------
# STATUS COLOR
# ---------------------------------------------------------

def status_color(status: str) -> str:
    status = status.upper()

    return {
        "NORMAL": "🟢",
        "WARNING": "🟡",
        "CRITICAL": "🔴"
    }.get(status, "⚪")


# ---------------------------------------------------------
# COLLECT LIVE METRICS
# ---------------------------------------------------------

cpu = get_cpu_metrics()
memory = get_memory_metrics()
disk = get_disk_metrics()

processes = get_all_processes()

total_threads = sum(
    process["num_threads"]
    for process in processes
)


# ---------------------------------------------------------
# DISPLAY LIVE METRICS
# ---------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    label=f"{status_color(cpu['status'])} CPU Usage",
    value=f"{cpu['total_percent']}%"
)


col2.metric(
    label=f"{status_color(memory['status'])} Memory Usage",
    value=f"{memory['percent']}%"
)


col3.metric(
    label=f"{status_color(disk['status'])} Disk Usage",
    value=f"{disk['percent']}%"
)


col4.metric(
    label="Processes",
    value=len(processes)
)


col5.metric(
    label="Total Threads",
    value=total_threads
)


# ---------------------------------------------------------
# HISTORICAL DATA
# ---------------------------------------------------------

st.divider()

st.subheader("📈 Recent History (Last 50 Readings)")


history = get_recent_metrics(limit=50)


if len(history) == 0:

    st.info(
        "No historical data yet. Make sure "
        "`backend/main.py` is running in another "
        "terminal to collect data."
    )

else:

    df = pd.DataFrame(history)

    fig = go.Figure()


    # CPU line
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["cpu_percent"],
            mode="lines+markers",
            name="CPU %"
        )
    )


    # Memory line
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["memory_percent"],
            mode="lines+markers",
            name="Memory %"
        )
    )


    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Usage %",
        yaxis_range=[0, 100],
        height=400
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "This dashboard refreshes automatically every 5 seconds. "
    "Make sure backend/main.py is running separately."
)


# ---------------------------------------------------------
# AUTO REFRESH
# ---------------------------------------------------------

time.sleep(5)

st.rerun()