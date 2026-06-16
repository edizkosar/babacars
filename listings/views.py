from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from listings import services, selectors
from listings.forms import ListingForm, VehicleForm, SearchForm

@require_http_methods(["GET"])
def index_view(request):
    listings = selectors.get_active_listings()
    paginator = Paginator(listings, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'listings/index.html', {'listings': page_obj.object_list, 'page_obj': page_obj})

@require_http_methods(["GET"])
def search_view(request):
    filters = request.GET.dict()
    results = selectors.search_listings(filters=filters)
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = SearchForm(request.GET)
    return render(request, 'listings/search.html', {'results': page_obj.object_list, 'page_obj': page_obj, 'form': form})

@require_http_methods(["GET"])
def map_view(request):
    """İlanları interaktif harita üzerinde gösteren sayfa."""
    form = SearchForm(request.GET)
    return render(request, 'listings/map.html', {'form': form})


@require_http_methods(["GET"])
def map_data_view(request):
    """Harita için ilanları GeoJSON olarak döndürür (filtre destekli).

    Koordinat anlık hesaplanır: ilçe doluysa o ilçe, boşsa şehrin merkez
    ilçesi kullanılır. Veritabanına koordinat yazılmaz.
    """
    from listings.geo import resolve_coordinates, central_district_name

    filters = request.GET.dict()
    qs = selectors.search_listings(filters=filters)

    features = []
    for listing in qs[:300]:
        coords = resolve_coordinates(listing.city, listing.district, seed=listing.id)
        if not coords:
            continue  # bilinmeyen şehir → haritada gösterme
        lat, lng = coords
        vehicle = getattr(listing, 'vehicle', None)
        cover = listing.photos.first()
        # İlçe gösterimi: doluysa kendi ilçesi, boşsa merkez ilçe
        shown_district = listing.district or central_district_name(listing.city)
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lng, lat],
            },
            'properties': {
                'district': shown_district,
                'id': listing.id,
                'title': listing.title,
                'price': f"{listing.price:,.0f} {listing.currency}".replace(',', '.'),
                'city': listing.city,
                'url': f'/{listing.slug}/',
                'type': listing.listing_type,
                'year': vehicle.year if vehicle else '',
                'make': vehicle.make if vehicle else '',
                'model': vehicle.model if vehicle else '',
                'cover': cover.image.url if cover else '',
            },
        })

    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@require_http_methods(["GET"])
def listing_detail_view(request, slug):
    try:
        listing = selectors.get_listing_by_slug(slug=slug)
    except Exception:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('listings:index')
        
    services.track_view(
        listing_id=listing.id, 
        user=request.user if request.user.is_authenticated else None, 
        ip_address=request.META.get('REMOTE_ADDR')
    )
    photos = selectors.get_photos_by_listing(listing=listing)
    
    is_favorited = False
    if request.user.is_authenticated:
        try:
            selectors.get_favorite(user=request.user, listing=listing)
            is_favorited = True
        except Exception:
            pass
            
    valuation = services.get_vehicle_valuation(listing_id=listing.id)

    # Recently viewed session tracking
    recently_viewed = request.session.get('recently_viewed', [])
    if listing.id not in recently_viewed:
        recently_viewed.insert(0, listing.id)
        recently_viewed = recently_viewed[:6]
        request.session['recently_viewed'] = recently_viewed

    similar_listings = selectors.get_similar_listings(listing=listing)
    recent_listings = []
    for lid in recently_viewed:
        if lid != listing.id:
            try:
                recent_listings.append(selectors.get_listing_by_id(listing_id=lid))
            except Exception:
                pass

    return render(request, 'listings/detail.html', {
        'listing': listing,
        'photos': photos,
        'is_favorited': is_favorited,
        'valuation': valuation,
        'similar_listings': similar_listings,
        'recent_listings': recent_listings[:5],
    })

@require_http_methods(["GET"])
def listing_pdf_view(request, slug):
    """İlan föyünü PDF olarak indirir."""
    from django.http import HttpResponse, Http404
    from listings.pdf import build_listing_pdf
    try:
        listing = selectors.get_listing_by_slug(slug=slug)
    except Exception:
        raise Http404('İlan bulunamadı.')

    pdf_bytes = build_listing_pdf(listing)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    safe_slug = slug or f'ilan-{listing.id}'
    response['Content-Disposition'] = f'attachment; filename="babacars-{safe_slug}.pdf"'
    return response


