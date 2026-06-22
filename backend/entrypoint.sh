#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn with Uvicorn workers..."
exec gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8005 \
    -w ${GUNICORN_WORKERS:-4} \
    --max-requests 10000 \
    --max-requests-jitter 2000 \
    --access-logfile - \
    --error-logfile -
