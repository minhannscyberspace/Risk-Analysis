#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:5173}"

echo "Checking frontend root at ${BASE_URL}"
curl -fsS "${BASE_URL}" >/dev/null
echo "Frontend smoke check passed."
