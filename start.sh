#!/usr/bin/env bash
set -e
cd /app || exit 1

echo "Starting Kowloon (Evennia)…"

# optional: activate venv if you use one
if [ -d venv ]; then
  source venv/bin/activate
fi

if [[ -f manage.py ]]; then
  echo "Django mode detected: running migrations"
  python manage.py migrate --noinput || true
  python manage.py collectstatic --noinput || true
else
  echo "Evennia mode detected: starting server"
  python -m evennia migrate || true
  python -m evennia start -l
fi

# keep container alive and stream logs
exec tail -F server/logs/portal.log server/logs/server.log

