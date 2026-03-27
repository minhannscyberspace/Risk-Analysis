#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"

echo "Checking backend health at ${BASE_URL}/api/health"
curl -fsS "${BASE_URL}/api/health" >/dev/null

echo "Checking backend readiness at ${BASE_URL}/api/ready"
curl -fsS "${BASE_URL}/api/ready" >/dev/null

echo "Backend health check passed."
