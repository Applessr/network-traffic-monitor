# Network Traffic Analyzer and Performance Monitoring Dashboard

A Python-based network traffic monitoring application that passively captures and analyzes network packets, calculates traffic metrics, stores historical measurements, compares current throughput with a recent baseline, and provides automatic alerts through an interactive Streamlit dashboard.

**Course:** Computer Networking  
**Assignment:** Assignment #3 — Network Tool / Application / Simulation Project  
**Development Environment:** macOS + VS Code  
**Primary Interface:** `en0`  
**Measurement Interval:** 10 seconds  

---

## 1. Project Overview

The **Network Traffic Analyzer and Performance Monitoring Dashboard** is a lightweight network monitoring application developed in Python.

The system captures network traffic from a selected network interface using **Scapy**, analyzes packet-level information, calculates traffic metrics, stores measurement results over time, compares the current throughput with a recent baseline, and presents the results through an interactive **Streamlit + Plotly dashboard**.

The project is designed as a **focused monitoring workflow**, not as a replacement for comprehensive packet-analysis tools such as Wireshark.

### Core monitoring workflow

```text
Capture → Analyze → Measure → Store History → Compare → Alert → Visualize
```

### Main capabilities

- Passive packet capture using Scapy
- Packet-level analysis
- Traffic volume measurement
- Throughput measurement
- Protocol distribution
- Historical traffic monitoring
- Baseline comparison
- Automatic NORMAL / WARNING status
- Toast notification on NORMAL → WARNING transition
- Interactive Streamlit dashboard
- Controlled throughput validation using iPerf3

---

## 2. Problem and Motivation

Raw packet captures contain detailed information, but packet-level data alone is not a convenient way to monitor traffic continuously.

A user may want to know:

1. How much traffic is currently observed?
2. What is the current observed throughput?
3. How is traffic distributed across protocols?
4. How has traffic changed over time?
5. Is the current throughput unusually high compared with recent traffic?

The project addresses this by transforming packet observations into a continuous monitoring workflow with historical context and a simple, explainable alert rule.

### Project positioning

The project does **not** claim that Wireshark lacks packet capture, statistics, or visualization. Instead, it focuses on integrating passive measurement, historical storage, baseline comparison, and automatic alerting into one small dashboard-oriented application suitable for a course project.

---

## 3. Final Objectives and Scope

### 3.1 Objectives

- Capture packets from a selected interface using Scapy.
- Extract timestamp, source, destination, protocol, and packet size.
- Calculate traffic volume and observed throughput.
- Calculate protocol distribution from captured packet counts.
- Store measurements and visualize traffic trends over time.
- Compare current throughput with the previous 10 measurement intervals.
- Generate NORMAL / WARNING status using a configurable monitoring rule implemented in the prototype.
- Present the results through an interactive dashboard.

### 3.2 Final In-Scope Features

| Feature | Status |
|---|---|
| Packet Capture | Implemented |
| Packet Analysis | Implemented |
| Traffic Volume | Implemented |
| Throughput | Implemented |
| Protocol Distribution | Implemented |
| Historical Trend | Implemented |
| Baseline Comparison | Implemented |
| Automatic Alert | Implemented |
| Streamlit Dashboard | Implemented |
| Dashboard Auto-refresh | Implemented |
| iPerf3 Throughput Validation | Implemented |

### 3.3 Out of Scope

| Feature | Decision | Reason |
|---|---|---|
| Latency measurement | Removed | The final project uses passive monitoring and does not define an endpoint-to-endpoint latency measurement method. |
| Packet loss measurement | Removed | Removed with active ICMP performance probing. |
| Network Health Score | Not included | Would require additional scoring assumptions and weighting methodology. |
| Deep intrusion detection / ML classification | Not included | Outside the final monitoring-focused scope. |

**Important:** ICMP may still appear as a protocol category during packet classification, but ICMP is **not** used to measure latency or packet loss.

---

## 4. System Architecture

