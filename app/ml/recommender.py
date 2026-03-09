"""AI Technology Recommendation Engine.

Recommends technologies based on a user's skill profile by combining three
signals:

    recommendation_score = momentum_score
                         * skill_similarity
                         * ecosystem_proximity

Where:
    - **skill_similarity**: cosine similarity between the user's TF-IDF
      vector and each candidate technology's vector.
    - **momentum_score**: latest technology momentum score from the DB
      (normalized 0–1).
    - **ecosystem_proximity**: graph-based proximity — technologies in the
      same or adjacent graph cluster to the user's known skills score higher.

Results are persisted in ``user_recommendations`` for auditability.
"""

import logging
from datetime import datetime, timezone

import networkx as nx
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.graph.dependency_graph import build_graph, ECOSYSTEM_SEEDS
from app.ml.skill_embeddings import SkillEmbedder
from app.models.models import TechnologyMomentum, TechnologyGraphMetrics, UserRecommendation

logger = logging.getLogger(__name__)

# Singleton embedder (TF-IDF matrix is small — fine to keep in memory)
_embedder: SkillEmbedder | None = None


def _get_embedder() -> SkillEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = SkillEmbedder()
    return _embedder


def _latest_momentum(db: Session) -> dict[str, float]:
    """Fetch latest momentum score per technology (normalized 0–1)."""
    subq = (
        db.query(
            TechnologyMomentum.technology_name,
            func.max(TechnologyMomentum.timestamp).label("max_ts"),
        )
        .group_by(TechnologyMomentum.technology_name)
        .subquery()
    )
    rows = (
        db.query(TechnologyMomentum)
        .join(
            subq,
            (TechnologyMomentum.technology_name == subq.c.technology_name)
            & (TechnologyMomentum.timestamp == subq.c.max_ts),
        )
        .all()
    )
    return {r.technology_name: r.momentum_score for r in rows}


def _ecosystem_proximity(user_skills: list[str]) -> dict[str, float]:
    """Score every technology based on graph proximity to user skills.

    Technologies in the same ecosystem cluster as any user skill get a
    high score; adjacent-cluster techs get a moderate score; unrelated
    ones get a small baseline.
    """
    G = build_graph()

    # Determine which ecosystem clusters the user already occupies
    user_ecosystems: set[str] = set()
    user_nodes: set[str] = set()
    for skill in user_skills:
        for node in G.nodes:
            if skill.lower() == node.lower():
                user_ecosystems.add(ECOSYSTEM_SEEDS.get(node, "Unknown"))
                user_nodes.add(node)
                break

    # Also add direct graph neighbours of user nodes
    neighbour_nodes: set[str] = set()
    for unode in user_nodes:
        neighbour_nodes.update(G.successors(unode))
        neighbour_nodes.update(G.predecessors(unode))

    scores: dict[str, float] = {}
    for tech in ECOSYSTEM_SEEDS:
        eco = ECOSYSTEM_SEEDS.get(tech, "Unknown")
        if tech.lower() in {s.lower() for s in user_skills}:
            # Already known — low priority for recommendation
            scores[tech] = 0.1
        elif tech in neighbour_nodes:
            scores[tech] = 1.0
        elif eco in user_ecosystems:
            scores[tech] = 0.75
        else:
            scores[tech] = 0.3
    return scores


def _generate_reason(
    tech: str,
    sim: float,
    momentum: float,
    proximity: float,
) -> str:
    """Generate a human-readable reason for recommending a technology."""
    eco = ECOSYSTEM_SEEDS.get(tech, "technology")

    parts: list[str] = []
    if momentum >= 0.5:
        parts.append(f"growing rapidly in {eco.lower()} ecosystem")
    elif momentum >= 0.35:
        parts.append(f"steady momentum in {eco.lower()} ecosystem")

    if proximity >= 0.9:
        parts.append("directly related to your current stack")
    elif proximity >= 0.7:
        parts.append("within your ecosystem")

    if sim >= 0.5:
        parts.append("strong skill alignment")
    elif sim >= 0.3:
        parts.append("complementary to your skills")

    if not parts:
        parts.append(f"emerging technology in {eco.lower()}")

    return "; ".join(parts)


class Recommender:
    """Generates personalized technology recommendations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def recommend(
        self,
        user_skills: list[str],
        top_n: int = 10,
    ) -> list[dict]:
        """Compute recommendation scores and return top-N results.

        Each result dict has: technology_name, recommendation_score,
        skill_similarity, momentum_score, ecosystem_proximity, reason.
        """
        embedder = _get_embedder()
        similarities = embedder.skill_similarity(user_skills)
        momentum_map = _latest_momentum(self.db)
        proximity_map = _ecosystem_proximity(user_skills)

        # All candidate technologies are the union of embedder techs and
        # any tech with momentum data
        candidates = set(similarities.keys()) | set(momentum_map.keys())

        results: list[dict] = []
        user_skills_lower = {s.lower() for s in user_skills}
        now = datetime.now(timezone.utc)

        for tech in candidates:
            # Skip technologies the user already knows
            if tech.lower() in user_skills_lower:
                continue

            sim = similarities.get(tech, 0.0)
            mom = momentum_map.get(tech, 0.3)  # default mid-range for graph-only techs
            prox = proximity_map.get(tech, 0.3)

            score = round(mom * sim * prox, 6)
            reason = _generate_reason(tech, sim, mom, prox)

            results.append(
                {
                    "technology_name": tech,
                    "recommendation_score": score,
                    "skill_similarity": round(sim, 6),
                    "momentum_score": round(mom, 6),
                    "ecosystem_proximity": round(prox, 6),
                    "reason": reason,
                }
            )

        # Sort descending by score
        results.sort(key=lambda r: r["recommendation_score"], reverse=True)
        top = results[:top_n]

        # Persist
        skill_str = ",".join(user_skills)
        for r in top:
            self.db.add(
                UserRecommendation(
                    skill_profile=skill_str,
                    technology_name=r["technology_name"],
                    recommendation_score=r["recommendation_score"],
                    skill_similarity=r["skill_similarity"],
                    momentum_score=r["momentum_score"],
                    ecosystem_proximity=r["ecosystem_proximity"],
                    reason=r["reason"],
                    created_at=now,
                )
            )
        self.db.commit()

        logger.info(
            "Generated %d recommendations for skills: %s",
            len(top),
            skill_str,
        )
        return top
