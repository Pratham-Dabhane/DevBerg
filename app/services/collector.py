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
from app.analytics.repo_health_analyzer import RepoHealthAnalyzer
from app.graph.graph_analyzer import GraphAnalyzer
from app.ml.investment_forecaster import InvestmentForecaster

logger = logging.getLogger(__name__)


def run_collection() -> None:
    """Execute a full data collection cycle across all sources."""
    logger.info("Starting scheduled data collection...")
    db: Session = SessionLocal()
    try:
        from app.services.tech_registry import get_active_technologies
        technologies = get_active_technologies(db)
        logger.info("Collecting data for %d tracked technologies.", len(technologies))

        github_svc = GitHubService(db)
        github_svc.collect_all(technologies)

        so_svc = StackOverflowService(db)
        so_svc.collect_all(technologies)

        hn_svc = HackerNewsService(db)
        hn_svc.collect_all(technologies)

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


def run_repo_health() -> None:
    """Execute the repository health analyzer."""
    logger.info("Starting scheduled repo health analysis...")
    db: Session = SessionLocal()
    try:
        RepoHealthAnalyzer(db).run()
        logger.info("Scheduled repo health analysis completed successfully.")
    except Exception as e:
        logger.error("Repo health analysis failed: %s", e)
    finally:
        db.close()


def run_graph_analysis() -> None:
    """Execute the technology graph analyzer."""
    logger.info("Starting scheduled graph analysis...")
    db: Session = SessionLocal()
    try:
        GraphAnalyzer(db).run()
        logger.info("Scheduled graph analysis completed successfully.")
    except Exception as e:
        logger.error("Graph analysis failed: %s", e)
    finally:
        db.close()


def run_investment_forecasts() -> None:
    """Execute the investment forecaster."""
    logger.info("Starting scheduled investment forecasts...")
    db: Session = SessionLocal()
    try:
        InvestmentForecaster(db).run()
        logger.info("Scheduled investment forecasts completed successfully.")
    except Exception as e:
        logger.error("Investment forecasts failed: %s", e)
    finally:
        db.close()


def run_discovery() -> None:
    """Execute the technology discovery service to find new trending techs."""
    logger.info("Starting scheduled tech discovery...")
    db: Session = SessionLocal()
    try:
        from app.services.discovery_service import DiscoveryService
        svc = DiscoveryService(db)
        added = svc.run()
        logger.info("Tech discovery completed — %d new technologies.", added)
    except Exception as e:
        logger.error("Tech discovery failed: %s", e)
    finally:
        db.close()


def seed_registry() -> None:
    """Seed the technology registry on first run."""
    db: Session = SessionLocal()
    try:
        from app.services.tech_registry import seed_technologies
        seed_technologies(db)
    except Exception as e:
        logger.error("Technology seeding failed: %s", e)
    finally:
        db.close()
