import logging

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.services.github_service import GitHubService
from app.services.stackoverflow_service import StackOverflowService
from app.services.hackernews_service import HackerNewsService
from app.pipeline.metrics_pipeline import MetricsPipeline

logger = logging.getLogger(__name__)


def run_collection() -> None:
    """Execute a full data collection cycle across all sources."""
    logger.info("Starting scheduled data collection...")
    db: Session = SessionLocal()
    try:
        github_svc = GitHubService(db)
        github_svc.collect_all()

        so_svc = StackOverflowService(db)
        so_svc.collect_all()

        hn_svc = HackerNewsService(db)
        hn_svc.collect_all()

        logger.info("Scheduled data collection completed successfully.")
    except Exception as e:
        logger.error("Data collection failed: %s", e)
    finally:
        db.close()


def run_pipeline() -> None:
    """Execute the metrics pipeline to transform raw data into signals."""
    logger.info("Starting scheduled pipeline run...")
    db: Session = SessionLocal()
    try:
        pipeline = MetricsPipeline(db)
        pipeline.run()
        logger.info("Scheduled pipeline run completed successfully.")
    except Exception as e:
        logger.error("Pipeline run failed: %s", e)
    finally:
        db.close()
