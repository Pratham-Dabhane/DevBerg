from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.graph.dependency_graph import graph_to_cytoscape
from app.graph.graph_analyzer import GraphAnalyzer
from app.models.models import TechnologyGraphMetrics
from app.models.schemas import (
    ClusterSchema,
    CollectionStatusSchema,
    GraphNetworkSchema,
    InfluenceRankSchema,
    TechnologyGraphMetricsSchema,
)

router = APIRouter(prefix="/graph", tags=["graph"])


# ── GET /graph/network ────────────────────────────────────────────

@router.get("/network", response_model=GraphNetworkSchema)
def get_graph_network(db: Session = Depends(get_db)) -> dict:
    """Return the full dependency graph in Cytoscape.js / D3.js format."""
    analyzer = GraphAnalyzer(db)
    G = analyzer.get_annotated_graph()

    # Build cluster mapping from the annotated graph
    clusters = {node: data.get("cluster_id", 0) for node, data in G.nodes(data=True)}
    return graph_to_cytoscape(G, clusters)


# ── GET /graph/influence ──────────────────────────────────────────

@router.get("/influence", response_model=list[InfluenceRankSchema])
def get_influence_rankings(db: Session = Depends(get_db)) -> list[dict]:
    """Return technologies ranked by ecosystem influence (latest snapshot)."""
    subq = (
        db.query(
            TechnologyGraphMetrics.technology_name,
            func.max(TechnologyGraphMetrics.last_updated).label("max_ts"),
        )
        .group_by(TechnologyGraphMetrics.technology_name)
        .subquery()
    )
    rows = (
        db.query(TechnologyGraphMetrics)
        .join(
            subq,
            (TechnologyGraphMetrics.technology_name == subq.c.technology_name)
            & (TechnologyGraphMetrics.last_updated == subq.c.max_ts),
        )
        .order_by(desc(TechnologyGraphMetrics.ecosystem_influence))
        .all()
    )
    return [
        {
            "technology_name": r.technology_name,
            "ecosystem_influence": r.ecosystem_influence,
            "degree_centrality": r.degree_centrality,
            "betweenness_centrality": r.betweenness_centrality,
            "closeness_centrality": r.closeness_centrality,
            "pagerank": r.pagerank,
        }
        for r in rows
    ]


# ── GET /graph/clusters ──────────────────────────────────────────

@router.get("/clusters", response_model=list[ClusterSchema])
def get_clusters(db: Session = Depends(get_db)) -> list[dict]:
    """Return ecosystem clusters with their member technologies."""
    subq = (
        db.query(
            TechnologyGraphMetrics.technology_name,
            func.max(TechnologyGraphMetrics.last_updated).label("max_ts"),
        )
        .group_by(TechnologyGraphMetrics.technology_name)
        .subquery()
    )
    rows = (
        db.query(TechnologyGraphMetrics)
        .join(
            subq,
            (TechnologyGraphMetrics.technology_name == subq.c.technology_name)
            & (TechnologyGraphMetrics.last_updated == subq.c.max_ts),
        )
        .all()
    )

    clusters: dict[int, dict] = {}
    for r in rows:
        if r.cluster_id not in clusters:
            clusters[r.cluster_id] = {
                "cluster_id": r.cluster_id,
                "cluster_label": r.cluster_label,
                "technologies": [],
            }
        clusters[r.cluster_id]["technologies"].append(r.technology_name)

    return sorted(clusters.values(), key=lambda c: c["cluster_id"])


# ── POST /graph/analyze ──────────────────────────────────────────

@router.post("/analyze", response_model=CollectionStatusSchema)
def trigger_graph_analysis(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run graph analytics and persist results."""
    analyzer = GraphAnalyzer(db)
    results = analyzer.run()
    return {
        "status": "success",
        "message": f"Computed graph metrics for {len(results)} technologies",
    }
