# settings_middleware.md

## Reference
See PROJECT_OVERVIEW.md for stack, deployment and app list.

## Purpose
Django project settings and custom middleware for offer expiry and booking completion.

---

## babacars/settings.py

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    # Local
    'accounts',
    'listings',
    'offers',
    'bookings',
    'messaging',
    'notifications',
    'dashboard',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'babacars.middleware.OfferExpiryMiddleware',
    'babacars.middleware.BookingCompletionMiddleware',
]

ROOT_URLCONF = 'babacars.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'babacars.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'listings:index'
LOGOUT_REDIRECT_URL = 'listings:index'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@babacars.com'
```

---

## babacars/middleware.py

```python
from offers.services import expire_stale_offers
from bookings.services import complete_booking
from bookings import selectors as booking_selectors


class OfferExpiryMiddleware:
    """
    Checks and expires stale offers on every request.
    Lightweight — only runs a bulk update query.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        expire_stale_offers()
        response = self.get_response(request)
        return response


class BookingCompletionMiddleware:
    """
    Checks and completes bookings whose end_date has passed on every request.
    Lightweight — only runs a bulk update query.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        active_bookings = booking_selectors.get_active_bookings()
        for booking in active_bookings:
            try:
                complete_booking(booking_id=booking.id)
            except ValueError:
                pass
        response = self.get_response(request)
        return response
```

---

## Healthcheck
After implementation run:
```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```
Manually verify:
- Server starts without errors
- /admin/ accessible
- AUTH_USER_MODEL = 'accounts.User' applied
- TIME_ZONE = 'Europe/Istanbul' applied
- Static files served correctly
- Media files served correctly in development
Expected: 0 errors, server starts cleanly.
Report any errors before proceeding to next file.

---

## PROMPT

### Context Files (must be read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- offers_services.md
- bookings_services.md
- selectors.md

### Task
Implement settings.py and middleware.py exactly as defined in this document.

### Files to Create
- babacars/settings.py
- babacars/middleware.py

### Rules
1. Copy settings.py exactly as written. Do NOT add or remove installed apps.
2. SECRET_KEY and DEBUG must be read from environment variables.
3. Middleware order is critical — do NOT reorder.
4. OfferExpiryMiddleware calls expire_stale_offers() from offers/services.py.
5. BookingCompletionMiddleware calls complete_booking() from bookings/services.py.
6. EMAIL_BACKEND uses console backend — no SMTP setup required.
7. Run Healthcheck after both files are created.

### Output
One code block per file. No explanations.
