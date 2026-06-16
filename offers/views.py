from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from offers import services, selectors
from offers.forms import OfferForm, CounterOfferForm
import json

@login_required
@require_http_methods(["POST"])
def create_offer_view(request, listing_id):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST.dict()

    form = OfferForm(data)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    try:
        offer = services.create_offer(
            buyer=request.user,
            listing_id=listing_id,
            amount=form.cleaned_data['amount'],
            message=form.cleaned_data.get('message', ''),
            rental_start_date=form.cleaned_data.get('rental_start_date'),
            rental_end_date=form.cleaned_data.get('rental_end_date')
        )
        return JsonResponse({'message': 'Teklifiniz gönderildi.', 'offer_id': offer.id})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def accept_offer_view(request, offer_id):
    try:
        services.accept_offer(user=request.user, offer_id=offer_id)
        return JsonResponse({'message': 'Teklif kabul edildi.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def reject_offer_view(request, offer_id):
    try:
        services.reject_offer(user=request.user, offer_id=offer_id)
        return JsonResponse({'message': 'Teklif reddedildi.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def counter_offer_view(request, offer_id):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST.dict()

    form = CounterOfferForm(data)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
        
    try:
        new_offer = services.counter_offer(
            user=request.user,
            offer_id=offer_id,
            amount=form.cleaned_data['amount'],
            message=form.cleaned_data['message']
        )
        return JsonResponse({'message': 'Karşı teklifiniz gönderildi.', 'offer_id': new_offer.id})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def cancel_offer_view(request, offer_id):
    try:
        services.cancel_offer(user=request.user, offer_id=offer_id)
        return JsonResponse({'message': 'Teklif iptal edildi.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def my_offers_view(request):
    offers = selectors.get_offers_by_buyer(buyer=request.user)
    return render(request, 'offers/my_offers.html', {'offers': offers})

@login_required
@require_http_methods(["GET"])
def listing_offers_view(request, listing_id):
    from listings import selectors as listing_selectors
    try:
        listing = listing_selectors.get_listing_by_id(listing_id=listing_id)
    except Exception:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('listings:index')
        
    if request.user != listing.seller:
        messages.error(request, 'Bu sayfayı görüntüleme yetkiniz yok.')
        return redirect('listings:index')
        
    offers = selectors.get_offers_by_listing(listing=listing)
    return render(request, 'offers/listing_offers.html', {'offers': offers, 'listing': listing})
