# CyberSecurityBackend

A Django-based backend for real-time network packet capture and analysis, using Redis, PostgreSQL, Kafka, and Django Channels.

---

## Prerequisites

Before running the project, ensure you have the following installed:

* Docker & Docker Compose
* Python 3.10+
* Virtual Environment (`venv`)
* PostgreSQL
* Kafka (optional if using live feed)

---

## Setup and Run

This project requires multiple processes running simultaneously. You will need **four separate terminal windows**.

---

### **Terminal 1: Start Infrastructure**

Start the required services (PostgreSQL, Kafka, Redis):

```bash
# Start services defined in docker-compose.yml
docker-compose up -d

# Run Redis on port 6380
docker run -p 6380:6379 -d redis:7
```

> Make sure both **Redis** and **PostgreSQL** are running properly.

---

### **Terminal 2: Start Backend Consumers**

Navigate to your Django project directory and activate your virtual environment. Then run:

```bash
# Start the database consumer
python manage.py consume_db

# In a new tab/window of the same terminal, start the live feed consumer
python manage.py consume_live
```

> These consumers process incoming packets and update the database in real-time.

---

### **Terminal 3: Run the Django ASGI Server**

In the Django project directory, start the ASGI server using **Daphne**:

```bash
daphne -p 8000 packet_analyzer.asgi:application
```

> Do **not** use `runserver`—Daphne is required for WebSocket support.

---

### **Terminal 4: Run the Packet Sniffer (Producer)**

Navigate to the project root and start capturing network packets. Replace `<your_interface>` with your network interface name (e.g., `"Wi-Fi"`):

```bash
sudo python packet_sniffer.py "<your_interface>"
```

> This process produces packets that will be consumed by the backend in real-time.

---

## Access Live Packets

Once everything is running, you can connect to the live packet feed via WebSocket:

```
ws://localhost:8000/ws/live-packets/
```

Use any WebSocket client to view packets in real-time. This data can also be consumed by your frontend React application for live visualization. 📡➡️💻

---

### **Summary**

With this setup, you can:

* Capture network traffic live.
* Process and store packets using Django, Redis, and PostgreSQL.
* Stream packet data to a frontend application via WebSockets.

---
