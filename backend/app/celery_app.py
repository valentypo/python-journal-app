from celery import Celery
import os

# Create a Celery instance without importing the Flask app at import-time.
# The Flask app should call `make_celery(app)` after the app is created.
broker = os.getenv("CELERY_BROKER_URL", "redis://journal_redis:6379/0")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://journal_redis:6379/0")

celery = Celery(__name__, broker=broker, backend=backend)

def make_celery(app):
    celery.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL", broker),
        result_backend=app.config.get("CELERY_RESULT_BACKEND", backend),
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery