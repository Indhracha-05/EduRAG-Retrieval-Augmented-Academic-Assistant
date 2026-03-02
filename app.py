"""
EduRAG — Context-Aware Academic RAG Assistant
Flask Application
"""

from flask import Flask, render_template, request, jsonify

from src.ingest import ingest_documents
from src.rag_pipeline import query, is_collection_ready
from src.mindmap import get_mind_map_data

app = Flask(__name__)


# ── pages ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── API endpoints ────────────────────────────────────────────────────
@app.route("/api/status")
def api_status():
    """Check if documents have been ingested."""
    ready = is_collection_ready()
    count = 0
    if ready:
        try:
            from src.rag_pipeline import _get_collection
            count = _get_collection().count()
        except Exception:
            pass
    return jsonify({"ready": ready, "count": count})


@app.route("/api/ingest", methods=["POST"])
def api_ingest():
    """Ingest all PDFs from data/ folder."""
    try:
        result = ingest_documents()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Run the RAG pipeline and return the answer."""
    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode", "Detailed")

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    if not is_collection_ready():
        return jsonify({"error": "No documents ingested yet. Please ingest documents first."}), 400

    try:
        result = query(question, mode)

        # Generate related concepts
        try:
            mm = get_mind_map_data(question, result["answer"])
            concepts = mm["concepts"]
        except Exception:
            concepts = []

        return jsonify({
            "answer": result["answer"],
            "sources": result["sources"],
            "exam_probability": result["exam_probability"],
            "concepts": concepts,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
