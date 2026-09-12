import pandas as pd
import plotly.express as px


HISTORICAL_FILE = "historical_data.csv"


def main():

    # -------------------------
    # Load historical data
    # -------------------------
    df = pd.read_csv(
        HISTORICAL_FILE
    )

    if df.empty:
        print("No historical data found.")
        return

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # ==================================================
    # 1. Historical Throughput
    # ==================================================

    throughput_fig = px.line(
        df,
        x="timestamp",
        y="throughput_mbps",
        markers=True,
        title="Historical Network Throughput"
    )

    throughput_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Throughput (Mbps)"
    )

    throughput_fig.write_html(
        "historical_throughput.html"
    )

    # ==================================================
    # 2. Current Protocol Distribution
    # ==================================================

    latest = df.iloc[-1]

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

    protocol_fig = px.bar(
        protocol_data,
        x="Protocol",
        y="Percentage",
        text="Percentage",
        title="Current Protocol Distribution"
    )

    protocol_fig.update_layout(
        xaxis_title="Protocol",
        yaxis_title="Percentage (%)"
    )

    protocol_fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    protocol_fig.write_html(
        "protocol_distribution.html"
    )

    print("Charts created:")
    print("- historical_throughput.html")
    print("- protocol_distribution.html")


if __name__ == "__main__":
    main()