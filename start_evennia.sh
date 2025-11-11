#!/bin/bash

# Evennia startup script for Docker container with SQLite
set -e

echo "=== Starting Evennia with SQLite ==="
echo "Time: $(date)"

# Change to the app directory
cd /app

# Install any new requirements
pip install -r requirements.txt

# Run Django migrations
echo "Running database migrations..."
evennia migrate --noinput

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('Daloa', 'admin@example.com', 'russell100')
    print("Created superuser: Daloa")
else:
    print("Superuser already exists")
EOF

# Collect static files
echo "Collecting static files..."
evennia collectstatic --noinput

# Fix permissions
chmod -R 755 /app/server
chmod -R 666 /app/server/evennia.db3 2>/dev/null || echo "Database file will be created"

# Start Evennia
echo "Starting Evennia..."
evennia start -l

# Keep container running and tail logs
echo "Evennia started. Monitoring logs..."
tail -f /app/server/logs/server.log