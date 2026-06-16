# selectors.md

## Reference
See PROJECT_OVERVIEW.md for full architecture and naming conventions.
See all models MD files for model definitions.

## Purpose
All ORM queries for all apps.
No business logic. No HTTP logic. Returns model instances or querysets only.
Views and services import from here. Never write ORM queries outside selectors.

## Rules
- Every function uses keyword-only arguments (*)
- Raise ObjectDoesNotExist if single object not found
- Never filter by status inside selectors — filtering by status is services.py responsibility
- Return QuerySet for lists, model instance for single objects

---

## accounts/selectors.py

```python
from django.contrib.auth import get_user_model
from accounts.models import SellerProfile, Review

User = get_user_model()

def get_user_by_id(*, user_id: int) -> User:
    return User.objects.get(id=user_id)

def get_user_by_email(*, email: str) -> User:
    return User.objects.get(email=email)

def get_seller_profile(*, user) -> SellerProfile:
    return SellerProfile.objects.get(user=user)

def get_seller_profile_by_id(*, seller_profile_id: int) -> SellerProfile:
    return SellerProfile.objects.get(id=seller_profile_id)

def get_reviews_by_seller(*, seller_profile) -> QuerySet:
    return Review.objects.filter(seller=seller_profile).order_by('-created_at')

def get_review(*, reviewer, seller_profile) -> Review:
    return Review.objects.get(reviewer=reviewer, seller=seller_profile)

def get_review_by_id(*, review_id: int) -> Review:
    return Review.objects.get(id=review_id)
```

---

## listings/selectors.py

```python
from listings.models import Listing, Vehicle, Photo, Favorite, ListingView

def get_listing_by_id(*, listing_id: int) -> Listing:
    return Listing.objects.select_related('vehicle', 'seller').get(id=listing_id)

def get_listing_by_slug(*, slug: str) -> Listing:
    return Listing.objects.select_related('vehicle', 'seller').get(slug=slug)

def get_active_listings() -> QuerySet:
    return Listing.objects.filter(status='active').select_related('vehicle', 'seller').prefetch_related('photos')

def get_listings_by_seller(*, seller) -> QuerySet:
    return Listing.objects.filter(seller=seller).select_related('vehicle').prefetch_related('photos')

def get_photo_by_id(*, photo_id: int) -> Photo:
    return Photo.objects.get(id=photo_id)

def get_photos_by_listing(*, listing) -> QuerySet:
    return Photo.objects.filter(listing=listing).order_by('order')

def get_favorite(*, user, listing) -> Favorite:
    return Favorite.objects.get(user=user, listing=listing)

def get_favorites_by_user(*, user) -> QuerySet:
    return Favorite.objects.filter(user=user).select_related('listing__vehicle')

def get_listing_views(*, listing, days: int = 30) -> QuerySet:
    from django.utils import timezone
    from datetime import timedelta
    since = timezone.now() - timedelta(days=days)
    return ListingView.objects.filter(listing=listing, viewed_at__gte=since)

def search_listings(*, filters: dict) -> QuerySet:
    # filters keys: listing_type, make, model, year_min, year_max,
    #               price_min, price_max, fuel_type, transmission,
    #               body_type, city, ordering
    qs = Listing.objects.filter(status='active').select_related('vehicle').prefetch_related('photos')
    if filters.get('listing_type'):
        qs = qs.filter(listing_type=filters['listing_type'])
    if filters.get('make'):
        qs = qs.filter(vehicle__make__icontains=filters['make'])
    if filters.get('model'):
        qs = qs.filter(vehicle__model__icontains=filters['model'])
    if filters.get('year_min'):
        qs = qs.filter(vehicle__year__gte=filters['year_min'])
    if filters.get('year_max'):
        qs = qs.filter(vehicle__year__lte=filters['year_max'])
    if filters.get('price_min'):
        qs = qs.filter(price__gte=filters['price_min'])
    if filters.get('price_max'):
        qs = qs.filter(price__lte=filters['price_max'])
    if filters.get('fuel_type'):
        qs = qs.filter(vehicle__fuel_type=filters['fuel_type'])
    if filters.get('transmission'):
        qs = qs.filter(vehicle__transmission=filters['transmission'])
    if filters.get('body_type'):
        qs = qs.filter(vehicle__body_type=filters['body_type'])
    if filters.get('city'):
        qs = qs.filter(city__icontains=filters['city'])
    ordering = filters.get('ordering', '-created_at')
    return qs.order_by(ordering)
```

---

## offers/selectors.py