```text
Network Traffic
      ↓
Packet Capture
   (Scapy)
      ↓
Packet Analysis
      ↓
┌─────────────────────────────┐
│ Traffic Volume              │
│ Throughput                  │
│ Protocol Distribution       │
└─────────────────────────────┘
      ↓
Historical Data
      ↓
Baseline Comparison
      ↓
Automatic Alert
      ↓
Streamlit Dashboard
      ↓
Charts + Statistics + Alerts + Trends
```

### 4.1 End-to-End Workflow

1. Network traffic is captured from the selected interface (`en0`) using Scapy `AsyncSniffer`.
2. The system captures traffic for a fixed **10-second measurement interval**.
3. Each packet is analyzed to extract timestamp, source, destination, protocol, and packet size.
4. Packet timestamps are converted to **Asia/Bangkok** time for consistent display.
5. The system calculates packet count, traffic volume, throughput, and protocol distribution.
6. One measurement record is appended to `historical_data.csv`.
7. The current throughput is compared with the average throughput of the previous 10 measurement intervals.
8. The warning threshold is calculated as `baseline × 1.5`.
9. If current throughput is greater than the threshold, the status becomes `WARNING`; otherwise it remains `NORMAL`.
10. The dashboard displays the current state, historical trend, baseline comparison, and alert information.

### 4.2 Data Flow

| Input | Processing | Output |
|---|---|---|
| Network packets | Scapy capture + packet parsing | Structured packet records |
| Packet records | Pandas aggregation | Traffic metrics |
| Metrics | CSV storage | Historical measurements |
| Historical measurements | Baseline calculation + threshold rule | NORMAL / WARNING |
| Stored data + current state | Streamlit + Plotly | Interactive dashboard |

---

## 5. Main Features and Measurement Definitions

### 5.1 Packet Capture

- Library: **Scapy**
- Interface used in the current prototype: `en0`
- Capture mode: passive sniffing
- Measurement interval: **10 seconds**
- macOS packet capture may require administrator/root privileges.

### 5.2 Packet Analysis

The analyzer extracts:

| Field | Description |
|---|---|
| `timestamp` | Packet capture timestamp, converted to Asia/Bangkok time |
| `source_ip` | IPv4, IPv6, or ARP source address when available |
| `destination_ip` | IPv4, IPv6, or ARP destination address when available |
| `protocol` | TCP, UDP, ICMP, ARP, or Other based on observed layers |
| `packet_size` | Length of the captured packet in bytes |

### 5.3 Traffic Volume

**Definition:** Total bytes observed during one measurement interval.

Example dashboard value:

```text
Traffic Volume = 13.57 MB
```

### 5.4 Throughput

The prototype calculates observed throughput as:

```text
Throughput (Mbps) = (Total Bytes × 8) ÷ Measurement Time ÷ 1,000,000
```

Example:

```text
Total Bytes     → observed during the 10-second interval
Measurement Time → 10 seconds
Output           → Mbps
```

**Important:** This is the throughput observed on the selected interface during the measurement period. It is not presented as the maximum Internet connection speed.

### 5.5 Protocol Distribution

Protocol distribution is based on **captured packet counts**, not byte volume.

```text
Protocol % = Protocol Packet Count ÷ Total Packet Count × 100
```

Example:

```text
UDP 99.9%
TCP  0.1%
ARP  0.0%
```

---

## 6. Historical Monitoring

Each 10-second measurement is saved as one historical record in:

```text
historical_data.csv
```

The dashboard uses these stored measurements to create an interactive throughput trend chart.

### Available time ranges

- Last 1 Hour
- Last 6 Hours
- Last 24 Hours
- All Data

Historical data is important for two reasons:

1. It shows traffic behavior over time, including rises and spikes.
2. It provides the recent measurements needed to calculate the baseline.

---

## 7. Baseline Comparison and Alert Logic

### 7.1 Baseline Definition

For a new measurement, the baseline is the **average throughput of the previous 10 measurement intervals**.

```text
Baseline = Average(Previous 10 Throughput Measurements)
```

The **current measurement is excluded** from the baseline calculation.

> The baseline is based on **10 previous measurement intervals**, not 10 packets.

