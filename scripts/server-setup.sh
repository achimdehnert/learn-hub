#!/usr/bin/env bash
# server-setup.sh — First-time server setup for learn-hub on 88.198.191.108
# Run this ONCE from your local machine (NOT on the server directly).
# Usage: bash scripts/server-setup.sh
set -euo pipefail

SERVER="88.198.191.108"
DEPLOY_PATH="/opt/learn-hub"

echo "=== learn-hub Server Setup (ADR-140) ==="
echo "Server: ${SERVER}"
echo "Path:   ${DEPLOY_PATH}"
echo ""

# 1. Create directory + clone repo
echo "1. Creating ${DEPLOY_PATH} and cloning repo..."
ssh "root@${SERVER}" <<'SETUP'
set -euo pipefail
mkdir -p /opt/learn-hub
cd /opt/learn-hub
if [ ! -d .git ]; then
    git clone https://github.com/achimdehnert/learn-hub.git .
else
    git pull origin main
fi
SETUP

# 2. Generate secrets and create .env files
echo "2. Creating .env.prod and .env.db..."
DJANGO_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(24))")

ssh "root@${SERVER}" bash -s -- "${DJANGO_SECRET}" "${DB_PASSWORD}" <<'ENVSETUP'
set -euo pipefail
DJANGO_SECRET="$1"
DB_PASSWORD="$2"

cat > /opt/learn-hub/.env.prod <<EOF
DJANGO_SECRET_KEY=${DJANGO_SECRET}
DEBUG=False
ALLOWED_HOSTS=learn.iil.pet,localhost,127.0.0.1

DATABASE_NAME=learn_hub
DATABASE_USER=learn_hub_app
DATABASE_PASSWORD=${DB_PASSWORD}
DATABASE_HOST=db
DATABASE_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

LOG_LEVEL=INFO
EOF

cat > /opt/learn-hub/.env.db <<EOF
POSTGRES_DB=learn_hub
POSTGRES_USER=learn_hub_app
POSTGRES_PASSWORD=${DB_PASSWORD}
EOF

chmod 600 /opt/learn-hub/.env.prod /opt/learn-hub/.env.db
echo "  .env files created with strong secrets"
ENVSETUP

# 3. Install Nginx config
echo "3. Installing Nginx config..."
scp deployment/nginx/prod/learn.iil.pet.conf "root@${SERVER}:/etc/nginx/sites-available/learn.iil.pet.conf" 2>/dev/null || \
ssh "root@${SERVER}" bash -s <<'NGINX'
cat > /etc/nginx/sites-available/learn.iil.pet.conf <<'CONF'
server {
    listen 80;
    server_name learn.iil.pet;

    location /livez/ {
        proxy_pass http://127.0.0.1:8099;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /healthz/ {
        proxy_pass http://127.0.0.1:8099;
        proxy_set_header Host $host;
    }
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name learn.iil.pet;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8099;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }
    location /static/ {
        proxy_pass http://127.0.0.1:8099;
        proxy_set_header Host $host;
        expires 1h;
        add_header Cache-Control "public";
    }
}
CONF

ln -sf /etc/nginx/sites-available/learn.iil.pet.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
echo "  Nginx configured and reloaded"
NGINX

# 4. Start containers
echo "4. Starting Docker containers..."
ssh "root@${SERVER}" <<'DOCKER'
set -euo pipefail
cd /opt/learn-hub
docker compose -f docker-compose.prod.yml pull 2>/dev/null || true
docker compose -f docker-compose.prod.yml run --rm migrate 2>/dev/null || echo "  Migration service will run on first compose up"
docker compose -f docker-compose.prod.yml up -d
echo "  Containers started"
docker compose -f docker-compose.prod.yml ps
DOCKER

# 5. SSL Certificate
echo "5. Provisioning SSL certificate..."
ssh "root@${SERVER}" "certbot --nginx -d learn.iil.pet --non-interactive --agree-tos -m achim@dehnert.com 2>/dev/null || echo '  SSL: Run manually: certbot --nginx -d learn.iil.pet'"

# 6. Health check
echo "6. Health check..."
sleep 10
for i in $(seq 1 10); do
    if curl -sf "http://${SERVER}:8099/livez/" > /dev/null 2>&1; then
        echo "✅ learn-hub is healthy!"
        exit 0
    fi
    echo "  Waiting... (${i}/10)"
    sleep 5
done

echo "⚠️  Health check via external URL pending (DNS propagation may take time)"
echo "   Check directly: curl http://${SERVER}:8099/livez/"
echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Add DNS A record: learn.iil.pet → ${SERVER} (Cloudflare)"
echo "  2. Verify: curl https://learn.iil.pet/healthz/"
