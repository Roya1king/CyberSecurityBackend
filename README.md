# CyberSecurityBackend

### Real-Time Network Packet Capture, DPI (Suricata IDS), Kafka Pipeline, and Security Analytics Dashboard

This project provides a complete cybersecurity monitoring backend built with **Django**, **Kafka**, **PostgreSQL**, **Redis**, and **Suricata IDS**, capable of:

✔ Capturing live network packets  
✔ Performing **Deep Packet Inspection (DPI)**  
✔ Detecting **Threats** and **Policy Violations**  
✔ Streaming live packets via WebSockets  
✔ Storing alerts + traffic logs in PostgreSQL  
✔ Providing REST APIs for dashboards  

---

# 📦 Project Architecture

```
Suricata (IDS) ─────► eve.json ──► alert_producer.py ──► Kafka(topic=security_alerts)
Packet Sniffer ─────► packet_sniffer.py ────────────────► Kafka(topic=packet_data)

Kafka ──────────────► Django Consumers ───────────────► PostgreSQL  
                                       │
                                       ▼
                                   WebSockets
```

---

# 🛠️ Prerequisites

### System Requirements
* Windows 10/11  
* **Npcap** (WinPcap-compatible mode)  
* **Suricata IDS**  
* **Docker + Docker Compose**  
* Python 3.10+  
* Redis  
* PostgreSQL  
* Kafka + Zookeeper  

---

# 🗄️ Database Setup (PostgreSQL)

## Option A — Docker (Recommended)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: packet_postgres
    environment:
      - POSTGRES_DB=packetdb
      - POSTGRES_USER=packetuser
      - POSTGRES_PASSWORD=12345678
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Add zookeeper + kafka in this file as required

volumes:
  postgres_data:
```

Start services:

```bash
docker-compose up -d
```

Start Redis:

```bash
docker run -p 6380:6379 -d redis:7
```

---

## Option B — Manual PostgreSQL Setup

```sql
CREATE DATABASE packetdb;
CREATE USER packetuser WITH PASSWORD '12345678';
GRANT ALL PRIVILEGES ON DATABASE packetdb TO packetuser;
```

---

# ⚙️ Apply Migrations

```bash
cd packet_analyzer
python manage.py makemigrations
python manage.py migrate
```

---

# 🚀 Running the Backend (Requires Multiple Terminals)

## **Terminal 1 — Start Docker Infrastructure**

```bash
docker-compose up -d
docker run -p 6380:6379 -d redis:7
```

---

## **Terminal 2 — Django Kafka Consumers (3 tabs)**

```bash
python manage.py consume_db
python manage.py consume_live
python manage.py consume_alerts
```

---

## **Terminal 3 — ASGI Server**

```bash
daphne -p 8000 packet_analyzer.asgi:application
```

---

## **Terminal 4 — Packet Sniffer (Producer)**


```bash
python packet_sniffer.py <YOUR_INTERFACE>

```

---

## **Terminal 5 — Suricata IDS Engine**
Run as Administrator:

```powershell
"C:\Program Files\Suricata\suricata.exe" -c suricata.yaml -i <YOUR_IP>
```

---

## **Terminal 6 — Alert Producer**

```bash
python alert_producer.py
```

---

# 🌐 API Endpoints

### **Live Packets (WebSocket)**  
`ws://localhost:8000/ws/live-packets/`

### **Top Talkers**  
`GET /api/top-talkers/<minutes>/`

### **IP Health Check**  
`POST /api/ip-health/`

### **Security Alerts**  
* All alerts → `/api/security-alerts/`  
* Only threats → `/api/security-alerts/?type=threat`  
* Only policy violations → `/api/security-alerts/?type=policy`  

---

# 🛡️ Suricata IDS – Windows Setup

This project ships a full Suricata configuration optimized for Windows.

## 📂 Contents

- `suricata.yaml` → Full configuration  
- `rules/custom.rules` → custom signatures (VPN, SQLi, Malware UA, DNS triggers)  

---

## 🖥️ Prerequisites

### 1. Install **Npcap**
Must check:

✔ "Install Npcap in WinPcap API-compatible Mode"

### 2. Install Suricata (Windows MSI)

---

## 📁 Place Configuration Files

Copy:

```
suricata.yaml → C:\Program Files\Suricata\
custom.rules → C:\Program Files\Suricata\rules\
```

---

## 🔍 Find Your Interface

```
"C:\Program Files\Suricata\suricata.exe" --list-iface
```

---

## ▶ Start Suricata

```
"C:\Program Files\Suricata\suricata.exe" -c suricata.yaml -i <YOUR_IP>
```

---

# 🧾 Custom Ruleset Overview

### **Policy Violations (1000xxx SIDs)**  
Non-malicious but undesirable traffic:

| Service | SID | Method |
|--------|-----|--------|
| BitTorrent | 1000001 | Pattern |
| OpenVPN DPI | 1000002 | app-layer-protocol |
| Tor | 1000003 | DPI |
| Discord | 1000004 | DNS |
| Crypto Mining | 1000006 | DNS |
| OpenVPN Port | 1000008 | Port 1194 |
| WireGuard | 1000009 | DPI |
| NordVPN | 1000010 | DNS |
| ExpressVPN | 1000011 | DNS |

---

### **Threat Detection (2000xxx SIDs)**  
Actual malicious patterns:

| Threat | SID | Logic |
|--------|-----|--------|
| SQL Injection | 2000001 | `OR 1=1` |
| Malware User-Agent | 2000004 | BlackSun |
| C2 Beacon | 2000005 | DNS |
| Nmap Xmas Scan | 2000006 | Flags |

---

# 🧪 Testing Suricata Alerts

### **1. Test Malware (Threat)**

```
curl.exe -A "BlackSun" http://google.com
```

Expected: Malware Alert

---

### **2. Test SQL Injection**

```
curl "http://testphp.vulnweb.com/artists.php?artist=1+OR+1=1"
```

---

### **3. Test Policy Violation (Discord)**

```
nslookup discord.com
```

---

# 📊 Logs

Located at:

```
C:\Program Files\Suricata\log\
```

- `fast.log` - readable alerts  
- `eve.json` - full JSON alerts (used by your Kafka producer)  
- `stats.log` - performance  

---

# ❗ Troubleshooting

### ❌ Error: missing **wpcap.dll**

Reinstall Npcap → enable "WinPcap Compatible Mode"

### ❌ Error: "emerging-all.rules" missing

Comment out this line in `suricata.yaml`:

```yaml
- emerging-all.rules
```

---
