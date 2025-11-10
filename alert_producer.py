import sys
import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_TOPIC = 'security_alerts'
KAFKA_BROKER = 'localhost:9092'
SURICATA_LOG = r"C:\Program Files\Suricata\log\eve.json"

def create_producer():
    """Tries to connect to Kafka and create a producer."""
    print(f"Attempting to connect to Kafka at {KAFKA_BROKER}...")
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✅ Successfully connected to Kafka.")
            return producer
        except NoBrokersAvailable:
            print("Broker not available. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def follow_file(file_path, producer):
    """Opens a file and follows it, processing new lines."""
    try:
        with open(file_path, 'r') as f:
            # Go to the end of the file
            f.seek(0, 2)
            print(f"Watching {file_path} for new alerts...")
            
            while True:
                line = f.readline()
                
                # If no new line, wait a moment and try again
                if not line:
                    time.sleep(0.1)
                    continue
                
                # We have a new line
                try:
                    alert_data = json.loads(line)
                    if alert_data.get('event_type') == 'alert':
                        sig = alert_data.get('alert', {}).get('signature', 'N/A')
                        print(f"ALERT DETECTED: {sig}")
                        producer.send(KAFKA_TOPIC, alert_data)
                        
                except json.JSONDecodeError:
                    pass # Ignore malformed lines
                except Exception as e:
                    print(f"Error processing line: {e}")
                    
    except FileNotFoundError:
        print(f"ERROR: Log file not found at {SURICATA_LOG}")
        print("Please ensure Suricata is running and the path is correct.")
    except PermissionError:
        print("ERROR: Permission denied.")
        print("Please make sure you are running this script as an Administrator.")
    except KeyboardInterrupt:
        print("\nShutting down alert producer.")
    

def main():
    producer = create_producer()
    try:
        follow_file(SURICATA_LOG, producer)
    finally:
        producer.flush()
        producer.close()
        print("Kafka producer closed.")

if __name__ == "__main__":
    main()