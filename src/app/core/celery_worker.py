from celery import Celery
import os
import sys
from pathlib import Path

#Correct imports

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configuración del worker de Celery
celery = Celery(
    'worker',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),  # Railway uses REDIS_URL
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
)

celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)

# Import tasks to register them with Celery
try:
    from app.tasks import bill_task
except ImportError:
    # If direct import fails, try with the full path
    from src.app.tasks import bill_task
