from monitoring import compare_with_baseline


# Test values
baseline = 1.0
current = 2.0


# Compare current traffic with baseline
status, threshold = compare_with_baseline(
    current,
    baseline
)


# Display test result
print("Baseline:", baseline, "Mbps")
print("Threshold:", threshold, "Mbps")
print("Current:", current, "Mbps")
print("Status:", status)