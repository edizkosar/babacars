import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from controlpanel import services, selectors


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)


@superuser_required
@require_http_methods(["GET"])
def panel_home_view(request):
    context = {
        'stats': selectors.get_global_stats(),
        'recent_users': selectors.get_recent_users(limit=8),
        'top_cities': selectors.get_top_cities(),
        'most_viewed': selectors.get_most_viewed_listings(),
        'status_distribution': selectors.get_status_distribution(),
        'top_sellers': selectors.get_top_sellers(),
        'system_summary': selectors.get_system_summary(),
        'recent_activity': selectors.get_recent_activity(),
    }
    return render(request, 'controlpanel/home.html', context)


@superuser_required
@require_http_methods(["GET"])
def panel_users_view(request):
    return render(request, 'controlpanel/users.html', {'users': selectors.get_all_users()})


@superuser_required
@require_http_methods(["GET"])
def panel_listings_view(request):
    return render(request, 'controlpanel/listings.html', {'listings': selectors.get_all_listings()})


@superuser_required
@require_http_methods(["GET"])
def panel_reports_view(request):
    return render(request, 'controlpanel/reports.html', {'reports': selectors.get_all_reports()})


@superuser_required
@require_http_methods(["GET"])
def panel_activity_view(request):
    return render(request, 'controlpanel/activity.html', {'logs': selectors.get_activity_logs()})


@superuser_required
@require_http_methods(["GET"])
def panel_charts_data_view(request):
    return JsonResponse({
        'signup_trend': [{'date': str(x['d']), 'count': x['c']} for x in selectors.get_signup_trend()],
        'listing_trend': [{'date': str(x['d']), 'count': x['c']} for x in selectors.get_listing_trend()],
        'top_cities': [{'city': x['city'], 'count': x['c']} for x in selectors.get_top_cities()],
        'status_distribution': [{'status': x['status'], 'count': x['c']} for x in selectors.get_status_distribution()],
    })


@superuser_required
@require_http_methods(["POST"])
def toggle_user_view(request, user_id):
    u = services.toggle_user_active(user_id=user_id)
    status_text = 'aktif' if u.is_active else 'pasif'
    services.log_activity(actor=request.user, action='admin_action', description=f'{u.email} kullanıcısı {status_text} yapıldı')
    return JsonResponse({'is_active': u.is_active})


@superuser_required
@require_http_methods(["POST"])
def verify_seller_view(request, user_id):
    u = services.verify_seller(user_id=user_id)
    services.log_activity(actor=request.user, action='admin_action', description=f'{u.email} satıcısı doğrulandı')
    return JsonResponse({'message': 'Satıcı doğrulandı.'})


@superuser_required
@require_http_methods(["POST"])
def delete_listing_view(request, listing_id):
    services.log_activity(actor=request.user, action='delete', description=f'İlan #{listing_id} silindi')
    services.delete_listing_admin(listing_id=listing_id)
    return JsonResponse({'message': 'İlan silindi.'})


@superuser_required
@require_http_methods(["POST"])
def set_listing_status_view(request, listing_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        services.set_listing_status_admin(listing_id=listing_id, status=status)
        services.log_activity(actor=request.user, action='update', description=f'İlan #{listing_id} durumu "{status}" olarak güncellendi')
        return JsonResponse({'message': 'Durum güncellendi.'})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@superuser_required
@require_http_methods(["POST"])
def resolve_report_view(request, report_id):
    services.resolve_report(report_id=report_id)
    services.log_activity(actor=request.user, action='admin_action', description=f'Rapor #{report_id} çözüldü olarak işaretlendi')
    return JsonResponse({'message': 'Rapor çözüldü.'})
