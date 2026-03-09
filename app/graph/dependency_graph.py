"""Technology Dependency Graph builder.

Constructs a directed graph where nodes are technologies and edges represent
dependency, ecosystem-usage, or framework-integration relationships.

The graph is enriched with node attributes (ecosystem label, tracked flag) so
downstream analytics and API layers can operate on a self-contained structure.
"""

import logging
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)

# ── Static dependency registry ────────────────────────────────────
# Each entry: (source, target, relationship_type)
# Designed to be extended — a future version could pull edges from
# package-manager manifests or GitHub dependency graphs.

DEPENDENCY_EDGES: list[tuple[str, str, str]] = [
    # AI / ML ecosystem
    ("LangChain", "OpenAI", "dependency"),
    ("LangChain", "ChromaDB", "dependency"),
    ("LangChain", "Qdrant", "dependency"),
    ("LangChain", "Hugging Face", "integration"),
    ("LangChain", "FastAPI", "integration"),
    ("OpenAI", "Tiktoken", "dependency"),
    ("ChromaDB", "DuckDB", "dependency"),
    ("Hugging Face", "PyTorch", "dependency"),
    ("PyTorch", "CUDA", "dependency"),

    # Python backend ecosystem
    ("FastAPI", "Pydantic", "dependency"),
    ("FastAPI", "Uvicorn", "dependency"),
    ("FastAPI", "Starlette", "dependency"),
    ("FastAPI", "SQLAlchemy", "integration"),
    ("Django", "Celery", "integration"),
    ("Django", "PostgreSQL", "ecosystem"),
    ("Flask", "Jinja2", "dependency"),
    ("Flask", "Werkzeug", "dependency"),

    # Rust ecosystem
    ("Rust", "Tokio", "dependency"),
    ("Rust", "Serde", "dependency"),
    ("Rust", "Actix", "dependency"),
    ("Rust", "Qdrant", "ecosystem"),
    ("Tokio", "Hyper", "dependency"),

    # Frontend / JS ecosystem
    ("React", "Next.js", "integration"),
    ("React", "Redux", "integration"),
    ("React", "Vite", "ecosystem"),
    ("Vue", "Nuxt", "integration"),
    ("Vue", "Vite", "ecosystem"),
    ("Bun", "Elysia", "integration"),
    ("Bun", "Vite", "ecosystem"),
    ("Next.js", "Vercel", "ecosystem"),

    # DevOps / Infra ecosystem
    ("Docker", "Kubernetes", "ecosystem"),
    ("Kubernetes", "Helm", "dependency"),
    ("Terraform", "AWS", "ecosystem"),
    ("Terraform", "Pulumi", "ecosystem"),
    ("GitHub Actions", "Docker", "integration"),
]

# Ecosystem labels assigned to seed nodes.  Nodes not listed here inherit
# a label from their most-connected neighbour during clustering.
ECOSYSTEM_SEEDS: dict[str, str] = {
    "LangChain": "AI",
    "OpenAI": "AI",
    "ChromaDB": "AI",
    "Hugging Face": "AI",
    "PyTorch": "AI",
    "CUDA": "AI",
    "Tiktoken": "AI",
    "Qdrant": "AI",
    "FastAPI": "Backend",
    "Pydantic": "Backend",
    "Uvicorn": "Backend",
    "Starlette": "Backend",
    "SQLAlchemy": "Backend",
    "Django": "Backend",
    "Celery": "Backend",
    "PostgreSQL": "Backend",
    "Flask": "Backend",
    "Jinja2": "Backend",
    "Werkzeug": "Backend",
    "Rust": "Systems",
    "Tokio": "Systems",
    "Serde": "Systems",
    "Actix": "Systems",
    "Hyper": "Systems",
    "React": "Frontend",
    "Next.js": "Frontend",
    "Redux": "Frontend",
    "Vue": "Frontend",
    "Nuxt": "Frontend",
    "Vite": "Frontend",
    "Bun": "Frontend",
    "Elysia": "Frontend",
    "Vercel": "Frontend",
    "Docker": "DevOps",
    "Kubernetes": "DevOps",
    "Helm": "DevOps",
    "Terraform": "DevOps",
    "AWS": "DevOps",
    "Pulumi": "DevOps",
    "GitHub Actions": "DevOps",
    "DuckDB": "AI",
}

# Tracked technologies (mirrors config.py names) get a special flag so the
# analyzer can weight them more meaningfully against the broader graph.
TRACKED_TECHNOLOGIES = {"FastAPI", "LangChain", "Rust", "Bun", "Qdrant"}


def build_graph() -> nx.DiGraph:
    """Construct the technology dependency graph.

    Returns a NetworkX DiGraph with node attributes:
        - ecosystem: str  (seed label or "Unknown")
        - tracked:   bool (True if the node is a tracked technology)
    and edge attributes:
        - relationship: str  ("dependency" | "integration" | "ecosystem")
    """
    G = nx.DiGraph()

    for source, target, rel in DEPENDENCY_EDGES:
        G.add_edge(source, target, relationship=rel)

    # Annotate nodes
    for node in G.nodes:
        G.nodes[node]["ecosystem"] = ECOSYSTEM_SEEDS.get(node, "Unknown")
        G.nodes[node]["tracked"] = node in TRACKED_TECHNOLOGIES

    logger.info(
        "Built dependency graph: %d nodes, %d edges.",
        G.number_of_nodes(),
        G.number_of_edges(),
    )
    return G


def graph_to_cytoscape(G: nx.DiGraph, clusters: dict[str, int] | None = None) -> dict[str, Any]:
    """Serialize graph to Cytoscape.js / D3.js compatible format.

    Returns ``{"nodes": [...], "edges": [...]}`` where each node carries
    ``id``, ``label``, ``cluster_id``, ``cluster_label``, ``ecosystem_influence``,
    ``pagerank`` and each edge carries ``source``, ``target``, ``relationship``.
    """
    nodes = []
    for node, data in G.nodes(data=True):
        nodes.append(
            {
                "id": node,
                "label": node,
                "cluster_id": clusters.get(node, 0) if clusters else 0,
                "cluster_label": data.get("cluster_label", data.get("ecosystem", "Unknown")),
                "ecosystem_influence": round(data.get("ecosystem_influence", 0.0), 4),
                "pagerank": round(data.get("pagerank", 0.0), 4),
            }
        )

    edges = []
    for src, tgt, data in G.edges(data=True):
        edges.append(
            {
                "source": src,
                "target": tgt,
                "relationship": data.get("relationship", "unknown"),
            }
        )

    return {"nodes": nodes, "edges": edges}
