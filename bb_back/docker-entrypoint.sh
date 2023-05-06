#!/bin/bash

# Make database migrations
echo "Make database migrations"
python manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate
python manage.py migrate core

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000