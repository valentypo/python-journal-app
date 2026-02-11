from flask import Blueprint, request, jsonify
from app.services.rag_service_langchain import (
    index_journal_entry,
    chat_with_journal
)

rag_bp = Blueprint("rag", __name__, url_prefix="/rag")


@rag_bp.post("/index")
def index_journal():
    """
    Index a journal entry into vector DB
    Expected JSON:
    {
        "journal_id": "...",
        "title": "...",
        "content": "...",
        "date": "YYYY-MM-DD"
    }
    """
    data = request.get_json()

    journal_id = data.get("journal_id")
    title = data.get("title")
    content = data.get("content")
    date = data.get("date")

    if not all([journal_id, title, content, date]):
        return jsonify({"error": "Missing fields"}), 400

    chunks_added = index_journal_entry(
        journal_id=journal_id,
        title=title,
        content=content,
        date=date
    )

    return jsonify({
        "status": "indexed",
        "chunks_added": chunks_added,
        "journal_id": journal_id
    }), 200



@rag_bp.post("/chat")
def chat():
    """
    Chat with journal memory
    Expected JSON:
    {
        "query": "user question",
        "top_k": 5
    }
    """
    data = request.get_json()

    query = data.get("query")
    top_k = data.get("top_k", 5)

    if not query:
        return jsonify({"error": "Query is required"}), 400

    result = chat_with_journal(query=query, top_k=top_k)

    return jsonify(result), 200