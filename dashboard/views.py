from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from dashboard import services
from listings import selectors as listing_selectors

@login_required
@require_http_methods(["GET"])
def dashboard_view(request):
    if not request.user.is_seller():
        messages.info(request, 'Dashboard ekranını görüntülemek için satıcı olmalısınız.')
        return redirect('accounts:become_seller')
        
    summary = services.get_dashboard_summary(user=request.user)
    listings = listing_selectors.get_listings_by_seller(seller=request.user)
    return render(request, 'dashboard/dashboard.html', {'summary': summary, 'listings': listings})

@login_required
@require_http_methods(["GET"])
def listing_stats_view(request, listing_id):
    try:
        stats = services.get_listing_stats(user=request.user, listing_id=listing_id)
        return render(request, 'dashboard/listing_stats.html', {'stats': stats})
    except PermissionError as e:
        messages.error(request, str(e))
        return redirect('dashboard:dashboard')

@login_required
@require_http_methods(["GET"])
def listing_traffic_view(request, listing_id):
    try:
        listing = listing_selectors.get_listing_by_id(listing_id=listing_id)
        if request.user != listing.seller:
            return JsonResponse({'error': 'Bu ilanın istatistiklerini görme yetkiniz yok.'}, status=403)
        hourly = services.get_hourly_traffic(listing_id=listing_id)
        daily = services.get_daily_traffic(listing_id=listing_id)
        return JsonResponse({'hourly': hourly, 'daily': daily})
    except (PermissionError, Exception) as e:
        return JsonResponse({'error': str(e)}, status=400)
