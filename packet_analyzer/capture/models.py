
from django.db import models

class TrafficLog(models.Model):
    source_ip = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(db_index=True) # Represents the start of the 1-minute bucket
    packet_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('source_ip', 'timestamp')

    def __str__(self):
        return f"{self.source_ip} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.packet_count} packets"

