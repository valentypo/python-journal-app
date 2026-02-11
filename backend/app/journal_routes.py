from flask import Blueprint, request, jsonify, current_app
from celery.result import AsyncResult
from typing import List
from pydantic import ValidationError
from datetime import datetime
from bson import ObjectId
from app.serializers import serialize_entry
from app.tasks import summarize_entries_task
from app.utils import get_date_range
from app.schemas import JournalEntry, JournalEntryCreate, JournalEntryUpdate
from app.services.rag_service_langchain import index_journal_entry

journal_bp = Blueprint("journal", __name__)


@journal_bp.get("/entries")
def get_entries():
    entries_collection = current_app.db.entries

    docs = list(entries_collection.find().sort("created_at", -1))
    entries: List[JournalEntry] = [serialize_entry(d) for d in docs]

    return jsonify([e.model_dump() for e in entries]), 200


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
    entry: JournalEntry = serialize_entry(created)
    
    # auto index to RAG vector DB
    try:
        index_journal_entry(
            journal_id=str(result.inserted_id),
            title=entry.title,
            content=entry.content,
            date=entry.created_at[:10]
        )
    except Exception as e:
        print("RAG indexing failed:", e)

    return jsonify(entry.model_dump()), 201



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
    entry = serialize_entry(updated)
    return jsonify(entry.model_dump()), 200


@journal_bp.delete("/entries/<entry_id>")
def delete_entry(entry_id):
    entries_collection = current_app.db.entries

    result = entries_collection.delete_one({"_id": ObjectId(entry_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Deleted"}), 200


@journal_bp.post("/entries/summarize/<period>")
def summarize(period):
    start, end = get_date_range(period)
    # dispatch Celery task to summarize entries for the period
    task = summarize_entries_task.delay(period, start, end)

    return jsonify({
        "task_id": task.id,
        "status": "processing"
    }), 202

@journal_bp.get("/tasks/<task_id>")
def get_task(task_id):
    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "state": task.state
    }

    if task.state == "PENDING":
        response["message"] = "Task queued"

    elif task.state == "STARTED":
        response["message"] = "Task running"

    elif task.state == "SUCCESS":
        response["summary"] = task.result   # <-- returned value
        response["message"] = "Completed"

    elif task.state == "FAILURE":
        response["message"] = str(task.result)

    return jsonify(response)