import json
from scapy.all import sniff, IP, TCP, UDP
from kafka import KafkaProducer
import sys

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'packet_data'
# Get the interface from command-line arguments, default to "Wi-Fi"
IFACE = sys.argv[1] if len(sys.argv) > 1 else "Wi-Fi"

# --- Kafka Producer Setup ---
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Successfully connected to Kafka.")
except Exception as e:
    print(f"❌ Could not connect to Kafka: {e}")
    exit()


def process_and_send(packet):
    """
    Callback function to process each captured packet and send it to Kafka.
    """
    if not packet.haslayer(IP):
        return

    try:
        # --- NEW: Initialize port variables ---
        protocol = None
        source_port = None
        destination_port = None
        
        # --- NEW: Check for TCP layer and extract ports ---
        if packet.haslayer(TCP):
            protocol = 'TCP'
            source_port = packet[TCP].sport
            destination_port = packet[TCP].dport
        
        # --- NEW: Check for UDP layer and extract ports ---
        elif packet.haslayer(UDP):
            protocol = 'UDP'
            source_port = packet[UDP].sport
            destination_port = packet[UDP].dport
        
        # --- Updated packet_info dictionary ---
        packet_info = {
            'source_ip': packet[IP].src,
            'destination_ip': packet[IP].dst,
            'packet_length': len(packet),
            'protocol': protocol,
            'source_port': source_port,
            'destination_port': destination_port
        }
        
        # Send the structured data to the Kafka topic
        producer.send(KAFKA_TOPIC, value=packet_info)
        
        # --- Updated print statement ---
        print(f"Sent: {packet_info['source_ip']}:{packet_info['source_port']} -> {packet_info['destination_ip']}:{packet_info['destination_port']} ({packet_info['protocol']})")

    except Exception as e:
        print(f"⚠️ Error processing packet: {e}")


if __name__ == "__main__":
    print(f"🚀 Starting packet sniffer on interface '{IFACE}'...")
    print(f"Sending data to Kafka topic '{KAFKA_TOPIC}' on broker '{KAFKA_BROKER}'")
    print("Press Ctrl+C to stop.")

    # Start sniffing. store=0 means we don't keep packets in memory.
    # On Linux/macOS, you'll likely need to run this with sudo.
    sniff(iface=IFACE, prn=process_and_send, store=0)