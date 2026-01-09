#!/bin/bash
# Start Celery worker for background task processing
# Make sure Redis is running before starting Celery

echo "Starting Celery worker..."
echo ""

cd "$(dirname "$0")"
source venv/bin/activate

celery -A legalease worker --loglevel=info

