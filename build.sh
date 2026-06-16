#!/usr/bin/env bash
# Render "Build Command" tarafından çalıştırılır.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
