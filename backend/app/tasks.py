from app.services.summarization import summarize_and_store
from app.celery_app import celery


@celery.task(bind=True)
def summarize_entries_task(self, period, start, end):
    summary = summarize_and_store(period, start, end)
    return summary