```python
from offers.models import Offer

def get_offer_by_id(*, offer_id: int) -> Offer:
    return Offer.objects.select_related('listing', 'buyer').get(id=offer_id)

def get_offers_by_listing(*, listing) -> QuerySet:
    return Offer.objects.filter(listing=listing).select_related('buyer').order_by('-created_at')

def get_offers_by_buyer(*, buyer) -> QuerySet:
    return Offer.objects.filter(buyer=buyer).select_related('listing').order_by('-created_at')

def get_pending_offer(*, buyer, listing) -> Offer:
    return Offer.objects.get(buyer=buyer, listing=listing, status='pending')

def get_expired_offers() -> QuerySet:
    from django.utils import timezone
    return Offer.objects.filter(status='pending', expires_at__lte=timezone.now())

def get_offer_chain(*, root_offer) -> QuerySet:
    # Returns all offers in chain starting from root
    ids = []
    current = root_offer
    while current is not None:
        ids.append(current.id)
        current = Offer.objects.filter(parent_offer=current).first()
    return Offer.objects.filter(id__in=ids).order_by('created_at')
```

---

## bookings/selectors.py

```python
from bookings.models import Booking, UnavailableDate

def get_booking_by_id(*, booking_id: int) -> Booking:
    return Booking.objects.select_related('listing', 'renter').get(id=booking_id)

def get_bookings_by_renter(*, renter) -> QuerySet:
    return Booking.objects.filter(renter=renter).select_related('listing').order_by('-created_at')

def get_bookings_by_listing(*, listing) -> QuerySet:
    return Booking.objects.filter(listing=listing).select_related('renter').order_by('-created_at')

def get_active_bookings() -> QuerySet:
    from django.utils import timezone
    return Booking.objects.filter(status='confirmed', end_date__lt=timezone.now().date())

def get_unavailable_dates(*, listing) -> QuerySet:
    return UnavailableDate.objects.filter(listing=listing)

def get_unavailable_date_by_id(*, unavailable_date_id: int) -> UnavailableDate:
    return UnavailableDate.objects.get(id=unavailable_date_id)
```

---

## messaging/selectors.py

```python
from messaging.models import Conversation, Message

def get_conversation_by_id(*, conversation_id: int) -> Conversation:
    return Conversation.objects.select_related('listing', 'buyer', 'seller').get(id=conversation_id)

def get_conversation(*, buyer, listing) -> Conversation:
    return Conversation.objects.get(buyer=buyer, listing=listing)

def get_conversations_by_user(*, user) -> QuerySet:
    from django.db.models import Q
    return Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).select_related('listing', 'buyer', 'seller').order_by('-updated_at')

def get_messages_by_conversation(*, conversation) -> QuerySet:
    return Message.objects.filter(conversation=conversation).order_by('created_at')

def get_message_by_id(*, message_id: int) -> Message:
    return Message.objects.get(id=message_id)

def get_unread_messages(*, user, conversation) -> QuerySet:
    return Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=user)
```

---

## notifications/selectors.py

```python
from notifications.models import Notification

def get_notification_by_id(*, notification_id: int) -> Notification:
    return Notification.objects.get(id=notification_id)

def get_notifications_by_user(*, user) -> QuerySet:
    return Notification.objects.filter(recipient=user).order_by('-created_at')

def get_unread_notifications(*, user) -> QuerySet:
    return Notification.objects.filter(recipient=user, is_read=False)
```

---

## dashboard/selectors.py

```python
from listings.models import Listing, ListingView, Favorite
from offers.models import Offer
from bookings.models import Booking
from messaging.models import Conversation

def get_seller_listings(*, seller) -> QuerySet:
    return Listing.objects.filter(seller=seller).select_related('vehicle').prefetch_related('photos')

def get_listing_view_count(*, listing) -> int:
    return ListingView.objects.filter(listing=listing).count()

def get_listing_offer_count(*, listing) -> int:
    return Offer.objects.filter(listing=listing).count()

def get_listing_pending_offer_count(*, listing) -> int:
    return Offer.objects.filter(listing=listing, status='pending').count()

def get_listing_message_count(*, listing) -> int:
    return Conversation.objects.filter(listing=listing).count()

def get_seller_total_views(*, seller) -> int:
    return ListingView.objects.filter(listing__seller=seller).count()

def get_seller_total_favorites(*, seller) -> int:
    return Favorite.objects.filter(listing__seller=seller).count()

def get_seller_pending_offers(*, seller) -> int:
    return Offer.objects.filter(listing__seller=seller, status='pending').count()

def get_seller_active_bookings(*, seller) -> int:
    return Booking.objects.filter(listing__seller=seller, status='confirmed').count()
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py test accounts listings offers bookings messaging notifications dashboard
```
Manually verify:
- Each selector raises ObjectDoesNotExist for non-existent records
- search_listings returns empty queryset for no matches (not an error)
- get_active_listings returns only status='active' listings
- get_expired_offers returns only pending offers past expires_at
Expected: 0 errors, 0 failures.
Report any errors before proceeding to next file.
