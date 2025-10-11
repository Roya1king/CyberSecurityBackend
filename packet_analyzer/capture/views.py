from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import TrafficLog
import json
from icmplib import ping, NameLookupError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def get_top_talkers(request, minutes_str):
    try:
        minutes = int(minutes_str)
        if not (0 < minutes <= 24 * 60): # Limit range
            raise ValueError()
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Please provide a valid number of minutes.")

    time_threshold = timezone.now() - timedelta(minutes=minutes)
    
    top_talkers = list(TrafficLog.objects.filter(
        timestamp__gte=time_threshold
    ).values(
        'source_ip'
    ).annotate(
        total_packets=Sum('packet_count')
    ).order_by(
        '-total_packets'
    )[:10]) # Top 10

    return JsonResponse(top_talkers, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def check_ip_health(request):
    try:
        data = json.loads(request.body)
        ip_address = data.get('ip_address')

        if not ip_address:
            return JsonResponse({'error': 'IP address not provided.'}, status=400)

        host = ping(ip_address, count=4, interval=0.2, timeout=4)

        # Use getattr to avoid AttributeError if hop_limit is missing
        ttl = getattr(host, "hop_limit", None) if host.is_alive else None

        response_data = {
            'ip_address': ip_address,
            'is_alive': host.is_alive,
            'rtt_avg_ms': f"{host.avg_rtt:.2f}" if host.is_alive else None,
            'ttl': ttl,
            'packets_sent': host.packets_sent,
            'packets_received': host.packets_received,
            'packet_loss_percent': f"{host.packet_loss * 100:.1f}"
        }
        return JsonResponse(response_data)

    except NameLookupError:
        return JsonResponse({
            'ip_address': ip_address,
            'is_alive': False,
            'error': 'Host not found (DNS lookup failed).'
        }, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)