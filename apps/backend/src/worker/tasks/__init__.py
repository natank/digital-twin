"""Celery task modules.

Importing this package registers tasks on the shared Celery app.
"""

from src.worker.tasks import cv as cv  # noqa: F401
from src.worker.tasks import ping as ping  # noqa: F401