@login_required
@require_http_methods(["GET", "POST"])
def create_listing_view(request):
    if request.method == "POST":
        listing_form = ListingForm(request.POST)
        vehicle_form = VehicleForm(request.POST)
        photos = request.FILES.getlist('photos')
        
        if listing_form.is_valid() and vehicle_form.is_valid():
            try:
                listing = services.create_listing(
                    seller=request.user,
                    listing_data=listing_form.cleaned_data,
                    vehicle_data=vehicle_form.cleaned_data,
                    photos=photos
                )
                return redirect('listings:detail', slug=listing.slug)
            except ValueError as e:
                messages.error(request, str(e))
            except PermissionError:
                return redirect('accounts:become_seller')
    else:
        listing_form = ListingForm()
        vehicle_form = VehicleForm()
        
    return render(request, 'listings/create.html', {
        'listing_form': listing_form,
        'vehicle_form': vehicle_form
    })

@login_required
@require_http_methods(["GET", "POST"])
def edit_listing_view(request, slug):
    try:
        listing = selectors.get_listing_by_slug(slug=slug)
    except Exception:
        messages.error(request, 'İlan bulunamadı.')
        return redirect('listings:index')
        
    if request.method == "POST":
        listing_form = ListingForm(request.POST, instance=listing)
        vehicle_form = VehicleForm(request.POST, instance=listing.vehicle)
        
        if listing_form.is_valid() and vehicle_form.is_valid():
            try:
                updated_listing = services.update_listing(
                    user=request.user,
                    listing_id=listing.id,
                    listing_data=listing_form.cleaned_data,
                    vehicle_data=vehicle_form.cleaned_data
                )
                return redirect('listings:detail', slug=updated_listing.slug)
            except PermissionError as e:
                messages.error(request, str(e))
                return redirect('listings:index')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        listing_form = ListingForm(instance=listing)
        vehicle_form = VehicleForm(instance=listing.vehicle)
        
    return render(request, 'listings/edit.html', {
        'listing_form': listing_form,
        'vehicle_form': vehicle_form,
        'listing': listing
    })

@login_required
@require_http_methods(["POST"])
def delete_listing_view(request, listing_id):
    try:
        services.delete_listing(user=request.user, listing_id=listing_id)
        messages.success(request, 'İlan başarıyla silindi.')
        return redirect('accounts:profile')
    except (PermissionError, ValueError) as e:
        messages.error(request, str(e))
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)

@login_required
@require_http_methods(["POST"])
def toggle_favorite_view(request, listing_id):
    try:
        result = services.toggle_favorite(user=request.user, listing_id=listing_id)
        return JsonResponse(result)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def my_favorites_view(request):
    favorites = selectors.get_favorites_by_user(user=request.user)
    return render(request, 'listings/favorites.html', {'favorites': favorites})

@require_http_methods(["GET", "POST"])
def compare_view(request):
    if request.method == "POST":
        if request.POST.get('clear'):
            request.session['compare_ids'] = []
            return redirect('listings:compare')

        listing_id = request.POST.get('listing_id')
        if not listing_id:
            return JsonResponse({'error': 'Geçersiz ilan.'}, status=400)
        try:
            listing_id = int(listing_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Geçersiz ilan.'}, status=400)

        compare_ids = request.session.get('compare_ids', [])

        in_compare = False
        if listing_id in compare_ids:
            compare_ids.remove(listing_id)
        else:
            if len(compare_ids) >= 3:
                return JsonResponse({'error': 'Max 3 araç eklenebilir.'}, status=400)
            compare_ids.append(listing_id)
            in_compare = True

        request.session['compare_ids'] = compare_ids
        return JsonResponse({'compare_count': len(compare_ids), 'in_compare': in_compare})
    else:
        compare_ids = request.session.get('compare_ids', [])
        listings = []
        for lid in compare_ids:
            try:
                listings.append(selectors.get_listing_by_id(listing_id=lid))
            except Exception:
                pass
        return render(request, 'listings/compare.html', {'listings': listings})

@login_required
@require_http_methods(["POST"])
def report_listing_view(request, listing_id):
    import json
    try:
        data = json.loads(request.body)
        services.report_listing(
            reporter=request.user, listing_id=listing_id,
            reason=data.get('reason'), description=data.get('description', '')
        )
        return JsonResponse({'message': 'İlan raporlandı. Teşekkürler.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def refresh_listing_view(request, listing_id):
    try:
        services.refresh_listing(user=request.user, listing_id=listing_id)
        return JsonResponse({'message': 'İlan yenilendi, en üste taşındı.'})
    except (ValueError, PermissionError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def bulk_update_view(request):
    import json
    try:
        data = json.loads(request.body)
        count = services.bulk_update_status(
            user=request.user,
            listing_ids=data.get('listing_ids', []),
            status=data.get('status')
        )
        return JsonResponse({'message': f'{count} ilan güncellendi.', 'count': count})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
