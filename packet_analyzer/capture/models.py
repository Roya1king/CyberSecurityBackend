# In packet_analyzer/capture/models.py
from django.db import models

class TrafficLog(models.Model):
    source_ip = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(db_index=True) # Represents the start of the 1-minute bucket
    packet_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('source_ip', 'timestamp')

    def __str__(self):
        return f"{self.source_ip} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.packet_count} packets"

# --- ADD THIS NEW MODEL BELOW YOUR TRAFFICLOG MODEL ---

class SecurityAlert(models.Model):
    """
    Stores a single security alert from Suricata.
    """
    timestamp = models.DateTimeField(db_index=True)
    signature = models.TextField()
    severity = models.PositiveIntegerField(db_index=True)
    protocol = models.CharField(max_length=20)
    
    src_ip = models.CharField(max_length=50, db_index=True)
    src_port = models.PositiveIntegerField(null=True, blank=True)
    dest_ip = models.CharField(max_length=50, db_index=True)
    dest_port = models.PositiveIntegerField(null=True, blank=True)
    
    # Stores the full JSON alert for detailed analysis
    raw_alert = models.JSONField()

    def __str__(self):
        return f"[{self.timestamp}] {self.signature} (Severity: {self.severity})"

    class Meta:
        ordering = ['-timestamp']