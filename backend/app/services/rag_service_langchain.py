from typing import List, Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
import os

# config
CHROMA_PATH = "data/chroma_journal"

# models and vector DB
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

vector_db = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80
)


def index_journal_entry(journal_id: str, title: str, content: str, date: str) -> int:
    """
    Index one journal entry into vector DB
    """
    base_text = f"Title: {title}\nDate: {date}\nContent: {content}"

    chunks: List[str] = text_splitter.split_text(base_text)

    # docs to store documents objects in chromaDB
    docs: List[Document] = []
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
    vector_db.persist()

    return len(docs)

# retriever
def get_retriever(top_k: int = 5) -> BaseRetriever:
    return vector_db.as_retriever(search_kwargs={"k": top_k})


CHAT_PROMPT = ChatPromptTemplate.from_template(
"""
You are a personal AI journal assistant.
You answer ONLY from the user's journal memory.

Context (journal memory):
{context}

User question:
{question}

Rules:
- Only use the journal context
- If data is missing, say you don't know
- Answer naturally, like a personal assistant
- Be clear and concise

Answer:
"""
)


# Chat with RAG
def chat_with_journal(query: str, top_k: int = 5) -> Dict[str, Any]:
    retriever = get_retriever(top_k)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": CHAT_PROMPT},
        return_source_documents=True
    )

    result = qa_chain.invoke({"query": query})

    sources: List[Dict[str, str]] = []
    for doc in result.get("source_documents", []):
        sources.append({
            "journal_id": doc.metadata.get("journal_id"),
            "date": doc.metadata.get("date")
        })

    return {
        "query": query,
        "answer": result.get("result"),
        "sources": sources,
        "created_at": datetime.utcnow().isoformat()
    }