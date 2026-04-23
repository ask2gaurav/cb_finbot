#!/bin/bash
# Runs after docker compose up
echo "Running smoke tests..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HTTP_CODE" -eq 200 ]; then
  echo "Backend Health Check: PASSED"
else
  echo "Backend Health Check: FAILED with code $HTTP_CODE"
fi
echo "Smoke test complete."
