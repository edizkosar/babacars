from offers.services import expire_stale_offers
from bookings.services import complete_booking
from bookings import selectors as booking_selectors


class OfferExpiryMiddleware:
    """
    Checks and expires stale offers.
    Throttled: runs at most once every 60 seconds.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self._last_run = None

    def __call__(self, request):
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        if self._last_run is None or (now - self._last_run) > timedelta(seconds=60):
            try:
                expire_stale_offers()
                self._last_run = now
            except Exception:
                pass
        response = self.get_response(request)
        return response


class BookingCompletionMiddleware:
    """
    Checks and completes bookings whose end_date has passed.
    Throttled: runs at most once every 60 seconds.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self._last_run = None

    def __call__(self, request):
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        if self._last_run is None or (now - self._last_run) > timedelta(seconds=60):
            try:
                active_bookings = booking_selectors.get_active_bookings()
                for booking in active_bookings:
                    try:
                        complete_booking(booking_id=booking.id)
                    except ValueError:
                        pass
                self._last_run = now
            except Exception:
                pass
        response = self.get_response(request)
        return response


class AlertsCheckMiddleware:
    """
    Checks price alerts, saved searches, watchlist price changes.
    Throttled: runs at most once every 60 seconds per server (via cache timestamp in session).
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self._last_run = None

    def __call__(self, request):
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        if self._last_run is None or (now - self._last_run) > timedelta(seconds=60):
            try:
                from alerts.services import check_price_alerts, check_saved_searches, check_watchlist_price_changes
                check_price_alerts()
                check_saved_searches()
                check_watchlist_price_changes()
                self._last_run = now
            except Exception:
                pass
        return self.get_response(request)

