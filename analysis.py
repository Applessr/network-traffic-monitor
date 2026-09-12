import pandas as pd

from scapy.all import (
    sniff,
    IP,
    IPv6,
    ARP,
    TCP,
    UDP,
    ICMP
)

from metrics import calculate_metrics, format_bytes
from storage import save_measurement


INTERFACE = "en0"
CAPTURE_DURATION = 10


def analyze_packet(packet):

    # -------------------------
    # Timestamp
    # -------------------------
    timestamp = packet.time

    # -------------------------
    # Source / Destination IP
    # -------------------------
    if packet.haslayer(IP):
        source = packet[IP].src
        destination = packet[IP].dst

    elif packet.haslayer(IPv6):
        source = packet[IPv6].src
        destination = packet[IPv6].dst

    elif packet.haslayer(ARP):
        source = packet[ARP].psrc
        destination = packet[ARP].pdst

    else:
        source = ""
        destination = ""

    # -------------------------
    # Protocol
    # -------------------------
    if packet.haslayer(TCP):
        protocol = "TCP"

    elif packet.haslayer(UDP):
        protocol = "UDP"

    elif packet.haslayer(ICMP):
        protocol = "ICMP"

    elif packet.haslayer(ARP):
        protocol = "ARP"

    else:
        protocol = "Other"

    # -------------------------
    # Packet Size
    # -------------------------
    packet_size = len(packet)

    return {
        "timestamp": timestamp,
        "source_ip": source,
        "destination_ip": destination,
        "protocol": protocol,
        "packet_size": packet_size
    }


def main():

    print("================================")
    print("Network Traffic Analyzer")
    print("================================")

    print(f"Interface: {INTERFACE}")
    print(f"Capture duration: {CAPTURE_DURATION} seconds")
    print()

    # -------------------------
    # Capture packets
    # -------------------------
    packets = sniff(
        iface=INTERFACE,
        timeout=CAPTURE_DURATION
    )

    print("Capture complete.")
    print()

    # -------------------------
    # Analyze packets
    # -------------------------
    records = []

    for packet in packets:

        data = analyze_packet(packet)
        records.append(data)

    # -------------------------
    # Create DataFrame
    # -------------------------
    df = pd.DataFrame(records)

    # Check if packets were captured
    if df.empty:

        print("No packets were captured.")

        return

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="s",
        utc=True
    ).dt.tz_convert("Asia/Bangkok")

    # -------------------------
    # Packet Analysis Result
    # -------------------------
    print("Packet Analysis Result:")
    print(df)

    print()

    # -------------------------
    # Protocol Distribution
    # -------------------------
    print("Protocol Distribution:")

    protocol_counts = (
        df["protocol"]
        .value_counts()
    )

    protocol_percent = (
        df["protocol"]
        .value_counts(normalize=True)
        * 100
    ).round(2)

    print(protocol_counts)
    print()
    print(protocol_percent)

    # -------------------------
    # Calculate Metrics
    # -------------------------
    metrics = calculate_metrics(
        df,
        CAPTURE_DURATION
    )

    print()
    print("Traffic Statistics:")

    print(
        "Total packets:",
        metrics["total_packets"]
    )

    print(
        "Total traffic:",
        format_bytes(metrics["total_bytes"])
    )

    print(
        f"Throughput: "
        f"{metrics['throughput_mbps']:.3f} Mbps"
    )

    # -------------------------
    # Create Historical Record
    # -------------------------
    measurement_time = df["timestamp"].min()

    measurement = {

        "timestamp": measurement_time,

        "total_packets":
            metrics["total_packets"],

        "total_bytes":
            metrics["total_bytes"],

        "throughput_mbps":
            metrics["throughput_mbps"]
    }

    # -------------------------
    # Save Historical Data
    # -------------------------
    save_measurement(measurement)

    print()
    print("Historical measurement saved.")
    print("File: historical_data.csv")


if __name__ == "__main__":
    main()