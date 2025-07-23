#!/bin/sh
#echo "Waiting for postgres..."
#/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Postgres is up"

set -e

echo "Running migrations..."
uv run python manage.py makemigrations --noinput  # --check
uv run python manage.py migrate # 실행 전에 migrate 자동실행

echo "Starting server..."
#uv run gunicorn config.wsgi:application \
#  --bind 0.0.0.0:8000 \
#  --workers 2 \
#  --log-level debug
uv run python manage.py runserver 0.0.0.0:8000
