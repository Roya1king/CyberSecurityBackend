# capture/management/commands/consume_live.py

import json
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Starts Kafka consumer for the live WebSocket feed'

    def handle(self, *args, **options):
        consumer = KafkaConsumer(
            'packet_data',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='live-feed-group' # Use a different group ID
        )
        
        channel_layer = get_channel_layer()
        self.stdout.write(self.style.SUCCESS('▶️ Starting live feed consumer...'))

        for message in consumer:
            packet_data = message.value
            
            # Send the packet data to the 'live_packets' group
            async_to_sync(channel_layer.group_send)(
                'live_packets',
                {
                    'type': 'packet_message', # This calls the method in our consumer
                    'packet': packet_data
                }
            )
            self.stdout.write(f"Pushed live packet from {packet_data.get('source_ip')}")