from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from bookings import services, selectors

@login_required
@require_http_methods(["GET"])
def my_bookings_view(request):
    bookings = selectors.get_bookings_by_renter(renter=request.user)
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
@require_http_methods(["GET"])
def booking_detail_view(request, booking_id):
    try:
        booking = selectors.get_booking_by_id(booking_id=booking_id)
        if request.user not in [booking.renter, booking.listing.seller]:
            messages.error(request, 'Bu sayfayı görüntüleme yetkiniz yok.')
            return redirect('listings:index')
        return render(request, 'bookings/booking_detail.html', {'booking': booking})
    except Exception:
        messages.error(request, 'Rezervasyon bulunamadı.')
        return redirect('listings:index')

@login_required
@require_http_methods(["POST"])
def cancel_booking_view(request, booking_id):
    try:
        services.cancel_booking(user=request.user, booking_id=booking_id)
        messages.success(request, 'Rezervasyon başarıyla iptal edildi.')
        return redirect('bookings:my_bookings')
    except (PermissionError, ValueError) as e:
        messages.error(request, str(e))
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)

@login_required
@require_http_methods(["POST"])
def block_dates_view(request, listing_id):
    from datetime import datetime
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    reason = request.POST.get('reason', 'blocked')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        services.block_dates(
            user=request.user, 
            listing_id=listing_id, 
            start_date=start_date, 
            end_date=end_date, 
            reason=reason
        )
        return JsonResponse({'message': 'Tarihler bloklandı.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def unblock_dates_view(request, unavailable_date_id):
    try:
        services.unblock_dates(user=request.user, unavailable_date_id=unavailable_date_id)
        return JsonResponse({'message': 'Blok kaldırıldı.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def check_availability_view(request, listing_id):
    from datetime import datetime
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse({'error': 'Tarihler eksik'}, status=400)
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Geçersiz tarih formatı'}, status=400)

    is_available = services.check_availability(
        listing_id=listing_id, 
        start_date=start_date, 
        end_date=end_date
    )
    return JsonResponse({'available': is_available})
