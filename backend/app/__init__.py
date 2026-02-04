from flask import Flask
from flask_cors import CORS

from app.journal_routes import journal_bp


def create_app():
    app = Flask(__name__)

    # Allow frontend to call backend without CORS errors
    CORS(app)

    # Blueprint routes
    app.register_blueprint(journal_bp)

    return app
