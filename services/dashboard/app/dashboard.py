"""
PortEdge Live Dashboard
=======================
Real-time view of edge gateway sensors and alerts.
"""

import os
import time
from datetime import datetime

import httpx
import pandas as pd
import streamlit as st
import plotly.express as px

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.set_page_config(
    page_title="PortEdge — Smart Port Edge Monitor",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚓ PortEdge — Edge Computing Dashboard")
st.caption("Real-time monitoring for Jeddah Islamic Port style operations · Computer Engineering Portfolio")

# Sidebar
st.sidebar.header("Controls")
refresh_rate = st.sidebar.slider("Refresh interval (seconds)", 2, 15, 4)
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)

# Fetch helpers
@st.cache_data(ttl=2)
def fetch_health():
    try:
        r = httpx.get(f"{GATEWAY_URL}/health", timeout=3.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=2)
def fetch_sensors():
    try:
        r = httpx.get(f"{GATEWAY_URL}/sensors", timeout=3.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "sensors": []}


@st.cache_data(ttl=2)
def fetch_alerts(limit=30):
    try:
        r = httpx.get(f"{GATEWAY_URL}/alerts?limit={limit}", timeout=3.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "alerts": []}


# Main layout
health = fetch_health()
sensors_data = fetch_sensors()
alerts_data = fetch_alerts()

# Status row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    status = health.get("status", "unknown")
    color = "🟢" if status == "ok" else "🟠"
    st.metric("Gateway Status", f"{color} {status.upper()}")

with col2:
    st.metric("MQTT Connected", "✅ Yes" if health.get("mqtt_connected") else "❌ No")

with col3:
    st.metric("Sensors Seen", health.get("sensors_seen", 0))

with col4:
    st.metric("Total Readings", health.get("total_readings", 0))

with col5:
    st.metric("Active Alerts", health.get("active_alerts", 0))

st.divider()

# Two columns: sensors + alerts
left, right = st.columns([1.4, 1])

with left:
    st.subheader("📡 Live Sensors")
    sensors = sensors_data.get("sensors", [])
    if sensors:
        df = pd.DataFrame(sensors)
        st.dataframe(
            df[["sensor_id", "type", "value", "unit", "location", "timestamp"]],
            use_container_width=True,
            hide_index=True,
        )

        if not df.empty:
            fig = px.bar(
                df,
                x="sensor_id",
                y="value",
                color="type",
                title="Current Sensor Values",
                labels={"value": "Value", "sensor_id": "Sensor"},
            )
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for sensor data from the edge gateway...")

with right:
    st.subheader("🚨 Recent Alerts")
    alerts = alerts_data.get("alerts", [])
    if alerts:
        for a in alerts[:12]:
            sev = a.get("severity", "low")
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(sev, "⚪")
            st.markdown(
                f"{icon} **{sev.upper()}** · `{a['sensor_id']}`  \n"
                f"{a['message']}  \n"
                f"<small>{a['timestamp']}</small>",
                unsafe_allow_html=True,
            )
            st.divider()
    else:
        st.success("No active alerts — system nominal")

# Footer
st.caption(
    f"Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC · "
    f"Gateway: {GATEWAY_URL} · PortEdge v0.1"
)

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
