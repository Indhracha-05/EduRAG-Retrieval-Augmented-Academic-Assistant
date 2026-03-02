"""
Mind-map generator.
Asks the LLM to extract related academic concepts from the answer,
then builds a lightweight networkx graph for display.
"""

import json
import networkx as nx
import ollama

LLM_MODEL = "llama3"


def extract_related_concepts(topic: str, answer: str, n: int = 6) -> list[str]:
    """Use the LLM to extract *n* related academic concepts."""
    prompt = (
        f"Given the following academic topic and answer, extract exactly {n} "
        "closely related academic concepts or sub-topics that a student should "
        "also study. Return ONLY a JSON array of strings, nothing else.\n\n"
        f"TOPIC: {topic}\n\n"
        f"ANSWER (excerpt): {answer[:1500]}\n\n"
        "JSON array:"
    )

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response["message"]["content"].strip()

    # Try to parse JSON from the response
    try:
        # Handle case where LLM wraps in markdown code block
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        concepts = json.loads(text)
        if isinstance(concepts, list):
            return [str(c) for c in concepts[:n]]
    except (json.JSONDecodeError, IndexError):
        pass

    # Fallback: split by newlines / commas
    lines = [
        line.strip().strip("-•*").strip().strip('"').strip("'")
        for line in text.replace(",", "\n").split("\n")
        if line.strip()
    ]
    return lines[:n]


def build_mind_map(topic: str, concepts: list[str]) -> nx.Graph:
    """Build a star graph with the topic at the center."""
    G = nx.Graph()
    G.add_node(topic, group="center")
    for concept in concepts:
        G.add_node(concept, group="related")
        G.add_edge(topic, concept)
    return G


def get_mind_map_data(topic: str, answer: str) -> dict:
    """
    Full pipeline: extract concepts → build graph → return serialisable data.
    Returns {nodes: [...], edges: [...], concepts: [...]}.
    """
    concepts = extract_related_concepts(topic, answer)
    G = build_mind_map(topic, concepts)

    nodes = [
        {
            "id": node,
            "label": node,
            "size": 30 if data.get("group") == "center" else 20,
            "color": "#FF6B6B" if data.get("group") == "center" else "#4ECDC4",
        }
        for node, data in G.nodes(data=True)
    ]

    edges = [
        {"source": u, "target": v}
        for u, v in G.edges()
    ]

    return {"nodes": nodes, "edges": edges, "concepts": concepts}
