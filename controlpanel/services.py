from django.contrib.auth import get_user_model
from listings.models import Listing, ListingReport

User = get_user_model()


def toggle_user_active(*, user_id: int) -> User:
    u = User.objects.get(id=user_id)
    u.is_active = not u.is_active
    u.save(update_fields=['is_active'])
    return u


def verify_seller(*, user_id: int) -> User:
    u = User.objects.get(id=user_id)
    if hasattr(u, 'seller_profile'):
        u.seller_profile.is_verified = True
        u.seller_profile.save(update_fields=['is_verified'])
    return u


def delete_listing_admin(*, listing_id: int) -> None:
    Listing.objects.filter(id=listing_id).delete()


def set_listing_status_admin(*, listing_id: int, status: str) -> Listing:
    valid = ['active', 'passive', 'pending', 'sold', 'rented']
    if status not in valid:
        raise ValueError('Geçersiz durum.')
    listing = Listing.objects.get(id=listing_id)
    listing.status = status
    listing.save(update_fields=['status'])
    return listing


def resolve_report(*, report_id: int) -> ListingReport:
    report = ListingReport.objects.get(id=report_id)
    report.is_resolved = True
    report.save(update_fields=['is_resolved'])
    return report


def log_activity(*, actor, action: str, description: str):
    from controlpanel.models import ActivityLog
    ActivityLog.objects.create(actor=actor, action=action, description=description)
