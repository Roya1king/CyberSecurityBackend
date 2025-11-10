from django.db import models

class TrafficLog(models.Model):
    source_ip = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField(db_index=True) # Represents the start of the 1-minute bucket

    # --- NEW FIELDS ADDED ---
    # We make them nullable in case a packet is IP-only (no TCP/UDP)
    protocol = models.CharField(max_length=10, null=True, blank=True)
    source_port = models.PositiveIntegerField(null=True, blank=True)
    dest_port = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # --- END NEW FIELDS ---

    packet_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        # --- UPDATED UNIQUE CONSTRAINT ---
        # This now aggregates packets by the full flow signature per minute
        unique_together = ('source_ip', 'timestamp', 'protocol', 'source_port', 'dest_port')

    def __str__(self):
        # --- UPDATED STRING REPRESENTATION ---
        port_info = f":{self.source_port} -> :{self.dest_port}" if self.protocol else ""
        return (f"{self.source_ip}{port_info} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')} "
                f"({self.protocol or 'IP'}) - {self.packet_count} packets")

# --- NO CHANGES NEEDED TO SECURITYALERT MODEL ---

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