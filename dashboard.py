import pandas as pd
import streamlit as st
import plotly.express as px

from streamlit_autorefresh import st_autorefresh
from metrics import format_bytes

from monitoring import (
    calculate_baseline,
    compare_with_baseline,
    calculate_deviation
)


HISTORICAL_FILE = "historical_data.csv"


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="Network Traffic Monitor",
    page_icon="📡",
    layout="wide"
)


# Refresh every 10 seconds
st_autorefresh(
    interval=10000,
    key="network_monitor_refresh"
)


# ==================================================
# Load Historical Data
# ==================================================

def load_data():

    df = pd.read_csv(
        HISTORICAL_FILE
    )

    if df.empty:
        return df

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # Sort by time
    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return df


df = load_data()


# ==================================================
# Check Data
# ==================================================

if df.empty:

    st.error(
        "No historical data available."
    )

    st.stop()


# ==================================================
# Current Data
# ==================================================

latest = df.iloc[-1]

current_throughput = (
    latest["throughput_mbps"]
)

current_packets = (
    latest["total_packets"]
)

current_bytes = (
    latest["total_bytes"]
)


# ==================================================
# Baseline Monitoring
# ==================================================

baseline = calculate_baseline(
    df
)

status, warning_threshold = (
    compare_with_baseline(
        current_throughput,
        baseline
    )
)

deviation = calculate_deviation(
    current_throughput,
    baseline
)

# ==================================================
# Alert Toast
# ==================================================

if "previous_status" not in st.session_state:
    st.session_state.previous_status = status


if (
    status == "WARNING"
    and st.session_state.previous_status != "WARNING"
):

    st.toast(
        "Current traffic is above the baseline.",
        icon="🚨",
        duration="long"
    )

st.session_state.previous_status = status

# ==================================================
# Header
# ==================================================

st.title(
    "📡 Network Traffic Monitor"
)

st.caption(
    "Network traffic analysis and performance monitoring dashboard"
)


# ==================================================
# KPI Cards
# ==================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Traffic Volume",
        format_bytes(current_bytes)
    )


with col2:

    st.metric(
        "Throughput",
        f"{current_throughput:.3f} Mbps"
    )


with col3:

    st.metric(
        "Packets",
        f"{current_packets:,}"
    )


with col4:

    st.metric(
        "Baseline",
        f"{baseline:.3f} Mbps"
    )


# ==================================================
# Historical Throughput
# ==================================================

st.subheader(
    "Historical Network Throughput"
)


# Time range selector
period = st.selectbox(
    "Select time range",
    [
        "Last 1 Hour",
        "Last 6 Hours",
        "Last 24 Hours",
        "All Data"
    ],
    index=3
)


# Latest timestamp
latest_time = df["timestamp"].max()


# ==================================================
# Filter Historical Data
# ==================================================

if period == "Last 1 Hour":

    start_time = (
        latest_time
        - pd.Timedelta(hours=1)
    )

    historical_view = df[
        df["timestamp"] >= start_time
    ]


elif period == "Last 6 Hours":

    start_time = (
        latest_time
        - pd.Timedelta(hours=6)
    )

    historical_view = df[
        df["timestamp"] >= start_time
    ]


elif period == "Last 24 Hours":

    start_time = (
        latest_time
        - pd.Timedelta(hours=24)
    )

    historical_view = df[
        df["timestamp"] >= start_time
    ]


else:

    historical_view = df


# ==================================================
# Historical Throughput Chart
# ==================================================

if historical_view.empty:

    st.info(
        "No historical data available for this time range."
    )

else:

    throughput_fig = px.line(
        historical_view,
        x="timestamp",
        y="throughput_mbps",
        markers=True,
        title="Throughput Over Time"
    )

    throughput_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Throughput (Mbps)"
    )

    st.plotly_chart(
        throughput_fig,
        use_container_width=True
    )


# ==================================================
# Protocol Distribution + Baseline
# ==================================================

col1, col2 = st.columns(2)


# ==================================================
# Protocol Distribution
# ==================================================

with col1:

    st.subheader(
        "Current Protocol Distribution"
    )

    protocol_data = pd.DataFrame({

        "Protocol": [
            "TCP",
            "UDP",
            "ICMP",
            "ARP"
        ],

        "Percentage": [
            latest["tcp_percent"],
            latest["udp_percent"],
            latest["icmp_percent"],
            latest["arp_percent"]
        ]

    })


    # Remove protocols with zero traffic
    protocol_data = protocol_data[
        protocol_data["Percentage"] > 0
    ]


    protocol_fig = px.bar(
        protocol_data,
        x="Protocol",
        y="Percentage",
        text="Percentage",
        title="Protocol Distribution"
    )


    protocol_fig.update_layout(
        xaxis_title="Protocol",
        yaxis_title="Percentage (%)"
    )


    protocol_fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )


    st.plotly_chart(
        protocol_fig,
        use_container_width=True
    )


# ==================================================
# Baseline Comparison
# ==================================================

with col2:

    st.subheader(
        "Baseline Comparison"
    )


    st.metric(
        "Current Throughput",
        f"{current_throughput:.3f} Mbps"
    )


    st.metric(
        "Normal Baseline",
        f"{baseline:.3f} Mbps"
    )


    st.metric(
        "Warning Threshold",
        f"{warning_threshold:.3f} Mbps"
    )


    st.metric(
        "Deviation",
        f"{deviation:+.2f}%"
    )


    if status == "WARNING":

        st.warning(
            "⚠ Current traffic is above the baseline."
        )

    else:

        st.success(
            "✓ Current traffic is within the expected range."
        )


# ==================================================
# Recent Measurements
# ==================================================

st.subheader(
    "Recent Measurements"
)


display_columns = [
    "timestamp",
    "total_packets",
    "total_bytes",
    "throughput_mbps"
]


recent_data = df[
    display_columns
].tail(10).copy()


# ==================================================
# Format Recent Data
# ==================================================

# Convert bytes to KB
recent_data["total_bytes"] = (
    recent_data["total_bytes"]
    / 1024
).round(2)


# Round throughput
recent_data["throughput_mbps"] = (
    recent_data["throughput_mbps"]
    .round(3)
)


# Rename columns
recent_data = recent_data.rename(
    columns={

        "timestamp":
            "Time",

        "total_packets":
            "Packets",

        "total_bytes":
            "Traffic (KB)",

        "throughput_mbps":
            "Throughput (Mbps)"
    }
)


# ==================================================
# Display Recent Data
# ==================================================

st.dataframe(
    recent_data,
    use_container_width=True,
    hide_index=True
)