### 7.2 Warning Threshold

The current prototype uses:

```text
Warning Threshold = Baseline × 1.5
```

The 1.5 multiplier is a **prototype design choice** for detecting a significant increase in observed traffic. It is not claimed to be a universal networking standard.

### 7.3 Status Rule

```text
IF Current Throughput > Warning Threshold
    → WARNING
ELSE
    → NORMAL
```

### 7.4 Deviation

The dashboard also displays the relative deviation from the baseline:

```text
Deviation (%) = (Current - Baseline) ÷ Baseline × 100
```

### 7.5 Automatic Notification

The dashboard displays:

- NORMAL status when traffic is within the configured range
- WARNING status when the threshold is exceeded
- A toast notification when the status changes from NORMAL to WARNING

The alert logic is intentionally simple and explainable for the prototype.

### Example WARNING condition

```text
Current Throughput = 5.292 Mbps
Baseline           = 0.778 Mbps
Warning Threshold  = 1.167 Mbps
Deviation          = +579.92%
Status             = WARNING
```

---

## 8. Dashboard

The final dashboard combines the monitoring outputs into a single interface.

### Dashboard sections

#### Current Status

Shows the current overall monitoring state:

```text
NORMAL
```

or

```text
WARNING
```

#### KPI Cards

Shows current:

- Traffic Volume
- Throughput
- Packet count / current measurement information
- Protocol distribution

#### Historical Network Throughput

Interactive Plotly line chart showing throughput changes over time.

#### Baseline Comparison

Shows:

- Current throughput
- Baseline
- Warning threshold
- Deviation
- NORMAL / WARNING state

#### Alerts

Shows the current alert state, latest check, and recent alert information without replacing the baseline-comparison explanation.

#### Recent Measurements

Shows the latest stored measurement intervals and their packet counts, traffic volumes, and throughput values.

### Dashboard behavior

- Auto-refresh: every **10 seconds**
- Data source: `historical_data.csv`
- Visualization: Plotly
- UI framework: Streamlit

---

## 9. Project Structure

### Current final structure

```text
network-monitor/
├── analysis.py
├── metrics.py
├── storage.py
├── monitoring.py
├── monitor.py
├── dashboard.py
├── test_alert.py
├── README.md
├── requirements.txt
├── .gitignore
├── evidence/
└── historical_data.csv
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `analysis.py` | Analyzes each captured packet and extracts structured packet information. |
| `metrics.py` | Calculates packet count, total bytes, throughput, protocol percentages, and byte formatting. |
| `storage.py` | Appends measurement results to `historical_data.csv`. |
| `monitoring.py` | Calculates baseline, warning threshold, deviation, and alert status. |
| `monitor.py` | Runs continuous 10-second packet capture, analysis, metric calculation, and storage. |
| `dashboard.py` | Reads historical data and displays the interactive Streamlit + Plotly dashboard. |
| `test_alert.py` | Tests alert-rule behavior separately from production historical data. |
| `README.md` | Quick-start and repository documentation. |
| `requirements.txt` | Python dependency list. |
| `.gitignore` | Prevents local environment/cache/sensitive data from being committed. |
| `evidence/` | Screenshots and evaluation evidence. |
| `historical_data.csv` | Locally generated historical measurements. Should normally remain uncommitted. |

**Removed from the final structure:** `historical_chart.py`. The dashboard now creates the historical Plotly chart directly in `dashboard.py`.

---

## 10. Technologies and Development Environment

| Component | Technology / Setup |
|---|---|
| Language | Python |
| Packet capture | Scapy |
| Data processing | Pandas |
| Visualization | Plotly |
| Dashboard | Streamlit |
| Auto-refresh | `streamlit-autorefresh` |
| Throughput validation | iPerf3 |
| IDE | Visual Studio Code |
| Python environment | `.venv` virtual environment |
| Development OS | macOS |
| Capture interface | `en0` |

---

## 11. Installation and Setup

### 11.1 Clone the Repository

```bash
git clone https://github.com/Applessr/network-traffic-monitor.git
cd network-traffic-monitor
```

### 11.2 Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 11.3 Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### 11.4 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 11.5 Install iPerf3 for Validation

On macOS with Homebrew:

```bash
brew install iperf3
```

Check the installation:

```bash
iperf3 --version
```

---

## 12. Running the System

### 12.1 Start the Network Monitor

Open a terminal in the project folder and run:

```bash
sudo .venv/bin/python monitor.py
```

The monitor will:

1. Capture packets on `en0`.
2. Run a 10-second measurement interval.
3. Analyze the captured packets.
4. Calculate traffic metrics.
5. Save one historical measurement.
6. Repeat until `Ctrl+C` is pressed.

Example output:

```text
================================
Network Traffic Monitor
================================
Interface: en0
Measurement interval: 10 seconds
Press Ctrl+C to stop.

