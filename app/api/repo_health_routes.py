from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import RepositoryHealth
from app.models.schemas import RepositoryHealthSchema, CollectionStatusSchema
from app.analytics.repo_health_analyzer import RepoHealthAnalyzer

router = APIRouter(prefix="/repos", tags=["repos"])


@router.get("/health", response_model=list[RepositoryHealthSchema])
def get_all_repo_health(db: Session = Depends(get_db)) -> list[RepositoryHealth]:
    """Return the latest health diagnostics for every repository."""
    subq = (
        db.query(
            RepositoryHealth.repository_name,
            func.max(RepositoryHealth.last_updated).label("max_ts"),
        )
        .group_by(RepositoryHealth.repository_name)
        .subquery()
    )
    return (
        db.query(RepositoryHealth)
        .join(
            subq,
            (RepositoryHealth.repository_name == subq.c.repository_name)
            & (RepositoryHealth.last_updated == subq.c.max_ts),
        )
        .order_by(desc(RepositoryHealth.health_score))
        .all()
    )


@router.get("/health/{repo_name:path}", response_model=RepositoryHealthSchema)
def get_repo_health(
    repo_name: str = Path(..., description="Repository slug, e.g. langchain-ai/langchain"),
    db: Session = Depends(get_db),
) -> RepositoryHealth:
    """Return the latest health diagnostics for a single repository."""
    row = (
        db.query(RepositoryHealth)
        .filter(RepositoryHealth.repository_name.ilike(repo_name))
        .order_by(desc(RepositoryHealth.last_updated))
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"No health data for '{repo_name}'")
    return row


@router.post("/health/run", response_model=CollectionStatusSchema)
def trigger_repo_health_analysis(db: Session = Depends(get_db)) -> dict[str, str]:
    """Run the repository health analyzer."""
    analyzer = RepoHealthAnalyzer(db)
    results = analyzer.run()
    return {
        "status": "success",
        "message": f"Computed health scores for {len(results)} repositories",
    }
