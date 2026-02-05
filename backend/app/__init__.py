import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

from app.journal_routes import journal_bp


def create_app():
    load_dotenv()  # loads .env into environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    app = Flask(__name__)
    CORS(app)

    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    if not app.config["OPENAI_API_KEY"]:
        raise RuntimeError("OPENAI_API_KEY not found")
    
    # Mongo connection
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI is not found.")

    client = MongoClient(mongo_uri)
    db = client["journal_db"]

    # store db on app so routes can access it
    app.db = db

    app.register_blueprint(journal_bp)

    return app
