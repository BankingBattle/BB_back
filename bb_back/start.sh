#!/bin/sh
python manage.py makemigrations
python manage.py migrate core
python manage.py collectstatic --no-input
gunicorn bb_back.wsgi:application --bind 0:8000