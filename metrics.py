def format_bytes(num_bytes):

    if num_bytes < 1024:
        return f"{num_bytes:.0f} B"

    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.2f} KB"

    else:
        return f"{num_bytes / (1024 * 1024):.2f} MB"


def calculate_metrics(df, duration):

    # -------------------------
    # Basic traffic statistics
    # -------------------------
    total_packets = len(df)

    total_bytes = df["packet_size"].sum()

    throughput_bps = (
        total_bytes * 8
    ) / duration

    throughput_mbps = (
        throughput_bps / 1_000_000
    )

    # -------------------------
    # Protocol percentages
    # -------------------------
    protocol_percent = (
        df["protocol"]
        .value_counts(normalize=True)
        * 100
    ).round(2)

    tcp_percent = protocol_percent.get(
        "TCP", 0
    )

    udp_percent = protocol_percent.get(
        "UDP", 0
    )

    icmp_percent = protocol_percent.get(
        "ICMP", 0
    )

    arp_percent = protocol_percent.get(
        "ARP", 0
    )

    return {

        "total_packets":
            total_packets,

        "total_bytes":
            total_bytes,

        "throughput_mbps":
            throughput_mbps,

        "tcp_percent":
            tcp_percent,

        "udp_percent":
            udp_percent,

        "icmp_percent":
            icmp_percent,

        "arp_percent":
            arp_percent
    }