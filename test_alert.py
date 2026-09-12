from monitoring import compare_with_baseline


baseline = 1.0
current = 2.0

status, threshold = compare_with_baseline(
    current,
    baseline
)

print("Baseline:", baseline, "Mbps")
print("Threshold:", threshold, "Mbps")
print("Current:", current, "Mbps")
print("Status:", status)