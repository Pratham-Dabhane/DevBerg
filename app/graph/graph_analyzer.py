"""Graph analytics engine.

Computes centrality metrics, PageRank, ecosystem influence scores, and
community clusters (Louvain) over the technology dependency graph, then
persists results into the ``technology_graph_metrics`` table.
"""

import logging
from datetime import datetime, timezone

import community as community_louvain  # python-louvain
import networkx as nx
from sqlalchemy.orm import Session

from app.graph.dependency_graph import build_graph
from app.models.models import TechnologyGraphMetrics

logger = logging.getLogger(__name__)

# Cluster-id → human-readable ecosystem label.
# After Louvain runs we map each community back to the dominant seed label
# of its members.  This mapping is built dynamically in ``_label_clusters``.
_ECOSYSTEM_NAMES = {
    "AI": "AI Ecosystem",
    "Backend": "Backend Ecosystem",
    "Frontend": "Frontend Ecosystem",
    "Systems": "Systems Ecosystem",
    "DevOps": "DevOps Ecosystem",
    "Unknown": "Other",
}


def _label_clusters(
    G_undirected: nx.Graph,
    partition: dict[str, int],
) -> dict[int, str]:
    """Derive a human-readable label for each Louvain cluster.

    For every cluster we count how often each seed ecosystem label appears
    among its members and pick the majority.
    """
    cluster_votes: dict[int, dict[str, int]] = {}
    for node, cid in partition.items():
        eco = G_undirected.nodes[node].get("ecosystem", "Unknown")
        cluster_votes.setdefault(cid, {})
        cluster_votes[cid][eco] = cluster_votes[cid].get(eco, 0) + 1

    labels: dict[int, str] = {}
    for cid, votes in cluster_votes.items():
        dominant = max(votes, key=votes.get)  # type: ignore[arg-type]
        labels[cid] = _ECOSYSTEM_NAMES.get(dominant, f"{dominant} Ecosystem")
    return labels


class GraphAnalyzer:
    """Runs graph analytics over the technology dependency graph."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Build & annotate ──────────────────────────────────────────

    def _analyse_graph(self) -> tuple[nx.DiGraph, dict[str, int], dict[int, str]]:
        """Build graph, compute all metrics, return (graph, partition, labels)."""
        G = build_graph()

        # Centrality metrics (computed on the directed graph)
        degree = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G)
        closeness = nx.closeness_centrality(G)
        pr = nx.pagerank(G, alpha=0.85)

        # Community detection needs an undirected view
        G_undirected = G.to_undirected()
        partition = community_louvain.best_partition(G_undirected)
        cluster_labels = _label_clusters(G_undirected, partition)

        # Ecosystem influence = weighted combination of centrality signals
        for node in G.nodes:
            dc = degree.get(node, 0.0)
            bc = betweenness.get(node, 0.0)
            cc = closeness.get(node, 0.0)
            p = pr.get(node, 0.0)

            influence = 0.30 * dc + 0.25 * bc + 0.25 * p + 0.20 * cc

            G.nodes[node]["degree_centrality"] = round(dc, 6)
            G.nodes[node]["betweenness_centrality"] = round(bc, 6)
            G.nodes[node]["closeness_centrality"] = round(cc, 6)
            G.nodes[node]["pagerank"] = round(p, 6)
            G.nodes[node]["ecosystem_influence"] = round(influence, 6)
            G.nodes[node]["cluster_id"] = partition.get(node, 0)
            G.nodes[node]["cluster_label"] = cluster_labels.get(
                partition.get(node, 0), "Other"
            )

        return G, partition, cluster_labels

    # ── Public API ────────────────────────────────────────────────

    def compute(self) -> list[dict]:
        """Return a list of per-node metric dicts (not yet persisted)."""
        G, partition, cluster_labels = self._analyse_graph()
        now = datetime.now(timezone.utc)

        results: list[dict] = []
        for node, data in G.nodes(data=True):
            results.append(
                {
                    "technology_name": node,
                    "degree_centrality": data["degree_centrality"],
                    "betweenness_centrality": data["betweenness_centrality"],
                    "closeness_centrality": data["closeness_centrality"],
                    "pagerank": data["pagerank"],
                    "ecosystem_influence": data["ecosystem_influence"],
                    "cluster_id": data["cluster_id"],
                    "cluster_label": data["cluster_label"],
                    "last_updated": now,
                }
            )

        # Sort by influence descending
        results.sort(key=lambda r: r["ecosystem_influence"], reverse=True)
        return results

    def run(self) -> list[TechnologyGraphMetrics]:
        """Compute and persist graph metrics. Returns ORM objects."""
        results = self.compute()
        if not results:
            return []

        orm_objects: list[TechnologyGraphMetrics] = []
        for r in results:
            obj = TechnologyGraphMetrics(**r)
            self.db.add(obj)
            orm_objects.append(obj)

        self.db.commit()
        for obj in orm_objects:
            self.db.refresh(obj)

        logger.info("Persisted graph metrics for %d technologies.", len(orm_objects))
        return orm_objects

    def get_annotated_graph(self) -> nx.DiGraph:
        """Return a fully-annotated DiGraph (for serialisation in the API)."""
        G, _, _ = self._analyse_graph()
        return G
