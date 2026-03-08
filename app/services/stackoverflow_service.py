import logging
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import StackOverflowStats

logger = logging.getLogger(__name__)

SO_API_BASE = "https://api.stackexchange.com/2.3"
SECONDS_IN_30_DAYS = 30 * 24 * 60 * 60


class StackOverflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def _get(self, url: str, params: dict) -> dict:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def _get_tag_info(self, tag: str) -> dict:
        """Fetch tag metadata including total question count."""
        url = f"{SO_API_BASE}/tags/{tag}/info"
        params: dict[str, str] = {
            "site": "stackoverflow",
        }
        if self.settings.stackoverflow_api_key:
            params["key"] = self.settings.stackoverflow_api_key
        data = self._get(url, params)
        if data.get("items"):
            return data["items"][0]
        return {}

    def _get_recent_question_count(self, tag: str) -> int:
        """Count questions posted in the last 30 days for a given tag."""
        from_date = int(time.time()) - SECONDS_IN_30_DAYS
        url = f"{SO_API_BASE}/questions"
        params: dict[str, str | int] = {
            "tagged": tag,
            "site": "stackoverflow",
            "filter": "total",
            "fromdate": from_date,
        }
        if self.settings.stackoverflow_api_key:
            params["key"] = self.settings.stackoverflow_api_key
        data = self._get(url, params)
        return data.get("total", 0)

    def collect_tag_data(self, technology: str, tag: str) -> StackOverflowStats:
        logger.info("Collecting StackOverflow data for %s (tag=%s)", technology, tag)

        tag_info = self._get_tag_info(tag)
        question_count = tag_info.get("count", 0)
        recent_count = self._get_recent_question_count(tag)

        record = StackOverflowStats(
            technology=technology,
            tag=tag,
            question_count=question_count,
            new_questions_last_30_days=recent_count,
            collected_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info(
            "Stored SO data for %s: %d total, %d recent",
            technology,
            question_count,
            recent_count,
        )
        return record

    def collect_all(self) -> list[StackOverflowStats]:
        results: list[StackOverflowStats] = []
        for tech in self.settings.tracked_technologies:
            try:
                record = self.collect_tag_data(tech["name"], tech["so_tag"])
                results.append(record)
            except httpx.HTTPStatusError as e:
                logger.error("StackOverflow API error for %s: %s", tech["name"], e)
            except Exception as e:
                logger.error(
                    "Unexpected error collecting SO data for %s: %s", tech["name"], e
                )
        return results
