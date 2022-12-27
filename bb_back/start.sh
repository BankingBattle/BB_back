#!/bin/sh
python manage.py makemigrations
python manage.py migrate
gunicorn bb_back.wsgi:application --bind 0:8000