Measurement Result:
Packets: 4990
Traffic: 6.01 MB
Throughput: 5.04 Mbps
TCP: 98.02%
UDP: 1.76%
ICMP: 0.00%
ARP: 0.04%
Saved to historical_data.csv
```

### 12.2 Start the Dashboard

Open another terminal:

```bash
source .venv/bin/activate
streamlit run dashboard.py
```

The dashboard runs locally and automatically refreshes every 10 seconds.

---

## 13. Throughput Validation with iPerf3

The throughput calculation is validated with controlled iPerf3 traffic.

### 13.1 Test Topology

```text
Mac
Analyzer + iPerf3 Client
        │
        │  Controlled TCP traffic
        │
        ▼
Windows Notebook
 iPerf3 Server
```

During the test, the Mac simultaneously runs the analyzer and captures traffic on `en0`.

### 13.2 Start the iPerf3 Server

On the Windows notebook:

```bash
iperf3 -s
```

The default server port is:

```text
5201
```

### 13.3 Run the iPerf3 Client

On the Mac:

```bash
iperf3 -c 192.168.1.11 -b 5M -t 10
```

Meaning:

- `-c 192.168.1.11` — connect to the Windows iPerf3 server.
- `-b 5M` — target approximately 5 Mbps.
- `-t 10` — run for 10 seconds.

The final successful comparison runs used an iPerf3 reference of approximately **5.03 Mbps**.

### 13.4 Paired Validation Results

| Test | iPerf3 Reference | Analyzer | Difference |
|---|---:|---:|---:|
| 1 | 5.03 Mbps | 5.09 Mbps | 1.19% |
| 2 | 5.03 Mbps | 5.18 Mbps | 2.98% |
| 3 | 5.03 Mbps | 5.20 Mbps | 3.38% |
| **Average** | **5.03 Mbps** | **5.16 Mbps** | **2.52%** |

The average absolute percentage difference across these three paired runs was **2.52%**.

This is presented as a **throughput comparison / validation result**, not as an absolute system accuracy score.

### 13.5 Why the Values Are Not Exactly Equal

Small differences are expected because:

- The analyzer observes all traffic visible on the selected interface.
- Background traffic may be present.
- The analyzer and iPerf3 may use slightly different start/end timing for their reported intervals.

---

## 14. Evaluation

### 14.1 Functional Evaluation

| Test Case | Expected Result | Status |
|---|---|---|
| Packet Capture | Packets are captured successfully | PASS |
| Packet Analysis | Timestamp, source/destination, protocol, and packet size are extracted | PASS |
| Traffic Volume | Total observed bytes are calculated | PASS |
| Throughput | Throughput is calculated from captured traffic | PASS |
| Protocol Distribution | Protocol percentages are displayed | PASS |
| Historical Monitoring | Measurements are stored and visualized over time | PASS |
| Baseline Comparison | Current traffic is compared with recent historical traffic | PASS |
| Automatic Alert | NORMAL / WARNING status is generated according to the rule | PASS |
| Dashboard | Results are displayed interactively | PASS |
| Dashboard Auto-refresh | New measurements appear after refresh cycle | PASS |
| iPerf3 Validation | Measured throughput is compared with controlled traffic | PASS |

### 14.2 Baseline / Alert Functional Examples

| Scenario | Current | Baseline | Threshold | Deviation | Result |
|---|---:|---:|---:|---:|---|
| Normal traffic | 0.295 Mbps | 1.291 Mbps | 1.936 Mbps | -77.15% | NORMAL |
| High traffic | 5.292 Mbps | 0.778 Mbps | 1.167 Mbps | +579.92% | WARNING |

These examples demonstrate the intended baseline rule: a lower current value remains NORMAL, while a sufficiently higher value exceeds the threshold and generates WARNING.

### 14.3 Historical Trend Observation

During controlled testing, throughput spikes were visible in the historical chart around iPerf3 activity. Example high-traffic analyzer measurements included approximately **5.09, 5.18, and 5.20 Mbps**, while nearby non-test periods were substantially lower.

---

## 15. Discussion

### 15.1 What the Final System Demonstrates

- The packet capture pipeline can continuously observe traffic and produce structured records.
- The system can calculate traffic volume and observed throughput from captured packets.
- Protocol distribution can be summarized from packet classifications.
- Historical storage provides context that a single current measurement cannot provide.
- The baseline rule provides a simple way to distinguish higher current traffic from recent lower traffic.
- The automatic alert converts the comparison into an easy-to-understand NORMAL / WARNING status.
- The dashboard combines current values, historical context, baseline information, and alerts in one interface.

### 15.2 Interpretation of the Validation Result

The three paired iPerf3 comparisons show close practical agreement under the tested conditions, with an average absolute difference of 2.52%.

This should not be interpreted as a universal accuracy claim because the selected interface can contain additional traffic and the measurement timing of the analyzer and reference tool can differ.

### 15.3 Why the Historical Baseline Is Useful

A current throughput value has limited meaning without context. The recent baseline provides a simple reference based on the previous ten measurement intervals rather than a fixed Internet-speed assumption or a single manually selected value.

---

## 16. Limitations and Risks

| Limitation | Impact / Handling |
|---|---|
| Observed-interface measurement | The system reports traffic observed on the selected interface, not maximum Internet speed. |
| Background traffic | Non-test traffic on the interface may affect measured throughput. |
| Baseline sensitivity | A baseline based on the previous 10 measurements can change as traffic conditions change. |
| Threshold design | The 1.5× multiplier is a prototype rule, not a universal network standard. |
| Single-interface prototype | The current prototype is configured for `en0`. |
| CSV storage | CSV is sufficient for the course prototype but is not intended for large-scale historical storage. |
| Capture privileges | macOS packet capture may require administrator/root privileges. |
| Security/privacy | Historical packet metadata may contain IP addresses or other network information. |
| Not an IDS | The system is a monitoring and alerting prototype, not a full intrusion-detection system. |
| Passive monitoring only | The final project does not measure latency or packet loss. |

---

## 17. Security and Privacy

The application should only be used on networks where packet capture is authorized.

The generated `historical_data.csv` may contain observed network addresses and other network metadata. For that reason:

- Review the file before sharing it.
- Do not commit private historical data to a public repository.
- Keep `historical_data.csv` in `.gitignore` for normal development.
- Use sanitized screenshots or sample values when publishing project materials.

---

## 18. Demonstration Flow

The recommended final demo follows the actual system behavior:

```text
1. Start Network Monitor
        ↓
