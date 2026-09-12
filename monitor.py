import signal
import time
import pandas as pd

from scapy.all import AsyncSniffer

from analysis import analyze_packet
from metrics import calculate_metrics, format_bytes
from storage import save_measurement


INTERFACE = "en0"
CAPTURE_DURATION = 10

stop_requested = False
sniffer = None


def handle_stop(signal_number, frame):

    global stop_requested

    print()
    print("Stopping monitor...")

    stop_requested = True


def capture_measurement():

    global sniffer

    print("--------------------------------")
    print(
        f"Capturing traffic for "
        f"{CAPTURE_DURATION} seconds..."
    )

    # Create asynchronous sniffer
    sniffer = AsyncSniffer(
        iface=INTERFACE
    )

    # Start capturing
    sniffer.start()

    # Wait for the measurement interval
    for _ in range(CAPTURE_DURATION):

        if stop_requested:
            break

        time.sleep(1)

    # Stop the sniffer
    packets = sniffer.stop()

    # Clear sniffer reference
    sniffer = None

    # If user requested stop, do not save
    if stop_requested:

        print("Current measurement was not saved.")

        return

    # -------------------------
    # Analyze packets
    # -------------------------
    records = []

    for packet in packets:

        data = analyze_packet(packet)

        records.append(data)

    # Create DataFrame
    df = pd.DataFrame(records)

    # No packets
    if df.empty:

        print("No packets captured.")

        return

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="s",
        utc=True
    ).dt.tz_convert("Asia/Bangkok")

    # -------------------------
    # Calculate metrics
    # -------------------------
    metrics = calculate_metrics(
        df,
        CAPTURE_DURATION
    )

    # Measurement timestamp
    measurement_time = df["timestamp"].min()

    # Historical record
    measurement = {
        "timestamp": measurement_time,
        "total_packets": metrics["total_packets"],
        "total_bytes": metrics["total_bytes"],
        "throughput_mbps": metrics["throughput_mbps"],
        "tcp_percent": metrics["tcp_percent"],
        "udp_percent": metrics["udp_percent"],
        "icmp_percent": metrics["icmp_percent"],
        "arp_percent": metrics["arp_percent"]
    }

    # Save historical data
    save_measurement(measurement)

    # -------------------------
    # Display result
    # -------------------------
    print()
    print("Measurement Result:")

    print(
        "Packets:",
        metrics["total_packets"]
    )

    print(
        "Traffic:",
        format_bytes(
            metrics["total_bytes"]
        )
    )

    print(
        f"Throughput: "
        f"{metrics['throughput_mbps']:.2f} Mbps"
    )

    print(
        f"TCP: {metrics['tcp_percent']:.2f}%"
    )

    print(
        f"UDP: {metrics['udp_percent']:.2f}%"
    )

    print(
        f"ICMP: {metrics['icmp_percent']:.2f}%"
    )

    print(
        f"ARP: {metrics['arp_percent']:.2f}%"
    )

    print(
        "Saved to historical_data.csv"
    )


def main():

    global stop_requested

    # Register Ctrl+C handler
    signal.signal(
        signal.SIGINT,
        handle_stop
    )

    print("================================")
    print("Network Traffic Monitor")
    print("================================")
    print()

    print(f"Interface: {INTERFACE}")

    print(
        f"Measurement interval: "
        f"{CAPTURE_DURATION} seconds"
    )

    print()

    print("Press Ctrl+C to stop.")
    print()

    while not stop_requested:

        capture_measurement()

        if stop_requested:
            break

        print()
        print("Waiting for next measurement...")
        print()

    print()
    print("================================")
    print("Monitoring stopped.")
    print("Historical data has been saved.")
    print("================================")


if __name__ == "__main__":
    main()