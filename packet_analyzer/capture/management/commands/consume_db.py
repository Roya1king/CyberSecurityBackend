import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F
from kafka import KafkaConsumer
from capture.models import TrafficLog

class Command(BaseCommand):
    help = 'Starts Kafka consumer for aggregating packet counts into the DB'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            'packet_data',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='db-aggregator-group'
        )

        self.stdout.write(self.style.SUCCESS('▶️ Starting DB aggregation consumer...'))

        for message in consumer:
            packet_data = message.value
            source_ip = packet_data.get('source_ip')

            if not source_ip:
                continue

            current_minute_bucket = timezone.now().replace(second=0, microsecond=0)

            # --- THE CORRECTED LOGIC IS HERE ---

            # Step 1: Atomically get the log entry or create a new one if it doesn't exist.
            # The 'defaults' here sets the initial value ONLY when creating.
            log_entry, created = TrafficLog.objects.get_or_create(
                source_ip=source_ip,
                timestamp=current_minute_bucket,
                defaults={'packet_count': 1} # Start the count at 1 if new
            )

            # Step 2: If the entry already existed (was not created), increment its count.
            if not created:
                # Use .update() with F() for an atomic increment operation.
                # This is efficient and safe from race conditions.
                TrafficLog.objects.filter(pk=log_entry.pk).update(packet_count=F('packet_count') + 1)
            
            self.stdout.write(f"Logged packet from {source_ip}")