web: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A src.app.core.celery_worker worker --loglevel=info
