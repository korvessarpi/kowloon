FROM python:3.11-slim

# Common build/runtime deps to avoid pip build failures (Pillow, psycopg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev libffi-dev libssl-dev \
    libjpeg-dev zlib1g-dev libpng-dev libopenjp2-7-dev libtiff5-dev libwebp-dev \
    libfreetype6-dev liblcms2-dev libpq-dev git curl netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . /app

ENV PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=server.conf.production_settings

# Non-root user
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# IMPORTANT: we point to the file that exists after the bind mount (./:/app)
ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint.sh"]

EXPOSE 4000 4001
