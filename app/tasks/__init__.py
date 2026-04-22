# This module provides task queue handling via Celery

from .celery_app import celery_app

__all__ = ['celery_app']
