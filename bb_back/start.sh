#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
gunicorn bb_back.wsgi:application --bind 0:8000