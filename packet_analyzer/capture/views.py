# from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import TrafficLog

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