import pandas as pd


HISTORICAL_FILE = "historical_data.csv"

BASELINE_WINDOW = 10
WARNING_MULTIPLIER = 1.5


def load_historical_data():

    df = pd.read_csv(
        HISTORICAL_FILE
    )

    if df.empty:
        raise ValueError(
            "Historical data is empty."
        )

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # Make sure data is sorted by time
    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    return df


def calculate_baseline(df):

    # If there is only one measurement,
    # use that measurement as the initial baseline.
    if len(df) <= 1:

        return df["throughput_mbps"].mean()

    # Use previous measurements only.
    # Exclude the latest measurement.
    start_index = max(
        0,
        len(df) - BASELINE_WINDOW - 1
    )

    end_index = len(df) - 1

    previous_data = df.iloc[
        start_index:end_index
    ]

    baseline = (
        previous_data["throughput_mbps"]
        .mean()
    )

    return baseline


def compare_with_baseline(
    current_throughput,
    baseline
):

    warning_threshold = (
        baseline * WARNING_MULTIPLIER
    )

    if current_throughput > warning_threshold:

        status = "WARNING"

    else:

        status = "NORMAL"

    return status, warning_threshold


def calculate_deviation(
    current_throughput,
    baseline
):

    if baseline == 0:

        return 0

    deviation = (
        (current_throughput - baseline)
        / baseline
    ) * 100

    return deviation


def generate_alert(
    status,
    current_throughput,
    baseline,
    warning_threshold,
    deviation
):

    if status == "WARNING":

        print()
        print("⚠ WARNING")
        print(
            "Current traffic is "
            "above the baseline."
        )

    else:

        print()
        print("✓ NORMAL")
        print(
            "Current traffic is "
            "within the expected range."
        )


def main():

    # -------------------------
    # Load historical data
    # -------------------------
    df = load_historical_data()

    # -------------------------
    # Calculate baseline
    # -------------------------
    baseline = calculate_baseline(df)

    # -------------------------
    # Latest measurement
    # -------------------------
    latest = df.iloc[-1]

    current_throughput = (
        latest["throughput_mbps"]
    )

    current_timestamp = (
        latest["timestamp"]
    )

    # -------------------------
    # Compare
    # -------------------------
    status, warning_threshold = (
        compare_with_baseline(
            current_throughput,
            baseline
        )
    )

    # -------------------------
    # Deviation
    # -------------------------
    deviation = calculate_deviation(
        current_throughput,
        baseline
    )

    # -------------------------
    # Display
    # -------------------------
    print("================================")
    print("Network Traffic Monitoring")
    print("================================")
    print()

    print(
        f"Baseline window: "
        f"Previous {BASELINE_WINDOW} measurements"
    )

    print(
        f"Current time: "
        f"{current_timestamp}"
    )

    print(
        f"Baseline: "
        f"{baseline:.3f} Mbps"
    )

    print(
        f"Warning threshold: "
        f"{warning_threshold:.3f} Mbps"
    )

    print(
        f"Current throughput: "
        f"{current_throughput:.3f} Mbps"
    )

    print(
        f"Deviation: "
        f"{deviation:+.2f}%"
    )

    print(
        f"Status: "
        f"{status}"
    )

    # -------------------------
    # Generate alert
    # -------------------------
    generate_alert(
        status,
        current_throughput,
        baseline,
        warning_threshold,
        deviation
    )


if __name__ == "__main__":
    main()