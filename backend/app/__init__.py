import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

from app.journal_routes import journal_bp


def create_app():
    load_dotenv()  # loads .env into environment variables

    app = Flask(__name__)
    CORS(app)

    # Mongo connection
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MONGODB_URI is missing. Add it to your .env file.")

    client = MongoClient(mongo_uri)
    db = client["journal_db"]

    # store db on app so routes can access it
    app.db = db

    app.register_blueprint(journal_bp)

    return app
