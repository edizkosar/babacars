from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from babacars import pwa_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Spesifik prefix'li uygulamalar önce gelir
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('offers/', include('offers.urls', namespace='offers')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('alerts/', include('alerts.urls', namespace='alerts')),
    path('api/v1/', include('api.urls', namespace='api')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path('control-panel/', include('controlpanel.urls', namespace='controlpanel')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # PWA — kök kapsamdan servis edilir
    path('manifest.webmanifest', pwa_views.manifest_view, name='manifest'),
    path('sw.js', pwa_views.service_worker_view, name='service_worker'),
    path('offline/', pwa_views.offline_view, name='offline'),
    # Listings en sona: '<slug>/' catch-all içerdiği için diğerlerini ezmemeli
    path('', include('listings.urls', namespace='listings')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
