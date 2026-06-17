web: gunicorn babacars.wsgi:application --bind 0.0.0.0:$PORT --timeout 120
release: python manage.py migrate --noinput