2. Open Dashboard
        ↓
3. Show NORMAL status
        ↓
4. Start iPerf3 controlled traffic (~5 Mbps)
        ↓
5. Throughput increases
        ↓
6. Historical graph shows the spike
        ↓
7. Current throughput exceeds the baseline threshold
        ↓
8. Dashboard changes to WARNING
        ↓
9. Toast notification appears
        ↓
10. Stop iPerf3
        ↓
11. Traffic decreases
        ↓
12. Dashboard returns toward NORMAL
```

### Recommended demo commands

**Terminal 1 — Monitor:**

```bash
sudo .venv/bin/python monitor.py
```

**Terminal 2 — Dashboard:**

```bash
streamlit run dashboard.py
```

**Windows — iPerf3 server:**

```bash
iperf3 -s
```

**Mac — iPerf3 client:**

```bash
iperf3 -c 192.168.1.11 -b 5M -t 10
```

The demo story should emphasize the relationship between **traffic generation → packet capture → throughput change → baseline comparison → WARNING**.

---

## 19. Key Facts for PPT and Poster

| Item | Final Project Information |
|---|---|
| Project title | Network Traffic Analyzer and Performance Monitoring Dashboard |
| Goal | Automated passive network traffic monitoring with history, baseline comparison, and alerting |
| Capture method | Scapy passive packet capture |
| Interface | `en0` on the current Mac prototype |
| Measurement interval | 10 seconds |
| Main metrics | Traffic volume, throughput, protocol distribution |
| Historical storage | `historical_data.csv` |
| Baseline | Average throughput of previous 10 measurement intervals |
| Warning threshold | `1.5 × baseline` |
| Status | NORMAL / WARNING |
| Notification | Dashboard status + toast on NORMAL → WARNING transition |
| Dashboard | Streamlit + Plotly |
| Validation tool | iPerf3 |
| Controlled target | Approximately 5 Mbps for 10 seconds |
| Validation reference | 5.03 Mbps in the successful comparison runs |
| Average absolute difference | 2.52% across three paired tests |
| Project positioning | Focused monitoring workflow, not a replacement for Wireshark |
| Final scope excludes | Latency measurement, packet-loss measurement, deep IDS/ML |

### Poster-ready summary

**Problem:** Raw packet data is detailed but is not convenient for continuous monitoring and trend interpretation.

**Solution:** A lightweight Python-based system that captures passive traffic, calculates traffic metrics, stores historical measurements, compares current throughput with a recent baseline, and generates a simple alert status.

**Method:**

```text
Scapy Capture
→ Packet Analysis
→ Traffic Metrics
→ Historical Storage
→ Baseline Comparison
→ Alert
→ Streamlit Dashboard
```

**Key rule:**

```text
Baseline = Average of Previous 10 Throughput Measurements
Warning = Current Throughput > 1.5 × Baseline
```

**Validation:** Controlled iPerf3 traffic was compared with analyzer throughput across three paired tests; the average absolute difference was 2.52%.

**Main output:** A dashboard showing current traffic, throughput, protocol distribution, historical trend, baseline comparison, alerts, and recent measurements.

---

## 20. Current Development Status

### Implemented and Tested

- [x] Packet Capture
- [x] Packet Analysis
- [x] Traffic Volume
- [x] Throughput
- [x] Protocol Distribution
- [x] Historical Data Storage
- [x] Historical Throughput Chart
- [x] Historical Time Range Selection
- [x] Baseline Comparison
- [x] Automatic Alert
- [x] Streamlit Dashboard
- [x] Dashboard Auto-refresh
- [x] iPerf3 Throughput Validation
- [x] Final dashboard states: NORMAL and WARNING
- [x] Evaluation evidence and results
- [x] Final presentation structure / draft

### Remaining Team Work

- [ ] Final poster
- [ ] Final demo video / editing
- [ ] Final live-demo rehearsal
- [ ] Final repository cleanup and submission check

---

## 21. References and Project Resources

### Technical References

1. Wireshark Foundation, *Wireshark: Network Protocol Analyzer*.
2. Scapy Project, *Scapy — Packet Manipulation Tool*.
3. ntop, *ntopng — High-Speed Web-based Traffic Analysis and Flow Collection*.
4. Houkan et al., “Enhancing Security in Industrial IoT Networks: Machine Learning Solutions for Feature Selection and Reduction,” *IEEE Access*, vol. 12, 2024, doi: 10.1109/ACCESS.2024.3481459.

### Project Resources

**GitHub Repository**  
https://github.com/Applessr/network-traffic-monitor.git

**Shared Documentation**  
https://docs.google.com/document/d/1lip-34QIesPaNIVZUiyP8P10Ryaml9FQYlPXHn-HzXI/edit?usp=sharing

