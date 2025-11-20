Here is the updated `README.md`. I have updated the **API Endpoints** section to include the specific filters for Threats and Policy Violations, and added a new **Verification & Testing** section with the commands we know work on your Windows setup.

-----

# CyberSecurityBackend

A Django-based backend for real-time network packet capture and analysis. It uses Suricata for deep packet inspection (DPI) and a Kafka pipeline (PostgreSQL, Redis, Django Channels) to process, store, and stream both network metadata and security alerts.

-----

## Prerequisites

Before running the project, ensure you have the following installed:

  * Docker & Docker Compose
  * Python 3.10+
  * Virtual Environment (`venv`)
  * **Suricata** (IDS/IPS Engine)
  * Kafka (Handled by Docker Compose)
  * PostgreSQL (Handled by Docker Compose)
  * Redis

-----

## Setup and Run

This project requires a distributed setup of **six separate terminal windows** running simultaneously. Four of these terminals must be **Run as Administrator** to capture packets and access system logs.

### **Terminal 1: Start Infrastructure (Docker)**

Start the core services (PostgreSQL, Kafka, Zookeeper):

```bash
# Navigate to the project root (where docker-compose.yml is)
cd C:\Users\Dell\Desktop\Basic Project\CS_PROJECT\network_api

# Start services
docker-compose up -d
```

In a separate tab, start the Redis server for Django Channels:

```bash
docker run -p 6380:6379 -d redis:7
```

### **Terminal 2: Start Backend Consumers**

  * **Directory:** `...\network_api\packet_analyzer`
  * **Action:** Activate your venv (`.\venv\Scripts\activate`)
  * **Note:** Run each command in a **separate tab**.

<!-- end list -->

```bash
# Tab 1: Process and store packet metadata
python manage.py consume_db

# Tab 2: Process and stream live packets to WebSocket
python manage.py consume_live

# Tab 3: Process and store security alerts (IDS)
python manage.py consume_alerts
```

> These consumers read from Kafka and update the PostgreSQL database.

### **Terminal 3: Run the Django ASGI Server**

  * **Directory:** `...\network_api\packet_analyzer`
  * **Action:** Activate your venv.

<!-- end list -->

```bash
daphne -p 8000 packet_analyzer.asgi:application
```

> Do **not** use `runserver`. Daphne is required for WebSocket support.

### **Terminal 4: Run the Packet Sniffer (Producer)**

  * **Access:** Must be **Run as Administrator**.
  * **Directory:** `...\network_api` (Project Root)
  * **Action:** Activate your venv (`.\packet_analyzer\venv\Scripts\activate`)

<!-- end list -->

```bash
# Replace <your_interface> with the name from "ipconfig" (e.g., "Wi-Fi")
sudo python packet_sniffer.py "<your_interface>"
```

> This produces raw packet metadata to the `packet_data` Kafka topic.

### **Terminal 5: Start Suricata Security Engine**

  * **Access:** Must be **Run as Administrator**.
  * **Directory:** `C:\Program Files\Suricata`

<!-- end list -->

```bash
# Replace with your actual IP address
.\suricata.exe -c suricata.yaml -i 10.228.212.153
```

> This runs the IDS, inspects all traffic against its rules, and writes alerts to `eve.json`.

### **Terminal 6: Run the Alert Producer**

  * **Access:** Must be **Run as Administrator**.
  * **Directory:** `...\network_api` (Project Root)
  * **Action:** Activate your venv (`.\packet_analyzer\venv\Scripts\activate`)

<!-- end list -->

```bash
# This script "tails" the eve.json log and produces alerts to Kafka
python alert_producer.py
```

> This script reads Suricata's `eve.json` log file in real-time and produces new alerts to the `security_alerts` Kafka topic.

-----

## 📡 Accessing Data

### Live Packet Feed (WebSocket)

Connect any WebSocket client to this endpoint to see a live JSON feed of network packets (sourced from `consume_live`).

`ws://localhost:8000/ws/live-packets/`

### API Endpoints (HTTP)

Your frontend can fetch aggregated data and alerts from these REST API endpoints.

  * **GET `/api/top-talkers/<minutes>/`**

      * Gets a list of the top 100 most active source IPs over the last `X` minutes.
      * **Example:** `http://localhost:8000/api/top-talkers/60/`

  * **POST `/api/ip-health/`**

      * Performs a live ping test on a given IP address.
      * **Body:** `{ "ip_address": "8.8.8.8" }`

  * **GET `/api/security-alerts/` (Master Log)**

      * Gets all alerts detected by Suricata mixed together.

  * **GET `/api/security-alerts/?type=threat` (High Severity)**

      * Fetches only **Critical Threats** (Malware, SQL Injection, Attacks).
      * **Use Case:** For the "Threats Detected" widget (Red Alerts).

  * **GET `/api/security-alerts/?type=policy` (Low Severity)**

      * Fetches only **Policy Violations** (VPNs, Gaming, P2P, Blocked Sites).
      * **Use Case:** For the "Policy Violations" widget (Yellow/Green Alerts).

-----

## 🧪 Verification & Testing

To ensure the system is working, run these commands in **PowerShell** to trigger specific alerts.

### 1\. Test Threat Detection (Severity: High)

These commands simulate malicious attacks. They should appear in the **Threats Detected** widget.

**Simulate SQL Injection / Root Access Attempt:**

```powershell
curl.exe "http://testmynids.org/uid=0(root)"
```

  * **Result:** Alert `GPL ATTACK_RESPONSE id check returned root`

**Simulate Malware Communication (BlackSun User-Agent):**

```powershell
curl.exe -A "BlackSun" http://google.com
```

  * **Result:** Alert `THREAT DETECTED: Known Malware User-Agent (BlackSun)`

### 2\. Test Policy Violations (Severity: Low/Medium)

These commands simulate unwanted but non-malicious traffic. They should appear in the **Policy Violations** widget.

**Simulate Discord Usage:**

```powershell
nslookup discord.com
```

  * **Result:** Alert `POLICY VIOLATION: Discord DNS Lookup`

**Simulate Manual Policy Test:**

```powershell
curl.exe http://test.com/policy-test
```

  * **Result:** Alert `POLICY TEST: Manual Trigger`

**Simulate OpenVPN (Port Check):**

```powershell
# Requires Netcat (nc) or similar tool, or just attempting to connect via VPN client
# This checks UDP port 1194
```

  * **Result:** Alert `POLICY VIOLATION: OpenVPN Port 1194 Traffic`

-----

### **Summary**

With this setup, you can:

  * Capture, process, and store all network traffic live.
  * **Perform deep packet inspection (DPI) using Suricata to detect threats.**
  * **Feed security alerts into a dedicated Kafka pipeline.**
  * Store both packet metadata and security alerts in PostgreSQL.
  * Stream live packet data via WebSockets.
  * **Expose a filtered API to distinguish between high-priority Threats and internal Policy Violations.**