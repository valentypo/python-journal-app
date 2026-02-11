import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# config
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "journal_db")
COLLECTION_NAME = "entries"

CHROMA_PATH = "data/chroma_journal"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# models
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

vector_db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80
)

# ================= CONNECT =================
mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]
collection = db[COLLECTION_NAME]

# ================= MIGRATION =================
def migrate():
    print("\nStarting vector migration (MongoDB → ChromaDB)\n")

    entries = list(collection.find())
    total = len(entries)

    print(f"Found {total} entries\n")

    indexed = 0

    for entry in entries:
        try:
            journal_id = str(entry["_id"])
            title = entry.get("title", "")
            content = entry.get("content", "")
            created_at = entry.get("created_at", "")

            date = created_at[:10] if created_at else datetime.utcnow().isoformat()[:10]

            base_text = f"Title: {title}\nDate: {date}\nContent: {content}"

            chunks = text_splitter.split_text(base_text)

            docs = []
            for i, chunk in enumerate(chunks):
                docs.append(Document(
                    page_content=chunk,
                    metadata={
                        "journal_id": journal_id,
                        "date": date,
                        "chunk": i
                    }
                ))

            vector_db.add_documents(docs)
            indexed += 1

            print(f"Indexed {indexed}/{total} | id={journal_id} | chunks={len(docs)}")

        except Exception as e:
            print(f"Failed {entry.get('_id')}: {e}")

    vector_db.persist()
    print("\nMigration completed successfully!")
    print(f"Total indexed: {indexed}/{total}\n")


if __name__ == "__main__":
    migrate()
