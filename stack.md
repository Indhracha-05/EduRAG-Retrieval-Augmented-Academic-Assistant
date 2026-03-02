# Technology Stack

## Programming Language

Python 3.10+

---

# Core Libraries

## Document Processing

pypdf

Used to:
- Extract text from PDF documents
- Load syllabus, notes, and past papers

---

## Embeddings

sentence-transformers

Recommended model:
all-MiniLM-L6-v2

Purpose:
Convert text chunks into vector embeddings.

---

## Vector Database

ChromaDB

Used for:
- Storing embeddings
- Performing similarity search
- Retrieving relevant document chunks

---

## RAG Orchestration

LangChain (optional but recommended)

Used for:
- Managing retrieval pipelines
- Integrating embeddings
- Prompt construction

---

## Large Language Model

Two options:

Option 1 (Cloud):
OpenAI API

Option 2 (Local):
Ollama with models like:
- llama3
- mistral

The LLM is responsible for generating answers using retrieved context.

---

## Frontend

Streamlit

Used to build the interface including:

- Question input
- Teaching mode selector
- Ask button
- Answer display
- Source display
- Exam probability indicator
- Mind map display

---

# System Architecture

Academic PDFs
    ↓
Text Extraction
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Database (ChromaDB)
    ↓
User Query
    ↓
Query Embedding
    ↓
Similarity Search
    ↓
Top Relevant Chunks
    ↓
Prompt Construction
    ↓
LLM
    ↓
Generated Answer
    ↓
UI Display (Streamlit)

---

# Project Folder Structure

rag_academic_assistant/

data/
    syllabus.pdf
    notes.pdf
    past_papers.pdf

src/
    ingest.py
    rag_pipeline.py
    prompts.py
    mindmap.py

app.py

requirements.txt

prd.md
stack.md

---

# Requirements.txt

streamlit
langchain
chromadb
sentence-transformers
pypdf
networkx
openai

---

# Development Steps

1. Implement document ingestion pipeline
2. Implement chunking and embeddings
3. Store embeddings in ChromaDB
4. Implement retrieval system
5. Build LLM prompt templates
6. Implement teaching modes
7. Add source citation
8. Implement exam probability logic
9. Implement mind map generator
10. Build Streamlit interface
11. Integrate backend with frontend

---

# Expected Output

The application should allow users to:

- Ask academic questions
- Receive context-grounded answers
- View document sources
- See exam relevance
- Explore related concepts