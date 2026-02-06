from celery import Celery
import os

# Create a Celery instance without importing the Flask app at import-time.
# The Flask app should call `make_celery(app)` after the app is created.
broker = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

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


# If this module is imported by a standalone Celery worker, ensure the
# Celery `Task` base class wraps execution with the Flask application
# context so `current_app` is available inside tasks. We try to create
# the Flask app and call `make_celery()` here; if it fails (for example
# during local imports where env isn't set), we silently skip it.
try:
    from app import create_app

    _app = create_app()
    make_celery(_app)
except Exception:
    # don't raise during import-time; worker or web container will
    # still call `make_celery()` when appropriate
    pass