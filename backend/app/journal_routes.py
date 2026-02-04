from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from datetime import datetime
from uuid import uuid4

from app.schemas import JournalEntryCreate

journal_bp = Blueprint("journal", __name__)

# Temporary "database" stored in memory
ENTRIES = []

@journal_bp.get("/entries")
def get_entries():
    return jsonify(ENTRIES), 200


@journal_bp.post("/entries")
def create_entry():

    try:
        data = request.get_json() or {}
        entry_data = JournalEntryCreate(**data)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.errors()}), 400

    new_entry = {
        "id": uuid4(),
        "title": entry_data.title,
        "content": entry_data.content,
        "created_at": datetime.now().isoformat()
    }

    ENTRIES.append(new_entry)

    return jsonify(new_entry), 201


@journal_bp.put("/entries/<int:entry_id>")
def update_entry(entry_id):
    data = request.get_json() or {}

    # find entry
    for entry in ENTRIES:
        if entry["id"] == entry_id:
            # update only fields sent
            if "title" in data:
                entry["title"] = data["title"]
            if "content" in data:
                entry["content"] = data["content"]

            return jsonify(entry), 200

    return jsonify({"error": "Entry not found"}), 404


@journal_bp.delete("/entries/<int:entry_id>")
def delete_entry(entry_id):
    global ENTRIES

    for entry in ENTRIES:
        if entry["id"] == entry_id:
            ENTRIES = [e for e in ENTRIES if e["id"] != entry_id]
            return jsonify({"message": "Deleted"}), 200

    return jsonify({"error": "Entry not found"}), 404