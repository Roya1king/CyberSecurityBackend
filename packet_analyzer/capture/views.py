from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Sum, Q  # <--- IMPORT Q HERE
from datetime import timedelta
from .models import TrafficLog, SecurityAlert
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from icmplib import ping, NameLookupError

# --- 1. Top Talkers View ---
def get_top_talkers(request, minutes_str):
    try:
        minutes = int(minutes_str)
        if not (0 < minutes <= 24 * 60): 
            raise ValueError()
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Please provide a valid number of minutes.")

    time_threshold = timezone.now() - timedelta(minutes=minutes)
    
    top_talkers = list(TrafficLog.objects.filter(
        timestamp__gte=time_threshold
    ).values(
        'source_ip', 'dest_port', 'protocol'
    ).annotate(
        total_packets=Sum('packet_count')
    ).order_by('-total_packets')[:100])

    return JsonResponse(top_talkers, safe=False)

# --- 2. IP Health Check View ---
@csrf_exempt
@require_http_methods(["POST"])
def check_ip_health(request):
    try:
        data = json.loads(request.body)
        ip_address = data.get('ip_address')

        if not ip_address:
            return JsonResponse({'error': 'IP address not provided.'}, status=400)

        # Run the ping
        host = ping(ip_address, count=4, interval=0.2, timeout=4)
        ttl = getattr(host, "hop_limit", None) if host.is_alive else None

        return JsonResponse({
            'ip_address': ip_address,
            'is_alive': host.is_alive,
            'rtt_avg_ms': f"{host.avg_rtt:.2f}" if host.is_alive else None,
            'ttl': ttl,
            'packet_loss_percent': f"{host.packet_loss * 100:.1f}"
        })

    except NameLookupError:
        return JsonResponse({
            'ip_address': ip_address,
            'is_alive': False,
            'error': 'Host not found (DNS lookup failed).'
        }, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- 3. Security Alerts View (UPDATED) ---
def get_security_alerts(request):
    """
    API to fetch alerts with optional filtering.
    Usage: 
      - /api/security-alerts/ (All)
      - /api/security-alerts/?type=policy (Policy Violations)
      - /api/security-alerts/?type=threat (Threats)
    """
    alert_type = request.GET.get('type')
    
    # Start with all alerts, newest first
    alerts_queryset = SecurityAlert.objects.all().order_by('-timestamp')

    # --- FILTER LOGIC ---
    if alert_type == 'policy':
        # Filter for Policy Violation keywords
        alerts_queryset = alerts_queryset.filter(
            Q(raw_alert__alert__category__icontains='Policy') |
            Q(raw_alert__alert__category__icontains='Violation')
        )
        
    elif alert_type == 'threat':
        # Filter for Threats (Exclude Policy Violations)
        alerts_queryset = alerts_queryset.exclude(
            Q(raw_alert__alert__category__icontains='Policy') |
            Q(raw_alert__alert__category__icontains='Violation')
        )

    # --- PAGINATION ---
    page_number = request.GET.get('page', 1)
    paginator = Paginator(alerts_queryset, 25)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return JsonResponse({
            'total_alerts': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_number,
            'alerts': []
        })

    # Build simplified response list
    alerts_data = list(page_obj.object_list.values(
        'id', 'timestamp', 'signature', 'severity', 
        'protocol', 'src_ip', 'src_port', 'dest_ip', 'dest_port',
        'raw_alert'
    ))

    return JsonResponse({
        'total_alerts': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'alerts': alerts_data
    })