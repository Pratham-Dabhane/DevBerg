import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import HackerNewsMention, TechMention

logger = logging.getLogger(__name__)

HN_API_BASE = "https://hn.algolia.com/api/v1"
MAX_STORIES_PER_TECH = 50


class HackerNewsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def _search_stories(self, query: str) -> dict:
        url = f"{HN_API_BASE}/search"
        params: dict[str, str | int] = {
            "query": query,
            "tags": "story",
            "hitsPerPage": MAX_STORIES_PER_TECH,
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def collect_mentions(self, technology: str) -> list[HackerNewsMention]:
        logger.info("Collecting HackerNews data for %s", technology)

        data = self._search_stories(technology)
        hits: list[dict] = data.get("hits", [])
        now = datetime.now(timezone.utc)

        mentions: list[HackerNewsMention] = []
        total_upvotes = 0
        total_comments = 0

        for hit in hits:
            story_id = int(hit.get("objectID", 0))
            upvotes = hit.get("points", 0) or 0
            comments = hit.get("num_comments", 0) or 0
            total_upvotes += upvotes
            total_comments += comments

            mention = HackerNewsMention(
                technology=technology,
                story_id=story_id,
                title=hit.get("title", "")[:500],
                url=hit.get("url"),
                upvotes=upvotes,
                comment_count=comments,
                collected_at=now,
            )
            mentions.append(mention)

        self.db.add_all(mentions)

        # Store aggregate tech mention record
        tech_mention = TechMention(
            technology=technology,
            source="hackernews",
            mention_count=len(hits),
            total_upvotes=total_upvotes,
            total_comments=total_comments,
            collected_at=now,
        )
        self.db.add(tech_mention)
        self.db.commit()

        logger.info(
            "Stored %d HN mentions for %s (upvotes=%d, comments=%d)",
            len(mentions),
            technology,
            total_upvotes,
            total_comments,
        )
        return mentions

    def collect_all(self, technologies: list[dict[str, str]] | None = None) -> list[HackerNewsMention]:
        techs = technologies or self.settings.tracked_technologies
        all_mentions: list[HackerNewsMention] = []
        for tech in techs:
            try:
                mentions = self.collect_mentions(tech["name"])
                all_mentions.extend(mentions)
            except httpx.HTTPStatusError as e:
                logger.error("HackerNews API error for %s: %s", tech["name"], e)
            except Exception as e:
                logger.error(
                    "Unexpected error collecting HN data for %s: %s", tech["name"], e
                )
        return all_mentions
