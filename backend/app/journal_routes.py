from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
from datetime import datetime
from bson import ObjectId

from app.schemas import JournalEntryCreate, JournalEntryUpdate

journal_bp = Blueprint("journal", __name__)


def serialize_entry(entry):
    """Convert MongoDB document into JSON-safe dict"""
    return {
        "id": str(entry["_id"]),
        "title": entry["title"],
        "content": entry["content"],
        "created_at": entry["created_at"],
        "updated_at": entry["updated_at"],
    }

@journal_bp.get("/entries")
def get_entries():
    entries_collection = current_app.db.entries
    entries = list(entries_collection.find().sort("created_at", -1))

    return jsonify([serialize_entry(e) for e in entries]), 200


@journal_bp.post("/entries")
def create_entry():
    entries_collection = current_app.db.entries

    try:
        data = request.get_json() or {}
        entry_data = JournalEntryCreate(**data)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.errors()}), 400

    now = datetime.now().isoformat()

    new_entry = {
        "title": entry_data.title,
        "content": entry_data.content,
        "created_at": now,
        "updated_at": now,
    }

    result = entries_collection.insert_one(new_entry)
    print("Inserted ID:", result.inserted_id)

    created = entries_collection.find_one({"_id": result.inserted_id})
    return jsonify(serialize_entry(created)), 201


@journal_bp.put("/entries/<entry_id>")
def update_entry(entry_id):
    entries_collection = current_app.db.entries

    try:
        data = request.get_json() or {}
        update_data = JournalEntryUpdate(**data)
    except ValidationError as e:
        return jsonify({"error": "Invalid data", "details": e.errors()}), 400

    updates = {}
    if update_data.title is not None:
        updates["title"] = update_data.title
    if update_data.content is not None:
        updates["content"] = update_data.content

    if not updates:
        return jsonify({"error": "No fields provided to update"}), 400

    updates["updated_at"] = datetime.now().isoformat()

    result = entries_collection.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": updates}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    updated = entries_collection.find_one({"_id": ObjectId(entry_id)})
    return jsonify(serialize_entry(updated)), 200


@journal_bp.delete("/entries/<entry_id>")
def delete_entry(entry_id):
    entries_collection = current_app.db.entries

    result = entries_collection.delete_one({"_id": ObjectId(entry_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Deleted"}), 200