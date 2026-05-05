"""
Celery configuration for Faculty Scheduling System
"""
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('faculty_scheduling')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks()

# Optional: configure Celery
app.conf.update(
    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE='UTC',
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
