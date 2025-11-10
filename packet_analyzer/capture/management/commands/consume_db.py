import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F
from kafka import KafkaConsumer
from capture.models import TrafficLog
import time
from kafka.errors import NoBrokersAvailable

class Command(BaseCommand):
    help = 'Starts Kafka consumer for aggregating packet counts into the DB'

    def handle(self, *args, **options):
        consumer = None
        self.stdout.write(self.style.SUCCESS('▶️ Attempting to connect to Kafka for DB aggregation...'))
        
        while consumer is None:
            try:
                consumer = KafkaConsumer(
                    'packet_data',
                    bootstrap_servers='localhost:9092',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    group_id='db-aggregator-group'
                )
                self.stdout.write(self.style.SUCCESS('✅ Kafka consumer connected.'))
            except NoBrokersAvailable:
                self.stdout.write(self.style.WARNING('Kafka not available. Retrying in 5s...'))
                time.sleep(5)

        for message in consumer:
            packet_data = message.value
            
            # --- UPDATED TO GET NEW FIELDS ---
            source_ip = packet_data.get('source_ip')
            protocol = packet_data.get('protocol')
            source_port = packet_data.get('source_port')
            dest_port = packet_data.get('destination_port')
            # --- END UPDATES ---

            if not source_ip:
                continue

            current_minute_bucket = timezone.now().replace(second=0, microsecond=0)

            # --- UPDATED get_or_create TO USE NEW FIELDS ---
            log_entry, created = TrafficLog.objects.get_or_create(
                source_ip=source_ip,
                timestamp=current_minute_bucket,
                protocol=protocol,
                source_port=source_port,
                dest_port=dest_port,
                defaults={'packet_count': 1} # Start the count at 1 if new
            )

            if not created:
                # This logic remains the same - it's atomic and fast
                TrafficLog.objects.filter(pk=log_entry.pk).update(packet_count=F('packet_count') + 1)
            
            # --- UPDATED PRINT STATEMENT ---
            port_info = f":{source_port} -> :{dest_port}" if protocol else ""
            self.stdout.write(f"Logged: {source_ip}{port_info} ({protocol or 'IP'})")