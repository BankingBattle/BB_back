#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn bb_back.wsgi:application --bind 0:8000