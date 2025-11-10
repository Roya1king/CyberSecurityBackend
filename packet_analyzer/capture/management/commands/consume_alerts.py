import json
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from django.core.management.base import BaseCommand
from capture.models import SecurityAlert
from dateutil.parser import isoparse
from django.utils import timezone

# Make sure you've installed this library: pip install python-dateutil
# And this one: pip install kafka-python

KAFKA_TOPIC = 'security_alerts'
KAFKA_BROKER = 'localhost:9092'

class Command(BaseCommand):
    help = 'Consumes security alerts from Kafka and saves them to the database.'

    def handle(self, *args, **options):
        self.stdout.write(f"Attempting to connect to Kafka at {KAFKA_BROKER}...")
        consumer = None
        while consumer is None:
            try:
                consumer = KafkaConsumer(
                    KAFKA_TOPIC,
                    bootstrap_servers=[KAFKA_BROKER],
                    auto_offset_reset='earliest', # Start from the beginning if consumer is new
                    group_id='suricata-alert-savers',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                self.stdout.write(self.style.SUCCESS("✅ Successfully connected to Kafka."))
            except NoBrokersAvailable:
                self.stdout.write("Broker not available. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"An error occurred: {e}. Retrying..."))
                time.sleep(5)

        self.stdout.write(f"Waiting for alerts on topic '{KAFKA_TOPIC}'...")
        
        for message in consumer:
            try:
                alert_data = message.value
                
                # We only care about alerts
                if alert_data.get('event_type') != 'alert':
                    continue

                # Extract the nested alert details
                alert_info = alert_data.get('alert', {})
                
                # Parse the timestamp. Suricata's format is ISO 8601.
                # Example: "2025-11-11T03:05:55.123456+0530"
                # Use isoparse to handle the timezone info correctly
                timestamp = isoparse(alert_data.get('timestamp'))
                
                # Ensure timestamp is timezone-aware (Django requires this)
                if not timezone.is_aware(timestamp):
                    timestamp = timezone.make_aware(timestamp, timezone.utc)


                # Create the database object
                alert = SecurityAlert(
                    timestamp=timestamp,
                    signature=alert_info.get('signature'),
                    severity=alert_info.get('severity'),
                    protocol=alert_data.get('proto'),
                    src_ip=alert_data.get('src_ip'),
                    src_port=alert_data.get('src_port'),
                    dest_ip=alert_data.get('dest_ip'),
                    dest_port=alert_data.get('dest_port'),
                    raw_alert=alert_data  # Store the whole thing
                )
                alert.save()
                
                self.stdout.write(self.style.SUCCESS(f"Saved alert: {alert.signature}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing message: {e} | DATA: {message.value}"))