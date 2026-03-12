# Stage 1: Build
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements/ requirements/
RUN pip install --no-cache-dir --prefix=/install -r requirements/base.txt

# Stage 2: Runtime
FROM python:3.12-slim

LABEL org.opencontainers.image.title="learn-hub" \
      org.opencontainers.image.description="Central Learning Management Hub (ADR-140)" \
      org.opencontainers.image.source="https://github.com/achimdehnert/learn-hub" \
      org.opencontainers.image.vendor="IIL"

RUN groupadd -g 1000 app && useradd -u 1000 -g app -m app

COPY --from=builder /install /usr/local

WORKDIR /app
COPY . .

RUN DJANGO_SECRET_KEY=build-placeholder python manage.py collectstatic --noinput

USER app:app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/livez/')"

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
