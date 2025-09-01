#!/bin/bash

# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Debug: Print Python path and current directory
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Contents of src:"
ls -la src/

# Start based on the service type
if [ "$RAILWAY_SERVICE_NAME" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A src.app.core.celery_worker worker --loglevel=info
else
    echo "Starting FastAPI web server..."
    exec uvicorn src.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
fi
