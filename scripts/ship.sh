#!/usr/bin/env bash
# ship.sh — Deploy learn-hub to production
# Usage: ./scripts/ship.sh [image_tag]
set -euo pipefail

APP_NAME="learn-hub"
SERVER="88.198.191.108"
DEPLOY_PATH="/opt/learn-hub"
COMPOSE_FILE="docker-compose.prod.yml"
HEALTH_URL="https://learn.iil.pet/healthz/"
IMAGE_TAG="${1:-latest}"

echo "=== Deploying ${APP_NAME} (tag: ${IMAGE_TAG}) ==="

echo "1. Syncing compose + config to server..."
ssh "root@${SERVER}" "mkdir -p ${DEPLOY_PATH}"
scp "${COMPOSE_FILE}" "root@${SERVER}:${DEPLOY_PATH}/"

echo "2. Pulling images..."
ssh "root@${SERVER}" "cd ${DEPLOY_PATH} && docker compose -f ${COMPOSE_FILE} pull"

echo "3. Running migrations..."
ssh "root@${SERVER}" "cd ${DEPLOY_PATH} && docker compose -f ${COMPOSE_FILE} run --rm migrate"

echo "4. Starting services..."
ssh "root@${SERVER}" "cd ${DEPLOY_PATH} && docker compose -f ${COMPOSE_FILE} up -d"

echo "5. Health check..."
for i in $(seq 1 10); do
    if curl -sf "${HEALTH_URL}" > /dev/null 2>&1; then
        echo "✅ ${APP_NAME} is healthy at ${HEALTH_URL}"
        exit 0
    fi
    echo "  Waiting... (${i}/10)"
    sleep 5
done

echo "❌ Health check failed after 50s"
exit 1
