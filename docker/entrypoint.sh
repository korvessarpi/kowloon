#!/usr/bin/env bash
set -Eeuo pipefail

cd /app

echo "Starting Kowloon (Evennia/Django)…"

# Graceful shutdown
cleanup() {
  echo "Stopping Evennia…"
  evennia stop || true
}
trap cleanup SIGTERM SIGINT

if [[ -f manage.py ]]; then
  echo "[Django mode] Applying migrations and collecting static"
  python manage.py migrate --noinput || true
  python manage.py collectstatic --noinput || true
else
  echo "[Evennia mode] No manage.py present"
fi

# Initialize logs dir so tail never exits
mkdir -p server/logs
touch server/logs/portal.log server/logs/server.log

# Try to run Evennia in foreground if available; otherwise start + tail
if evennia start -h 2>&1 | grep -q -- '--nodaemon'; then
  echo "Launching Evennia in foreground (--nodaemon)"
  # Run in foreground so this process stays attached
  evennia start -l --nodaemon &
else
  echo "Launching Evennia (daemon mode) and tailing logs"
  evennia start -l || true
fi

# Keep container in the foreground
tail -F server/logs/portal.log server/logs/server.log &
wait -n

