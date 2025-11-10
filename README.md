Here is the updated `README.md` for your project.

It now includes the **Suricata security engine**, the **new alert pipeline**, and the **API endpoints** section, reflecting the 6-terminal setup we built.

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

-----

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

-----

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

# Tab 3 (NEW): Process and store security alerts
python manage.py consume_alerts
```

> These consumers read from Kafka and update the PostgreSQL database.

-----

### **Terminal 3: Run the Django ASGI Server**

  * **Directory:** `...\network_api\packet_analyzer`
  * **Action:** Activate your venv.

<!-- end list -->

```bash
daphne -p 8000 packet_analyzer.asgi:application
```

> Do **not** use `runserver`. Daphne is required for WebSocket support.

-----

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

-----

### **Terminal 5: Start Suricata Security Engine**

  * **Access:** Must be **Run as Administrator**.
  * **Directory:** `C:\Program Files\Suricata`

<!-- end list -->

```bash
# Replace with your actual IP address
.\suricata.exe -c suricata.yaml -i 10.228.212.153
```

> This runs the IDS, inspects all traffic against its rules, and writes alerts to `eve.json`.

-----

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

  * **GET `/api/security-alerts/`**

      * Gets the latest security alerts detected by Suricata, 25 per page.
      * **Example:** `http://localhost:8000/api/security-alerts/`
      * **Pagination:** `http://localhost:8000/api/security-alerts/?page=2`

-----

### **Summary**

With this setup, you can:

  * Capture, process, and store all network traffic live.
  * **Perform deep packet inspection (DPI) using Suricata to detect threats.**
  * **Feed security alerts into a dedicated Kafka pipeline.**
  * Store both packet metadata and security alerts in PostgreSQL.
  * Stream live packet data via WebSockets.
  * **Expose a full API for a frontend dashboard to visualize network health and security alerts.**