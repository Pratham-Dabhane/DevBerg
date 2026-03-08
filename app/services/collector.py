import logging

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.services.github_service import GitHubService
from app.services.stackoverflow_service import StackOverflowService
from app.services.hackernews_service import HackerNewsService
from app.pipeline.metrics_pipeline import MetricsPipeline
from app.ml.trend_engine import TrendEngine
from app.analytics.momentum_engine import MomentumEngine
from app.analytics.lifecycle_detector import LifecycleDetector
from app.analytics.emerging_detector import EmergingDetector

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


def run_trend_engine() -> None:
    """Execute the trend detection engine to generate predictions."""
    logger.info("Starting scheduled trend engine run...")
    db: Session = SessionLocal()
    try:
        engine = TrendEngine(db)
        engine.run()
        logger.info("Scheduled trend engine run completed successfully.")
    except Exception as e:
        logger.error("Trend engine run failed: %s", e)
    finally:
        db.close()


def run_analytics() -> None:
    """Execute the full analytics pipeline: momentum → lifecycle → emerging."""
    logger.info("Starting scheduled analytics run...")
    db: Session = SessionLocal()
    try:
        MomentumEngine(db).run()
        LifecycleDetector(db).run()
        EmergingDetector(db).run()
        logger.info("Scheduled analytics run completed successfully.")
    except Exception as e:
        logger.error("Analytics run failed: %s", e)
    finally:
        db.close()
