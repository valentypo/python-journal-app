import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from app.celery_app import make_celery
from app.journal_routes import journal_bp
from app.rag_routes import rag_bp


def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )
    

    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL")
    app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND")


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
    app.register_blueprint(rag_bp)

    return app
