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
    ("LlamaIndex", "OpenAI", "dependency"),
    ("LlamaIndex", "LangChain", "integration"),
    ("OpenAI", "Tiktoken", "dependency"),
    ("Ollama", "LangChain", "integration"),
    ("ChromaDB", "DuckDB", "dependency"),
    ("Hugging Face", "PyTorch", "dependency"),
    ("Hugging Face", "TensorFlow", "integration"),
    ("PyTorch", "CUDA", "dependency"),
    ("TensorFlow", "CUDA", "dependency"),
    ("TensorFlow", "Keras", "integration"),
    ("scikit-learn", "PostgreSQL", "ecosystem"),
    ("MLflow", "PyTorch", "integration"),
    ("MLflow", "scikit-learn", "integration"),
    ("Stable Diffusion", "PyTorch", "dependency"),
    ("Weaviate", "Go", "dependency"),
    ("Milvus", "Go", "dependency"),
    ("Qdrant", "Rust", "dependency"),

    # Python backend ecosystem
    ("FastAPI", "Pydantic", "dependency"),
    ("FastAPI", "Uvicorn", "dependency"),
    ("FastAPI", "Starlette", "dependency"),
    ("FastAPI", "SQLAlchemy", "integration"),
    ("Django", "Celery", "integration"),
    ("Django", "PostgreSQL", "ecosystem"),
    ("Flask", "Jinja2", "dependency"),
    ("Flask", "Werkzeug", "dependency"),
    ("Flask", "SQLAlchemy", "integration"),

    # Node.js backend ecosystem
    ("Express.js", "Node.js", "dependency"),
    ("NestJS", "Express.js", "dependency"),
    ("NestJS", "Node.js", "dependency"),
    ("Hono", "Bun", "integration"),
    ("Hono", "Node.js", "integration"),

    # JVM ecosystem
    ("Spring Boot", "Kotlin", "integration"),
    ("Spring Boot", "PostgreSQL", "ecosystem"),

    # Go ecosystem
    ("Gin", "Go", "dependency"),

    # Other backend
    ("Ruby on Rails", "PostgreSQL", "ecosystem"),
    ("Laravel", "Redis", "integration"),
    ("ASP.NET Core", "PostgreSQL", "ecosystem"),

    # Rust ecosystem
    ("Rust", "Tokio", "dependency"),
    ("Rust", "Serde", "dependency"),
    ("Rust", "Actix", "dependency"),
    ("Tokio", "Hyper", "dependency"),

    # Frontend / JS ecosystem
    ("React", "Next.js", "integration"),
    ("React", "Redux", "integration"),
    ("React", "Vite", "ecosystem"),
    ("React", "Remix", "integration"),
    ("Vue", "Nuxt", "integration"),
    ("Vue", "Vite", "ecosystem"),
    ("Svelte", "Vite", "ecosystem"),
    ("SolidJS", "Vite", "ecosystem"),
    ("Astro", "Vite", "dependency"),
    ("Astro", "React", "integration"),
    ("Bun", "Elysia", "integration"),
    ("Bun", "Vite", "ecosystem"),
    ("Next.js", "Vercel", "ecosystem"),
    ("htmx", "Django", "integration"),
    ("htmx", "FastAPI", "integration"),
    ("Tailwind CSS", "Vite", "ecosystem"),
    ("Tailwind CSS", "Next.js", "integration"),
    ("Angular", "TypeScript", "dependency"),
    ("Angular", "Node.js", "ecosystem"),

    # Database / ORM ecosystem
    ("Supabase", "PostgreSQL", "dependency"),
    ("Prisma", "PostgreSQL", "ecosystem"),
    ("Prisma", "Node.js", "dependency"),
    ("Drizzle ORM", "PostgreSQL", "ecosystem"),
    ("Drizzle ORM", "Node.js", "dependency"),
    ("SQLAlchemy", "PostgreSQL", "ecosystem"),
    ("Elasticsearch", "Kubernetes", "ecosystem"),

    # DevOps / Infra ecosystem
    ("Docker", "Kubernetes", "ecosystem"),
    ("Kubernetes", "Helm", "dependency"),
    ("ArgoCD", "Kubernetes", "dependency"),
    ("Grafana", "Prometheus", "integration"),
    ("Prometheus", "Kubernetes", "integration"),
    ("Ansible", "Docker", "integration"),
    ("Terraform", "AWS", "ecosystem"),
    ("Terraform", "Pulumi", "ecosystem"),
    ("GitHub Actions", "Docker", "integration"),

    # Runtime / Tooling ecosystem
    ("Deno", "Rust", "dependency"),
    ("Tauri", "Rust", "dependency"),
    ("Electron", "Node.js", "dependency"),
    ("Electron", "React", "integration"),

    # Mobile ecosystem
    ("React Native", "React", "dependency"),
    ("React Native", "Node.js", "dependency"),
]

