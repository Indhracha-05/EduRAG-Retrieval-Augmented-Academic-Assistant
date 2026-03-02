"""
RAG pipeline — query embedding, retrieval, LLM generation, source & exam-probability extraction.
"""

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
import ollama

from src.prompts import get_prompt

# ── constants ────────────────────────────────────────────────────────
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
COLLECTION_NAME = "academic_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama3"
TOP_K = 5


# ── retrieval helpers ────────────────────────────────────────────────
def _get_collection():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
    )
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)


def _compute_exam_probability(metadatas: list[dict]) -> dict:
    """Estimate exam probability based on document types of retrieved chunks."""
    doc_types = {m.get("doc_type", "") for m in metadatas}

    if "past_paper" in doc_types:
        return {
            "level": "High",
            "emoji": "🔴",
            "reason": "Topic appears in past question papers.",
        }
    if doc_types & {"syllabus", "notes"}:
        return {
            "level": "Medium",
            "emoji": "🟡",
            "reason": "Topic found in syllabus or lecture notes.",
        }
    return {
        "level": "Low",
        "emoji": "🟢",
        "reason": "Topic not prominently featured in core materials.",
    }


def _format_sources(metadatas: list[dict]) -> list[dict]:
    """De-duplicate and format source references."""
    seen = set()
    sources = []
    for m in metadatas:
        key = (m["filename"], m["page"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "filename": m["filename"],
                "page": m["page"],
                "doc_type": m["doc_type"],
            })
    return sources


# ── public API ───────────────────────────────────────────────────────
def query(question: str, mode: str = "Detailed") -> dict:
    """
    Run the full RAG pipeline.

    Returns:
        dict with keys: answer, sources, exam_probability
    """
    collection = _get_collection()

    # Retrieve
    results = collection.query(query_texts=[question], n_results=TOP_K)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context
    context = "\n\n---\n\n".join(documents)

    # Build prompt
    prompt = get_prompt(mode, context, question)

    # Call LLM
    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response["message"]["content"]
    except Exception as e:
        # Fallback if Ollama is not running
        answer = (
            "⚠️ **Ollama Connection Error**\n\n"
            "The system was unable to connect to the Ollama service to generate a summary. "
            "However, I have successfully retrieved the following relevant information from your documents:\n\n"
            + context + 
            "\n\n---\n\n"
            "**Action Required**: Please ensure Ollama is installed and running on your system with the `llama3` model."
        )

    return {
        "answer": answer,
        "sources": _format_sources(metadatas),
        "exam_probability": _compute_exam_probability(metadatas),
        "context_chunks": documents,
    }


def query_stream(question: str, mode: str = "Detailed"):
    """
    Streaming version — yields answer token-by-token.
    Also returns metadata after stream completes via .meta attribute
    set on the generator.
    """
    collection = _get_collection()

    results = collection.query(query_texts=[question], n_results=TOP_K)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n---\n\n".join(documents)
    prompt = get_prompt(mode, context, question)

    stream = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    full_answer = []
    for chunk in stream:
        token = chunk["message"]["content"]
        full_answer.append(token)
        yield token

    # Attach metadata to the generator (caller collects via wrapper)
    yield {
        "__meta__": True,
        "sources": _format_sources(metadatas),
        "exam_probability": _compute_exam_probability(metadatas),
        "full_answer": "".join(full_answer),
        "context_chunks": documents,
    }


def is_collection_ready() -> bool:
    """Check if the ChromaDB collection exists and has documents."""
    try:
        col = _get_collection()
        return col.count() > 0
    except Exception:
        return False
