import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from alerts import services, selectors


@login_required
@require_http_methods(["POST"])
def create_price_alert_view(request, listing_id):
    try:
        data = json.loads(request.body)
        alert = services.create_price_alert(
            user=request.user, listing_id=listing_id,
            target_price=float(data.get('target_price'))
        )
        return JsonResponse({'message': 'Fiyat alarmı kuruldu.', 'alert_id': alert.id})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_price_alert_view(request, alert_id):
    try:
        services.delete_price_alert(user=request.user, alert_id=alert_id)
        return JsonResponse({'message': 'Alarm silindi.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def save_search_view(request):
    try:
        data = json.loads(request.body)
        search = services.create_saved_search(
            user=request.user, name=data.get('name', ''),
            filters=data.get('filters', {})
        )
        return JsonResponse({'message': 'Arama kaydedildi.', 'search_id': search.id})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_saved_search_view(request, search_id):
    try:
        services.delete_saved_search(user=request.user, search_id=search_id)
        return JsonResponse({'message': 'Arama silindi.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def toggle_watchlist_view(request, listing_id):
    try:
        from alerts.models import Watchlist
        from listings.selectors import get_listing_by_id
        listing = get_listing_by_id(listing_id=listing_id)
        existing = Watchlist.objects.filter(user=request.user, listing=listing).exists()
        if existing:
            services.remove_from_watchlist(user=request.user, listing_id=listing_id)
            return JsonResponse({'watching': False, 'message': 'İzlemeden çıkarıldı.'})
        else:
            services.add_to_watchlist(user=request.user, listing_id=listing_id)
            return JsonResponse({'watching': True, 'message': 'İzlemeye alındı.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def my_alerts_view(request):
    context = {
        'price_alerts': selectors.get_user_price_alerts(user=request.user),
        'saved_searches': selectors.get_user_saved_searches(user=request.user),
        'watchlist': selectors.get_user_watchlist(user=request.user),
    }
    return render(request, 'alerts/my_alerts.html', context)
