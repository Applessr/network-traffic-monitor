import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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


# ==================================================
# Auto Refresh
# ==================================================

st_autorefresh(
    interval=10000,
    key="network_monitor_refresh"
)


# ==================================================
# Theme-aware CSS
# ==================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ------------------------------------------
       Header
    ------------------------------------------ */

    .dashboard-title {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.02em;
        color: var(--st-text-color);
    }

    .dashboard-subtitle {
        font-size: 0.95rem;
        color: var(--st-text-color);
        opacity: 0.65;
        margin-top: 0.25rem;
    }

    .live-status {
        text-align: right;
        color: var(--st-text-color);
        opacity: 0.75;
        padding-top: 0.3rem;
    }

    .live-label {
        color: #22c55e;
        font-weight: 800;
        font-size: 0.95rem;
    }

    .live-time {
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }


    /* ------------------------------------------
       Section title
    ------------------------------------------ */

    .section-title {
        font-size: 1.15rem;
        font-weight: 750;
        color: var(--st-text-color);
        margin-bottom: 0.5rem;
    }


    /* ------------------------------------------
       Card accents (legacy, kept for compatibility)
    ------------------------------------------ */

    .accent-blue {
        height: 4px;
        width: 52px;
        border-radius: 10px;
        background: #38bdf8;
        margin-bottom: 0.7rem;
    }

    .accent-teal {
        height: 4px;
        width: 52px;
        border-radius: 10px;
        background: #2dd4bf;
        margin-bottom: 0.7rem;
    }

    .accent-purple {
        height: 4px;
        width: 52px;
        border-radius: 10px;
        background: #a78bfa;
        margin-bottom: 0.7rem;
    }

    .accent-orange {
        height: 4px;
        width: 52px;
        border-radius: 10px;
        background: #f59e0b;
        margin-bottom: 0.7rem;
    }


    /* ------------------------------------------
       Card header: icon chip + title, replaces
       the plain accent bar for a more finished,
       "designed" feel while staying simple.
    ------------------------------------------ */

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.9rem;
    }

    .card-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        min-width: 34px;
        border-radius: 10px;
        font-size: 1.05rem;
        line-height: 1;
    }

    .card-header-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: var(--st-text-color);
        letter-spacing: -0.01em;
    }


    /* ------------------------------------------
       Stat blocks: consistent label / value /
       sub-value typography used across every
       card so numbers always read the same way.
    ------------------------------------------ */

    .stat-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--st-text-color);
        opacity: 0.5;
        margin-bottom: 0.15rem;
    }

    .stat-value {
        font-size: 1.55rem;
        font-weight: 750;
        line-height: 1.15;
        letter-spacing: -0.02em;
        color: var(--st-text-color);
    }

    .stat-sub {
        font-size: 0.75rem;
        opacity: 0.5;
        color: var(--st-text-color);
        margin-top: 0.1rem;
    }


    /* ------------------------------------------
       LIVE pill badge
    ------------------------------------------ */

    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        font-size: 0.78rem;
        font-weight: 700;
        color: #22c55e;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.20);
    }


    /* ------------------------------------------
       Soft panel: gives a chart or block its own
       visual weight instead of floating loosely
       in the card's whitespace.
    ------------------------------------------ */

    .soft-panel {
        background: rgba(128, 128, 128, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.14);
        border-radius: 12px;
        padding: 0.9rem 1rem 0.6rem 1rem;
    }

    .row-divider {
        border-top: 1px solid rgba(128, 128, 128, 0.14);
        margin: 0.9rem 0 0.9rem 0;
    }


    /* ------------------------------------------
       Hero status band: the headline read of the
       whole dashboard, front and center under
       the page title.
    ------------------------------------------ */

    .hero-band {
        border-radius: 16px;
        padding: 1.1rem 1.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    .hero-band.is-normal {
        background: linear-gradient(135deg, rgba(34,197,94,0.14), rgba(34,197,94,0.04));
        border: 1px solid rgba(34, 197, 94, 0.30);
    }

    .hero-band.is-warning {
        background: linear-gradient(135deg, rgba(245,158,11,0.18), rgba(239,68,68,0.05));
        border: 1px solid rgba(245, 158, 11, 0.40);
    }

    .hero-left {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }

    .hero-icon {
        width: 48px;
        height: 48px;
        min-width: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    .hero-title {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: var(--st-text-color);
    }

    .hero-subtitle {
        font-size: 0.82rem;
        opacity: 0.65;
        color: var(--st-text-color);
        margin-top: 0.1rem;
    }

    .hero-stats {
        display: flex;
        gap: 1.8rem;
    }

    .hero-stat-label {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.55;
        color: var(--st-text-color);
    }

    .hero-stat-value {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--st-text-color);
    }


    /* ------------------------------------------
       Trend badge: small up/down chip next to a
       stat value showing change vs. the previous
       reading.
    ------------------------------------------ */

    .trend-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.1rem 0.45rem;
        border-radius: 999px;
        margin-left: 0.4rem;
        vertical-align: middle;
    }

    .trend-up {
        color: #ef4444;
        background: rgba(239, 68, 68, 0.12);
    }

    .trend-down {
        color: #22c55e;
        background: rgba(34, 197, 94, 0.12);
    }

    .trend-flat {
        color: #94a3b8;
        background: rgba(148, 163, 184, 0.12);
    }


    /* ------------------------------------------
       Subtle elevation on bordered cards for a
       bit of depth (safe no-op if the selector
       doesn't match a future Streamlit version).
    ------------------------------------------ */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
    }


    /* ------------------------------------------
       Status
    ------------------------------------------ */

    .normal-status {
        color: #22c55e;
        font-size: 1.35rem;
        font-weight: 800;
    }

    .warning-status {
        color: #f59e0b;
        font-size: 1.35rem;
        font-weight: 800;
    }


    /* ------------------------------------------
       Alert boxes
    ------------------------------------------ */

    .normal-box {
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.30);
        border-radius: 10px;
        padding: 0.6rem 0.85rem;
        color: #22c55e;
        font-weight: 500;
        font-size: 0.85rem;
    }

    .warning-box {
        background: rgba(245, 158, 11, 0.10);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 10px;
        padding: 0.6rem 0.85rem;
        color: #f59e0b;
        font-weight: 500;
        font-size: 0.85rem;
    }


    /* ------------------------------------------
       Information text
    ------------------------------------------ */

    .info-label {
        font-size: 0.78rem;
        color: var(--st-text-color);
        opacity: 0.58;
    }

    .info-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--st-text-color);
    }

    /* ------------------------------------------
       Alert log rows
    ------------------------------------------ */

    .alert-log-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        padding: 0.25rem 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
        color: var(--st-text-color);
    }

    .alert-log-empty {
        font-size: 0.85rem;
        opacity: 0.55;
        padding: 0.35rem 0;
        color: var(--st-text-color);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# Load Data
# ==================================================

def load_data():

    df = pd.read_csv(
        HISTORICAL_FILE
    )

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

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
# Helper: break line charts across real time gaps
# ==================================================

def insert_gap_breaks(data, time_col, value_cols, gap_multiplier=3):
    """
    Inserts NaN rows wherever the gap between two consecutive
    timestamps is much larger than the typical sampling interval,
    so Plotly draws a break instead of a misleading straight line
    across missing data.
    """

    if len(data) < 3:
        return data

    diffs = data[time_col].diff().dropna()

    # Use the median interval as "normal" cadence, ignoring outliers.
    median_diff = diffs.median()

    if pd.isna(median_diff) or median_diff <= pd.Timedelta(0):
        return data

    threshold = median_diff * gap_multiplier

    rows = []

    for i in range(len(data)):

        rows.append(data.iloc[i])

        if i < len(data) - 1:

            gap = data.iloc[i + 1][time_col] - data.iloc[i][time_col]

            if gap > threshold:

                gap_row = data.iloc[i].copy()
                gap_row[time_col] = data.iloc[i][time_col] + (gap / 2)

                for col in value_cols:
                    gap_row[col] = np.nan

                rows.append(gap_row)

    return pd.DataFrame(rows).reset_index(drop=True)


# ==================================================
# Helper: smooth a series for sparkline display
# ==================================================

def smooth_series(series, window=3):

    if len(series) < window:
        return series

    return series.rolling(
        window=window,
        min_periods=1,
        center=True
    ).mean()


# ==================================================
# Helper: card header (icon chip + title)
# ==================================================

def card_header(icon, title, color):

    st.markdown(
        f'<div class="card-header">'
        f'<div class="card-icon" style="background: {color}22; color: {color};">'
        f'{icon}'
        f'</div>'
        f'<div class="card-header-title">{title}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ==================================================
# Helper: consistent stat block (label / value / sub)
# ==================================================

def render_stat(label, value, sub=None, color=None, size="1.55rem", badge=""):

    color_style = f"color: {color};" if color else ""

    sub_html = (
        f'<div class="stat-sub">{sub}</div>'
        if sub else ""
    )

    st.markdown(
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value" style="font-size:{size}; {color_style}">{value}{badge}</div>'
        f'{sub_html}',
        unsafe_allow_html=True
    )


# ==================================================
# Helper: consistent vertical gap between blocks
# ==================================================

def spacer(px=14):

    st.markdown(
        f'<div style="height:{px}px;"></div>',
        unsafe_allow_html=True
    )


# ==================================================
# Helper: small up/down trend badge vs. previous
# reading, rendered inline next to a stat label.
# ==================================================

def trend_badge(current, previous):

    if previous is None or previous == 0 or pd.isna(previous):
        return ""

    pct_change = ((current - previous) / abs(previous)) * 100

    if abs(pct_change) < 0.5:
        return '<span class="trend-badge trend-flat">→ flat</span>'

    if pct_change > 0:
        return f'<span class="trend-badge trend-up">▲ {pct_change:.0f}%</span>'

    return f'<span class="trend-badge trend-down">▼ {abs(pct_change):.0f}%</span>'


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

latest_time = df["timestamp"].max()

# Previous reading, for trend badges (None if there's only one row).
previous_row = df.iloc[-2] if len(df) > 1 else None
previous_throughput = previous_row["throughput_mbps"] if previous_row is not None else None
previous_bytes = previous_row["total_bytes"] if previous_row is not None else None


# ==================================================
# Baseline
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
# Toast + Alert Log
# ==================================================

if "previous_status" not in st.session_state:
    st.session_state.previous_status = status

if "alert_log" not in st.session_state:
    st.session_state.alert_log = []

if (
    status == "WARNING"
    and st.session_state.previous_status != "WARNING"
):

    st.toast(
        "Current traffic is above the baseline.",
        icon="🚨"
    )

    st.session_state.alert_log.insert(
        0,
        {
            "time": latest_time,
            "throughput": current_throughput,
            "deviation": deviation
        }
    )

    # Keep only the most recent 5 alerts.
    st.session_state.alert_log = st.session_state.alert_log[:5]


st.session_state.previous_status = status


# ==================================================
# Format Time
# ==================================================

latest_time_display = latest_time.strftime(
    "%Y-%m-%d %I:%M %p"
)


# ==================================================
# Header
# ==================================================

header_left, header_right = st.columns(
    [4, 1]
)


with header_left:

    st.markdown(
        '<div class="dashboard-title">'
        '📡 Network Traffic Monitor'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Network traffic analysis and performance monitoring dashboard'
        '</div>',
        unsafe_allow_html=True
    )


with header_right:

    st.markdown(
        '<div style="text-align:right;">'
        '<span class="live-pill">'
        '<span class="live-dot"></span> LIVE'
        '</span>'
        f'<div class="live-time" style="margin-top:0.4rem; opacity:0.6;">{latest_time_display}</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ==================================================
# Hero Status Band
# ==================================================

if status == "WARNING":

    hero_class = "is-warning"
    hero_icon = "⚠"
    hero_icon_bg = "rgba(245, 158, 11, 0.20)"
    hero_icon_color = "#f59e0b"
    hero_headline = "Elevated traffic detected"
    hero_sub = "Current throughput is running above the normal baseline."

else:

    hero_class = "is-normal"
    hero_icon = "✓"
    hero_icon_bg = "rgba(34, 197, 94, 0.20)"
    hero_icon_color = "#22c55e"
    hero_headline = "Network is running normally"
    hero_sub = "Current throughput is within the expected range."

deviation_sign_color = "#f59e0b" if status == "WARNING" else "#22c55e"

st.markdown(
    f'<div class="hero-band {hero_class}">'
    f'<div class="hero-left">'
    f'<div class="hero-icon" style="background:{hero_icon_bg}; color:{hero_icon_color};">{hero_icon}</div>'
    f'<div>'
    f'<div class="hero-title">{hero_headline}</div>'
    f'<div class="hero-subtitle">{hero_sub}</div>'
    f'</div>'
    f'</div>'
    f'<div class="hero-stats">'
    f'<div><div class="hero-stat-label">Current</div>'
    f'<div class="hero-stat-value">{current_throughput:.2f} Mbps</div></div>'
    f'<div><div class="hero-stat-label">Baseline</div>'
    f'<div class="hero-stat-value">{baseline:.2f} Mbps</div></div>'
    f'<div><div class="hero-stat-label">Deviation</div>'
    f'<div class="hero-stat-value" style="color:{deviation_sign_color};">{deviation:+.1f}%</div></div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)


# ==================================================
# Top Cards
# ==================================================

traffic_col, throughput_col, protocol_col = st.columns(
    [1, 1, 1],
    gap="medium"
)


# ==================================================
# Traffic Volume
# ==================================================

with traffic_col:

    with st.container(
        border=True,
        height=280,
        key="traffic_volume_card"
    ):

        card_header("📦", "Traffic Volume", "#38bdf8")

        traffic_trend = trend_badge(current_bytes, previous_bytes)
        render_stat("Current", format_bytes(current_bytes), badge=traffic_trend)

        spark_df = df.tail(20).copy()

        spark_df["traffic_mb"] = (
            spark_df["total_bytes"]
            / (1024 * 1024)
        )

        # Smooth so short-interval bursts don't dominate the sparkline.
        spark_df["traffic_mb_smooth"] = smooth_series(
            spark_df["traffic_mb"]
        )

        spark_fig = px.line(
            spark_df,
            y="traffic_mb_smooth"
        )

        spark_fig.update_traces(
            line=dict(
                color="#38bdf8",
                width=3,
                shape="spline"
            ),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.16)",
            hovertemplate=(
                "%{y:.2f} MB"
                "<extra></extra>"
            )
        )

        spark_fig.update_layout(
            height=90,
            margin=dict(
                l=0,
                r=0,
                t=5,
                b=0
            ),
            xaxis=dict(
                visible=False
            ),
            yaxis=dict(
                visible=False
            ),
            showlegend=False
        )

        st.plotly_chart(
            spark_fig,
            use_container_width=True,
            theme="streamlit",
            config={
                "displayModeBar": False
            },
            key="traffic_sparkline"
        )


# ==================================================
# Throughput
# ==================================================

with throughput_col:

    with st.container(
        border=True,
        height=280,
        key="throughput_card"
    ):

        card_header("⚡", "Throughput", "#2dd4bf")

        throughput_trend = trend_badge(current_throughput, previous_throughput)
        render_stat(
            "Current",
            f"{current_throughput:.3f} Mbps",
            badge=throughput_trend
        )

        spark_df_t = df.tail(20).copy()

        spark_df_t["throughput_smooth"] = smooth_series(
            spark_df_t["throughput_mbps"]
        )

        spark_fig = px.line(
            spark_df_t,
            y="throughput_smooth"
        )

        spark_fig.update_traces(
            line=dict(
                color="#2dd4bf",
                width=3,
                shape="spline"
            ),
            fill="tozeroy",
            fillcolor="rgba(45, 212, 191, 0.16)",
            hovertemplate=(
                "%{y:.3f} Mbps"
                "<extra></extra>"
            )
        )

        spark_fig.update_layout(
            height=90,
            margin=dict(
                l=0,
                r=0,
                t=5,
                b=0
            ),
            xaxis=dict(
                visible=False
            ),
            yaxis=dict(
                visible=False
            ),
            showlegend=False
        )

        st.plotly_chart(
            spark_fig,
            use_container_width=True,
            theme="streamlit",
            config={
                "displayModeBar": False
            },
            key="throughput_sparkline"
        )

# ==================================================
# Protocol Distribution
# ==================================================

with protocol_col:

    with st.container(
        border=True,
        height=280,
        key="protocol_card"
    ):

        card_header("🌐", "Protocol Distribution", "#a78bfa")

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

        protocol_data = protocol_data[
            protocol_data["Percentage"] > 0
        ]

        if protocol_data.empty:

            st.info(
                "No protocol data available."
            )

        else:

            # Bake the percentage into the label so it's readable
            # without needing to hover.
            protocol_data["Label"] = protocol_data.apply(
                lambda row: f"{row['Protocol']}  {row['Percentage']:.1f}%",
                axis=1
            )

            protocol_colors = {
                "TCP": "#38bdf8",
                "UDP": "#a78bfa",
                "ICMP": "#f59e0b",
                "ARP": "#2dd4bf",
            }

            label_color_map = {
                row["Label"]: protocol_colors.get(row["Protocol"], "#94a3b8")
                for _, row in protocol_data.iterrows()
            }

            dominant_row = protocol_data.loc[
                protocol_data["Percentage"].idxmax()
            ]

            dominant_color = protocol_colors.get(
                dominant_row["Protocol"], "#94a3b8"
            )

            protocol_fig = px.pie(
                protocol_data,
                names="Label",
                values="Percentage",
                hole=0.58,
                color="Label",
                color_discrete_map=label_color_map
            )

            protocol_fig.update_traces(
                textinfo="none",
                hovertemplate=(
                    "%{label}"
                    "<extra></extra>"
                )
            )

            protocol_fig.add_annotation(
                text=(
                    f"<b style='font-size:20px; color:{dominant_color};'>"
                    f"{dominant_row['Percentage']:.0f}%</b>"
                    f"<br><span style='font-size:11px; opacity:0.6;'>"
                    f"{dominant_row['Protocol']}</span>"
                ),
                showarrow=False,
                font=dict(size=13),
                x=0.5,
                y=0.5
            )

            protocol_fig.update_layout(
                height=155,
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0
                ),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(
                        size=11
                    )
                )
            )

            st.plotly_chart(
                protocol_fig,
                use_container_width=True,
                theme="streamlit",
                config={
                    "displayModeBar": False
                },
                key="protocol_chart"
            )



# ==================================================
# Historical Throughput
# ==================================================

with st.container(
    border=True,
    key="historical_card"
):

    card_header("📈", "Historical Network Throughput", "#38bdf8")

    period = st.selectbox(
        "Select time range",
        [
            "Last 1 Hour",
            "Last 6 Hours",
            "Last 24 Hours",
            "Last 7 Days",
            "All Data"
        ],
        index=0,  # default to a focused, recent view instead of "All Data"
        key="historical_period"
    )

    period_lookback = {
        "Last 1 Hour": pd.Timedelta(hours=1),
        "Last 6 Hours": pd.Timedelta(hours=6),
        "Last 24 Hours": pd.Timedelta(hours=24),
        "Last 7 Days": pd.Timedelta(days=7),
    }

    if period in period_lookback:

        start_time = (
            latest_time
            - period_lookback[period]
        )

        historical_view = df[
            df["timestamp"] >= start_time
        ]

    else:

        historical_view = df


    if historical_view.empty:

        st.info(
            "No historical data available "
            "for this time range."
        )

    else:

        # Break the line across real gaps in data collection instead
        # of drawing a straight (misleading) line across missing time.
        historical_plot_df = insert_gap_breaks(
            historical_view,
            time_col="timestamp",
            value_cols=["throughput_mbps"]
        )

        throughput_fig = px.line(
            historical_plot_df,
            x="timestamp",
            y="throughput_mbps",
            markers=True
        )

        throughput_fig.update_traces(
            line=dict(
                color="#38bdf8",
                width=3
            ),
            marker=dict(
                size=6
            ),
            connectgaps=False,
            hovertemplate=(
                "%{x|%Y-%m-%d %I:%M:%S %p}"
                "<br>Throughput: "
                "%{y:.3f} Mbps"
                "<extra></extra>"
            )
        )

        throughput_fig.update_layout(
            height=420,
            xaxis_title="Time",
            yaxis_title="Throughput (Mbps)",
            margin=dict(
                l=20,
                r=20,
                t=10,
                b=20
            )
        )

        # Shade the normal / elevated zones behind the trend line so an
        # anomaly is visible at a glance, using the same color language
        # as the Baseline Comparison gauge.
        chart_y_max = max(
            historical_plot_df["throughput_mbps"].max(skipna=True) or 0,
            warning_threshold
        ) * 1.15

        throughput_fig.add_hrect(
            y0=0, y1=baseline,
            fillcolor="rgba(34, 197, 94, 0.06)",
            line_width=0,
            layer="below"
        )

        throughput_fig.add_hrect(
            y0=baseline, y1=warning_threshold,
            fillcolor="rgba(245, 158, 11, 0.06)",
            line_width=0,
            layer="below"
        )

        throughput_fig.add_hline(
            y=warning_threshold,
            line=dict(color="#ef4444", width=1.5, dash="dot"),
            annotation_text="warning threshold",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#ef4444")
        )

        throughput_fig.update_yaxes(range=[0, chart_y_max])

        st.plotly_chart(
            throughput_fig,
            use_container_width=True,
            theme="streamlit",
            config={
                "displayModeBar": False
            },
            key="historical_chart"
        )


# ==================================================
# Baseline + Alerts
# ==================================================

baseline_col, alert_col = st.columns(
    [1, 1],
    gap="medium"
)


# ==================================================
# Baseline Comparison
# ==================================================

CARD_PAIR_HEIGHT = 400

with baseline_col:

    with st.container(
        border=True,
        height=CARD_PAIR_HEIGHT,
        key="baseline_card"
    ):

        card_header("⚖", "Baseline Comparison", "#f59e0b")

        # ------------------------------------------
        # Stat row: current / baseline / deviation
        # in one aligned row instead of stacked
        # blocks of differing sizes.
        # ------------------------------------------

        c1, c2, c3 = st.columns(3)

        with c1:
            render_stat("Current", f"{current_throughput:.3f}", "Mbps")

        with c2:
            render_stat("Baseline", f"{baseline:.3f}", "Mbps")

        with c3:
            deviation_color = "#f59e0b" if status == "WARNING" else "#22c55e"
            render_stat(
                "Deviation",
                f"{deviation:+.1f}%",
                "vs baseline",
                color=deviation_color
            )

        spacer(18)

        # ------------------------------------------
        # Range gauge, wrapped in its own soft panel
        # so it reads as one deliberate visual block
        # instead of floating in empty space.
        # ------------------------------------------

        gauge_panel = st.container(border=True)

        with gauge_panel:

            axis_max = max(
                warning_threshold * 1.3,
                current_throughput * 1.1,
                baseline * 1.3,
                1.0
            )

            gauge_fig = go.Figure(
                go.Indicator(
                    mode="gauge",
                    value=current_throughput,
                    gauge={
                        "shape": "bullet",
                        "axis": {
                            "range": [0, axis_max],
                            "tickfont": {"size": 10}
                        },
                        "threshold": {
                            "line": {"color": "#ef4444", "width": 3},
                            "thickness": 0.9,
                            "value": warning_threshold
                        },
                        "steps": [
                            {
                                "range": [0, baseline],
                                "color": "rgba(34, 197, 94, 0.40)"
                            },
                            {
                                "range": [baseline, warning_threshold],
                                "color": "rgba(245, 158, 11, 0.35)"
                            },
                            {
                                "range": [warning_threshold, axis_max],
                                "color": "rgba(239, 68, 68, 0.35)"
                            }
                        ],
                        "bar": {"color": "#38bdf8", "thickness": 0.6}
                    }
                )
            )

            gauge_fig.update_layout(
                height=64,
                margin=dict(l=6, r=6, t=10, b=6)
            )

            st.plotly_chart(
                gauge_fig,
                use_container_width=True,
                theme="streamlit",
                config={"displayModeBar": False},
                key="baseline_gauge"
            )

            st.markdown(
                '<div class="info-label">'
                f'Warning threshold: {warning_threshold:.3f} Mbps &nbsp;·&nbsp; '
                '<span style="color:#22c55e;">■</span> normal &nbsp;'
                '<span style="color:#f59e0b;">■</span> elevated &nbsp;'
                '<span style="color:#ef4444;">■</span> above threshold'
                '</div>',
                unsafe_allow_html=True
            )

        spacer(18)

        # ------------------------------------------
        # Single, compact status pill (color already
        # carries the meaning via the gauge above, so
        # this is a short confirmation, not a repeat
        # of the same message in a big box).
        # ------------------------------------------

        if status == "WARNING":

            st.markdown(
                """
                <div class="warning-box">
                    ⚠ <b>WARNING</b> — current traffic is above the baseline.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="normal-box">
                    ✓ <b>NORMAL</b> — current traffic is within the expected range.
                </div>
                """,
                unsafe_allow_html=True
            )


# ==================================================
# Alerts
# ==================================================

with alert_col:

    with st.container(
        border=True,
        height=CARD_PAIR_HEIGHT,
        key="alerts_card"
    ):

        card_header("🔔", "Alerts", "#f59e0b")

        # ------------------------------------------
        # Stat row, matching the baseline card's
        # 3-column rhythm: latest check / status /
        # alert count.
        # ------------------------------------------

        a1, a2, a3 = st.columns(3)

        with a1:
            render_stat(
                "Latest Check",
                latest_time.strftime("%I:%M %p"),
                latest_time.strftime("%m/%d")
            )

        with a2:
            status_color = "#f59e0b" if status == "WARNING" else "#22c55e"
            status_label = "WARNING" if status == "WARNING" else "NORMAL"
            render_stat(
                "Status",
                status_label,
                "current state",
                color=status_color
            )

        with a3:
            render_stat(
                "Alerts",
                str(len(st.session_state.alert_log)),
                "this session"
            )

        spacer(18)

        # ------------------------------------------
        # Single compact status pill, same visual
        # weight as the baseline card's pill.
        # ------------------------------------------

        if status == "WARNING":

            st.markdown(
                """
                <div class="warning-box">
                    🚨 <b>Traffic increase detected</b> — above the configured
                    warning level.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="normal-box">
                    ✓ <b>No abnormal traffic increase</b> — within the expected range.
                </div>
                """,
                unsafe_allow_html=True
            )

        spacer(18)

        # ------------------------------------------
        # Recent alert history, in its own bordered
        # panel so it carries the same visual weight
        # as the gauge panel in the Baseline card.
        # ------------------------------------------

        history_panel = st.container(border=True)

        with history_panel:

            st.markdown(
                '<div class="info-label" style="margin-bottom:0.5rem;">'
                'RECENT ALERTS'
                '</div>',
                unsafe_allow_html=True
            )

            if not st.session_state.alert_log:

                st.markdown(
                    '<div class="alert-log-empty" style="text-align:center; padding:0.6rem 0;">'
                    '✓ No alerts triggered this session'
                    '</div>',
                    unsafe_allow_html=True
                )

            else:

                for entry in st.session_state.alert_log:

                    entry_time = entry["time"].strftime("%I:%M %p")

                    st.markdown(
                        f'<div class="alert-log-row">'
                        f'<span>{entry_time}</span>'
                        f'<span>{entry["throughput"]:.3f} Mbps '
                        f'({entry["deviation"]:+.1f}%)</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )


# ==================================================
# Recent Measurements
# ==================================================

with st.container(
    border=True,
    key="recent_measurements_card"
):

    card_header("📋", "Recent Measurements", "#a78bfa")

    st.markdown(
        '<div class="stat-sub" style="margin-bottom:0.6rem;">'
        'Latest 10 measurement intervals'
        '</div>',
        unsafe_allow_html=True
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


    # Short time format
    recent_data["timestamp"] = (
        recent_data["timestamp"]
        .dt.strftime(
            "%m/%d %I:%M:%S %p"
        )
    )


    # Readable traffic volume
    recent_data["total_bytes"] = (
        recent_data["total_bytes"]
        .apply(format_bytes)
    )


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
                "Traffic",

            "throughput_mbps":
                "Throughput (Mbps)"
        }
    )


    st.dataframe(
        recent_data,
        use_container_width=True,
        hide_index=True
    )