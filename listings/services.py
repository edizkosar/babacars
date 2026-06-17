from django.db import transaction
from listings.models import Listing, Vehicle, Photo, Favorite, ListingView, STATUS_CHOICES
from listings import selectors


def _optimize_image(uploaded_file, max_dim: int = 1600, quality: int = 82):
    """
    Yüklenen fotoğrafı küçültüp JPEG'e çevirir → upload hızlanır, depolama küçülür.
    Herhangi bir sorunda orijinal dosyayı olduğu gibi döndürür (güvenli).
    """
    try:
        import io
        from PIL import Image, ImageOps
        from django.core.files.base import ContentFile

        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)          # telefon dönüklüğünü düzelt
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')                 # WebP/PNG şeffaflık → JPEG
        img.thumbnail((max_dim, max_dim))            # oranı koruyarak küçült

        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        buf.seek(0)

        name = getattr(uploaded_file, 'name', 'photo')
        base = name.rsplit('.', 1)[0] if '.' in name else name
        return ContentFile(buf.read(), name=f'{base}.jpg')
    except Exception:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        return uploaded_file


def create_listing(*, seller, listing_data: dict, vehicle_data: dict, photos: list) -> Listing:
    if not seller.is_seller():
        raise PermissionError('User is not a seller')
    if len(photos) < 4:
        raise ValueError('En az 4 fotoğraf gerekli')

    # Hepsi-ya-hiç: araç veya foto kaydı patlarsa ilan da kaydedilmesin (yarım ilan kalmasın)
    with transaction.atomic():
        listing = Listing(seller=seller, **listing_data)
        listing.save()

        Vehicle.objects.create(listing=listing, **vehicle_data)

        for idx, photo_file in enumerate(photos):
            Photo.objects.create(
                listing=listing,
                image=_optimize_image(photo_file),
                is_cover=(idx == 0),
                order=idx
            )

    return listing

def update_listing(*, user, listing_id: int, listing_data: dict = None, vehicle_data: dict = None) -> Listing:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Not authorized')
    if listing.status in ['sold', 'rented']:
        raise ValueError('Cannot update sold or rented listing')
        
    if listing_data:
        for key, value in listing_data.items():
            setattr(listing, key, value)
        listing.save()
        
    if vehicle_data:
        vehicle = listing.vehicle
        for key, value in vehicle_data.items():
            setattr(vehicle, key, value)
        vehicle.save()
        
    return listing

def delete_listing(*, user, listing_id: int) -> None:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Not authorized')
    if listing.status in ['sold', 'rented']:
        raise ValueError('Cannot delete sold or rented listing')
        
    listing.delete()

def set_listing_status(*, user, listing_id: int, status: str) -> Listing:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Not authorized')
        
    valid_statuses = [choice[0] for choice in STATUS_CHOICES]
    if status not in valid_statuses:
        raise ValueError('Invalid status')
        
    listing.status = status
    listing.save(update_fields=['status'])
    return listing

def add_photo(*, user, listing_id: int, image) -> Photo:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Not authorized')
        
    # Get max order
    max_order = Photo.objects.filter(listing=listing).order_by('-order').first()
    new_order = (max_order.order + 1) if max_order else 0
    
    return Photo.objects.create(
        listing=listing,
        image=image,
        is_cover=False,
        order=new_order
    )

def delete_photo(*, user, photo_id: int) -> None:
    photo = selectors.get_photo_by_id(photo_id=photo_id)
    if user != photo.listing.seller:
        raise PermissionError('Not authorized')
    if photo.is_cover:
        raise ValueError('Cannot delete cover photo')
        
    photo.delete()

def set_cover_photo(*, user, photo_id: int) -> Photo:
    photo = selectors.get_photo_by_id(photo_id=photo_id)
    if user != photo.listing.seller:
        raise PermissionError('Not authorized')
        
    Photo.objects.filter(listing=photo.listing).update(is_cover=False)
    photo.is_cover = True
    photo.save(update_fields=['is_cover'])
    return photo

def toggle_favorite(*, user, listing_id: int) -> dict:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user == listing.seller:
        raise ValueError('Cannot favorite your own listing')
        
    try:
        fav = selectors.get_favorite(user=user, listing=listing)
        fav.delete()
        listing.favorite_count = max(0, listing.favorite_count - 1)
        listing.save(update_fields=['favorite_count'])
        is_favorited = False
    except Favorite.DoesNotExist:
        Favorite.objects.create(user=user, listing=listing)
        listing.favorite_count += 1
        listing.save(update_fields=['favorite_count'])
        is_favorited = True
        
    return {'is_favorited': is_favorited, 'favorite_count': listing.favorite_count}

def track_view(*, listing_id: int, user=None, ip_address: str = None) -> None:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    
    # Prevent duplicate views from same IP/User within a short time (optional logic, but typically required for accuracy)
    # Sticking strictly to spec:
    ListingView.objects.create(
        listing=listing,
        user=user if user and user.is_authenticated else None,
        ip_address=ip_address or None
    )
    
    listing.view_count += 1
    listing.save(update_fields=['view_count'])


def report_listing(*, reporter, listing_id: int, reason: str, description: str = '') -> 'ListingReport':
    from listings.models import ListingReport
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if reporter == listing.seller:
        raise PermissionError('Kendi ilanınızı raporlayamazsınız.')
    valid_reasons = ['fake', 'sold', 'wrong_info', 'spam', 'other']
    if reason not in valid_reasons:
        raise ValueError('Geçersiz rapor sebebi.')
    return ListingReport.objects.create(
        listing=listing, reporter=reporter, reason=reason, description=description
    )


def get_vehicle_valuation(*, listing_id: int) -> dict:
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    try:
        v = listing.vehicle
    except Exception:
        return {'available': False}
    data = selectors.get_valuation_data(make=v.make, model=v.model, year=v.year)
    if not data['count'] or data['count'] < 2:
        return {'available': False}
    return {
        'available': True,
        'avg_price': round(float(data['avg_price'])),
        'min_price': round(float(data['min_price'])),
        'max_price': round(float(data['max_price'])),
        'sample_size': data['count'],
        'this_price': float(listing.price),
        'verdict': 'below' if listing.price < data['avg_price'] else 'above',
    }


def refresh_listing(*, user, listing_id: int) -> 'Listing':
    from django.utils import timezone
    listing = selectors.get_listing_by_id(listing_id=listing_id)
    if user != listing.seller:
        raise PermissionError('Bu ilanı yenileme yetkiniz yok.')
    if listing.status != 'active':
        raise ValueError('Sadece aktif ilanlar yenilenebilir.')
    listing.created_at = timezone.now()
    listing.save(update_fields=['created_at'])
    return listing


def bulk_update_status(*, user, listing_ids: list, status: str) -> int:
    valid = ['active', 'passive']
    if status not in valid:
        raise ValueError('Geçersiz durum.')
    listings = Listing.objects.filter(id__in=listing_ids, seller=user)
    listings = listings.exclude(status__in=['sold', 'rented'])
    return listings.update(status=status)

