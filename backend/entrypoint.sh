#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if [ "${RUN_SETUP_DEMO:-1}" = "1" ]; then
  echo "Ensuring demo data..."
  python manage.py setup_demo || true
fi

PORT="${PORT:-8000}"
echo "Starting gunicorn on port ${PORT}..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -