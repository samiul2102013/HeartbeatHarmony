#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8005 config.asgi:application
