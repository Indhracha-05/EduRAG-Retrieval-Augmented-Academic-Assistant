"""
Document ingestion pipeline.
- Reads all PDFs from data/
- Extracts text, tags with metadata (filename, page, doc_type)
- Chunks text with overlap
- Embeds and stores in ChromaDB
"""

import os
import re
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions


# ── constants ────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"
COLLECTION_NAME = "academic_docs"
CHUNK_SIZE = 500       # characters  (~125 tokens)
CHUNK_OVERLAP = 50     # characters
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ── helpers ──────────────────────────────────────────────────────────
def _infer_doc_type(filename: str) -> str:
    """Guess document type from filename keywords."""
    name = filename.lower()
    if any(kw in name for kw in ("past_paper", "question_paper", "previous_year", "pyq")):
        return "past_paper"
    if any(kw in name for kw in ("syllabus", "curriculum")):
        return "syllabus"
    if any(kw in name for kw in ("lab", "manual", "practical")):
        return "lab_manual"
    return "notes"


def _extract_pages(pdf_path: Path) -> list[dict]:
    """Return list of {text, page, filename, doc_type}."""
    reader = PdfReader(str(pdf_path))
    doc_type = _infer_doc_type(pdf_path.name)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            pages.append({
                "text": text,
                "page": i + 1,
                "filename": pdf_path.name,
                "doc_type": doc_type,
            })
    return pages


# ── main entry point ─────────────────────────────────────────────────
def ingest_documents(data_dir: str | Path | None = None) -> dict:
    """
    Process every PDF in *data_dir*, chunk, embed, and store in ChromaDB.

    Returns a summary dict: {files_processed, total_chunks}.
    """
    data_dir = Path(data_dir) if data_dir else DATA_DIR
    pdf_files = sorted(data_dir.glob("*.pdf"))

    if not pdf_files:
        return {"files_processed": 0, "total_chunks": 0, "message": "No PDF files found in data/ folder."}

    # ── extract pages ────────────────────────────────────────────────
    all_pages: list[dict] = []
    for pdf in pdf_files:
        all_pages.extend(_extract_pages(pdf))

    # ── chunk ────────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[dict] = []
    for page_info in all_pages:
        splits = splitter.split_text(page_info["text"])
        for j, chunk_text in enumerate(splits):
            chunks.append({
                "id": f"{page_info['filename']}_p{page_info['page']}_c{j}",
                "text": chunk_text,
                "metadata": {
                    "filename": page_info["filename"],
                    "page": page_info["page"],
                    "doc_type": page_info["doc_type"],
                    "chunk_index": j,
                },
            })

    # ── embed & store ────────────────────────────────────────────────
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL,
    )

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Reset collection so re-ingestion is idempotent
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
    )

    # ChromaDB batch limit is 5 461; process in batches of 500
    BATCH = 500
    for start in range(0, len(chunks), BATCH):
        batch = chunks[start : start + BATCH]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )

    return {
        "files_processed": len(pdf_files),
        "total_chunks": len(chunks),
        "message": f"Successfully ingested {len(pdf_files)} file(s) → {len(chunks)} chunks.",
    }


# allow running as script: python -m src.ingest
if __name__ == "__main__":
    result = ingest_documents()
    print(result["message"])
