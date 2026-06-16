from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from notifications import services, selectors

@login_required
@require_http_methods(["GET"])
def notifications_view(request):
    notifications = selectors.get_notifications_by_user(user=request.user)
    return render(request, 'notifications/notifications.html', {'notifications': notifications})

@login_required
@require_http_methods(["POST"])
def mark_as_read_view(request, notification_id):
    try:
        services.mark_as_read(user=request.user, notification_id=notification_id)
        return JsonResponse({'message': 'Bildirim okundu olarak işaretlendi.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def mark_all_as_read_view(request):
    count = services.mark_all_as_read(user=request.user)
    return JsonResponse({'message': 'Tüm bildirimler okundu.', 'count': count})

@login_required
@require_http_methods(["GET"])
def unread_count_view(request):
    count = services.get_unread_count(user=request.user)
    return JsonResponse({'unread_count': count})
