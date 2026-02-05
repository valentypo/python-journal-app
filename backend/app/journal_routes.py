from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, List
from pydantic import ValidationError
from datetime import datetime, date
from bson import ObjectId
from openai import OpenAI

from app.schemas import JournalEntry, JournalEntryCreate, JournalEntryUpdate

journal_bp = Blueprint("journal", __name__)

def serialize_entry(entry: Dict[str, Any]) -> JournalEntry:
    # convert MongoDB document into JSON-safe dict
    return JournalEntry(
        id = str(entry["_id"]),
        title = entry["title"],
        content = entry["content"],
        created_at = entry["created_at"],
        updated_at =  entry["updated_at"],
    )

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

@journal_bp.post("/entries/summarize")
def summarize_today(): # summarizes entry only for all entries made today.
    
    today = date.today().isoformat()
    start = f"{today}T00:00:00"
    end = f"{today}T23:59:59"

    entries_collection = current_app.db.entries

    entries = list(
        entries_collection.find({
            "created_at": {
                "$gte": start,
                "$lte": end
            }
        })
    )

    if not entries:
        return jsonify({"error": "No entries for today"}), 400
    
    journal_text = ""

    for i, entry in enumerate(entries, start=1):
        journal_text += f"""
        Entry {i}
        Title: {entry['title']}
        Content: {entry['content']}
        """

    client = OpenAI()
    
    system_prompt = """
        The text you received is user's journal from today's entry. 
        You must summarize their entry with a minimum length of 1 sentence and maximum length of 3 sentences, try to keep it balanced.
        If there are not enough contents you can add suggestion for the user's input.
        Make sure that you use a warm tone and explain as brief as possible, as user will prefer a shorter summarization.
    """
    
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "user", "content": journal_text},
            {"role":"system", "content": system_prompt}
        ],
    )
    
    summary_text = response.output_text
    
    return jsonify({"summary": summary_text}), 200