# Ecosystem labels assigned to seed nodes.  Nodes not listed here inherit
# a label from their most-connected neighbour during clustering.
ECOSYSTEM_SEEDS: dict[str, str] = {
    # AI / ML
    "LangChain": "AI", "OpenAI": "AI", "ChromaDB": "AI", "Hugging Face": "AI",
    "PyTorch": "AI", "CUDA": "AI", "Tiktoken": "AI", "Qdrant": "AI",
    "TensorFlow": "AI", "Keras": "AI", "scikit-learn": "AI", "MLflow": "AI",
    "Stable Diffusion": "AI", "Ollama": "AI", "LlamaIndex": "AI",
    "Weaviate": "AI", "Milvus": "AI", "DuckDB": "AI", "LangGraph": "AI",
    # Backend
    "FastAPI": "Backend", "Pydantic": "Backend", "Uvicorn": "Backend",
    "Starlette": "Backend", "SQLAlchemy": "Backend", "Django": "Backend",
    "Celery": "Backend", "PostgreSQL": "Backend", "Flask": "Backend",
    "Jinja2": "Backend", "Werkzeug": "Backend", "Express.js": "Backend",
    "NestJS": "Backend", "Spring Boot": "Backend", "Gin": "Backend",
    "Ruby on Rails": "Backend", "Laravel": "Backend", "ASP.NET Core": "Backend",
    "Hono": "Backend",
    # Frontend
    "React": "Frontend", "Next.js": "Frontend", "Redux": "Frontend",
    "Vue": "Frontend", "Nuxt": "Frontend", "Vite": "Frontend",
    "Bun": "Frontend", "Elysia": "Frontend", "Vercel": "Frontend",
    "Angular": "Frontend", "Svelte": "Frontend", "Remix": "Frontend",
    "Astro": "Frontend", "SolidJS": "Frontend", "htmx": "Frontend",
    "Tailwind CSS": "Frontend",
    # Systems
    "Rust": "Systems", "Tokio": "Systems", "Serde": "Systems",
    "Actix": "Systems", "Hyper": "Systems", "Go": "Systems", "Zig": "Systems",
    "Kotlin": "Systems", "TypeScript": "Systems",
    # Database
    "MongoDB": "Database", "Redis": "Database", "Elasticsearch": "Database",
    "Supabase": "Database", "Prisma": "Database", "Drizzle ORM": "Database",
    # DevOps
    "Docker": "DevOps", "Kubernetes": "DevOps", "Helm": "DevOps",
    "Terraform": "DevOps", "AWS": "DevOps", "Pulumi": "DevOps",
    "GitHub Actions": "DevOps", "Ansible": "DevOps", "ArgoCD": "DevOps",
    "Grafana": "DevOps", "Prometheus": "DevOps",
    # Mobile
    "Flutter": "Mobile", "React Native": "Mobile",
    # Runtime
    "Deno": "Runtime", "Node.js": "Runtime", "Tauri": "Runtime",
    "Electron": "Runtime",
}


def build_graph(tracked_technologies: set[str] | None = None) -> nx.DiGraph:
    """Construct the technology dependency graph.

    Args:
        tracked_technologies: Optional set of technology names from the DB.
            If *None*, all nodes present in ECOSYSTEM_SEEDS are considered tracked.

    Returns a NetworkX DiGraph with node attributes:
        - ecosystem: str  (seed label or "Unknown")
        - tracked:   bool (True if the node is a tracked technology)
    and edge attributes:
        - relationship: str  ("dependency" | "integration" | "ecosystem")
    """
    G = nx.DiGraph()

    for source, target, rel in DEPENDENCY_EDGES:
        G.add_edge(source, target, relationship=rel)

    # If no explicit set provided, treat every seeded node as tracked
    if tracked_technologies is None:
        tracked_technologies = set(ECOSYSTEM_SEEDS.keys())

    # Annotate nodes
    for node in G.nodes:
        G.nodes[node]["ecosystem"] = ECOSYSTEM_SEEDS.get(node, "Unknown")
        G.nodes[node]["tracked"] = node in tracked_technologies

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
