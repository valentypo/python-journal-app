from app.celery_app import celery
from app.services.summarization import summarize_and_store

@celery.task
def summarize_entries_task(period: str, start: str, end: str):
    return summarize_and_store(period, start, end)