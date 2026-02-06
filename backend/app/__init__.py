import os
from flask import Flask, app
from flask_cors import CORS
from app.celery_app import make_celery
from dotenv import load_dotenv
from pymongo import MongoClient

from app.journal_routes import journal_bp


def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    app.config["CELERY_BROKER_URL"] = "redis://redis:6379/0" # redis itu nama service redis di docker-compose
    app.config["CELERY_RESULT_BACKEND"] = "redis://redis:6379/0"


    if not app.config["OPENAI_API_KEY"]:
        raise RuntimeError("OPENAI_API_KEY not found")

    # Mongo
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("MONGODB_URI not found")

    client = MongoClient(mongo_uri)
    app.db = client["journal_db"]

    make_celery(app)

    app.register_blueprint(journal_bp)

    return app
