# capture/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class LivePacketConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'live_packets'

        # Join the 'live_packets' group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    def disconnect(self, close_code):
        # Leave the group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected: {self.channel_name}")

    # This method is called when we send a message to the group
    def packet_message(self, event):
        packet_data = event['packet']

        # Send the packet data to the WebSocket client
        self.send(text_data=json.dumps(packet_data))