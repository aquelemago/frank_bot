from __future__ import annotations

from app.config.models import EmailQueueSettings
from app.csv.io import normalize_key
from app.queue.attendant_emails import load_attendant_emails
from app.queue.grouping import group_by_attendant
from app.queue.repository import (
    EmailQueue,
    EmailQueueError,
    EmailQueueItem,
    build_attendant_email_queue,
    mark_queue_item_failed,
    mark_queue_item_sent,
    slugify,
)


__all__ = [
    "EmailQueue",
    "EmailQueueError",
    "EmailQueueItem",
    "EmailQueueSettings",
    "build_attendant_email_queue",
    "group_by_attendant",
    "load_attendant_emails",
    "mark_queue_item_failed",
    "mark_queue_item_sent",
    "normalize_key",
    "slugify",
]
