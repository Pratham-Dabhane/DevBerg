"""Technology Discovery Service.

Periodically queries GitHub Search API for trending repositories
and auto-registers new technologies into the tracked_technologies table.
"""

import logging
import time
from datetime import datetime, timezone, timedelta

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import TrackedTechnology

logger = logging.getLogger(__name__)

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"

# Minimum star threshold for auto-discovered repos
MIN_STARS = 3000

# Maximum number of new techs to discover per cycle
MAX_DISCOVERIES_PER_CYCLE = 10

# Topics that signal a "developer tool / framework / language"
RELEVANT_TOPICS = {
    "framework", "library", "programming-language", "developer-tools",
    "machine-learning", "deep-learning", "web-framework", "database",
    "devops", "cli", "api", "sdk", "orm", "runtime", "compiler",
    "frontend", "backend", "full-stack", "data-science", "llm",
    "vector-database", "artificial-intelligence", "cloud-native",
    "infrastructure", "monitoring", "testing", "build-tool",
}

# Category inference from repo topics / language
TOPIC_TO_CATEGORY = {
    "machine-learning": "AI", "deep-learning": "AI", "artificial-intelligence": "AI",
    "llm": "AI", "vector-database": "AI", "data-science": "AI",
    "web-framework": "Backend", "backend": "Backend", "api": "Backend",
    "frontend": "Frontend", "ui": "Frontend",
    "devops": "DevOps", "infrastructure": "DevOps", "monitoring": "DevOps",
    "database": "Database", "orm": "Database",
    "programming-language": "Systems", "compiler": "Systems", "runtime": "Runtime",
    "cli": "Runtime", "build-tool": "Runtime", "developer-tools": "Runtime",
}

LANGUAGE_TO_CATEGORY = {
    "Python": "Backend", "JavaScript": "Frontend", "TypeScript": "Frontend",
    "Rust": "Systems", "Go": "Systems", "Java": "Backend", "C++": "Systems",
    "Ruby": "Backend", "PHP": "Backend", "C#": "Backend", "Kotlin": "Mobile",
    "Swift": "Mobile", "Dart": "Mobile",
}


def _infer_category(topics: list[str], language: str | None) -> str:
    """Best-effort category from repo topics and primary language."""
    for topic in topics:
        if topic in TOPIC_TO_CATEGORY:
            return TOPIC_TO_CATEGORY[topic]
    if language and language in LANGUAGE_TO_CATEGORY:
        return LANGUAGE_TO_CATEGORY[language]
    return "General"


def _infer_so_tag(repo_name: str, topics: list[str]) -> str:
    """Best-effort StackOverflow tag from repo name / topics."""
    # Common SO tag is just the repo name lowered
    name_lower = repo_name.lower().replace(" ", "-")
    return name_lower


def _build_description(repo: dict) -> str:
    """Build a short TF-IDF friendly description from repo metadata."""
    parts: list[str] = []
    if repo.get("description"):
        parts.append(repo["description"][:200])
    topics = repo.get("topics", [])
    if topics:
        parts.append(" ".join(topics[:10]))
    if repo.get("language"):
        parts.append(repo["language"].lower())
    return " ".join(parts)[:500]


class DiscoveryService:
    """Discovers trending GitHub repositories and registers them as technologies."""

    def __init__(self, db: Session) -> None:
        self.db = db
        settings = get_settings()
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    def _search_github(self, query: str, sort: str = "stars", per_page: int = 30) -> list[dict]:
        """Run a GitHub repository search."""
        params = {"q": query, "sort": sort, "order": "desc", "per_page": per_page}
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(GITHUB_SEARCH_URL, headers=self.headers, params=params)
                resp.raise_for_status()
                return resp.json().get("items", [])
        except httpx.HTTPStatusError as e:
            logger.warning("GitHub search API error: %s", e)
            return []

    def discover_trending(self) -> int:
        """Find trending repos pushed recently with high star counts.

        Returns the number of newly registered technologies.
        """
        # Search for repos with significant stars that were pushed in the last 90 days
        cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%d")
        query = f"stars:>{MIN_STARS} pushed:>{cutoff}"
        repos = self._search_github(query, sort="stars", per_page=50)

        existing_repos = {
            t.github_repo
            for t in self.db.query(TrackedTechnology.github_repo).all()
        }
        existing_names = {
            t.name.lower()
            for t in self.db.query(TrackedTechnology.name).all()
        }

        added = 0
        for repo in repos:
            if added >= MAX_DISCOVERIES_PER_CYCLE:
                break

            full_name: str = repo.get("full_name", "")
            repo_name: str = repo.get("name", "")
            topics: list[str] = repo.get("topics", [])

            # Skip if already tracked
            if full_name in existing_repos or repo_name.lower() in existing_names:
                continue

            # Must have at least one relevant topic to be a "tech"
            if not any(t in RELEVANT_TOPICS for t in topics):
                continue

            category = _infer_category(topics, repo.get("language"))
            so_tag = _infer_so_tag(repo_name, topics)
            description = _build_description(repo)

            tech = TrackedTechnology(
                name=repo_name,
                github_repo=full_name,
                so_tag=so_tag,
                category=category,
                description=description,
                is_active=True,
                auto_discovered=True,
            )
            self.db.add(tech)
            added += 1
            logger.info("Auto-discovered technology: %s (%s)", repo_name, full_name)

        if added:
            self.db.commit()
        logger.info("Discovery cycle complete — %d new technologies registered.", added)
        return added

    def discover_rising_stars(self) -> int:
        """Find repos created in the last year that gained stars fast."""
        one_year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
        query = f"stars:>1000 created:>{one_year_ago}"
        repos = self._search_github(query, sort="stars", per_page=30)

        existing_repos = {
            t.github_repo
            for t in self.db.query(TrackedTechnology.github_repo).all()
        }
        existing_names = {
            t.name.lower()
            for t in self.db.query(TrackedTechnology.name).all()
        }

        added = 0
        for repo in repos:
            if added >= MAX_DISCOVERIES_PER_CYCLE:
                break

            full_name = repo.get("full_name", "")
            repo_name = repo.get("name", "")
            topics = repo.get("topics", [])

            if full_name in existing_repos or repo_name.lower() in existing_names:
                continue

            if not any(t in RELEVANT_TOPICS for t in topics):
                continue

            category = _infer_category(topics, repo.get("language"))
            so_tag = _infer_so_tag(repo_name, topics)
            description = _build_description(repo)

            tech = TrackedTechnology(
                name=repo_name,
                github_repo=full_name,
                so_tag=so_tag,
                category=category,
                description=description,
                is_active=True,
                auto_discovered=True,
            )
            self.db.add(tech)
            added += 1
            logger.info("Rising-star technology: %s (%s)", repo_name, full_name)

        if added:
            self.db.commit()
        logger.info("Rising-stars cycle — %d new technologies.", added)
        return added

    def run(self) -> int:
        """Execute full discovery: trending + rising stars."""
        total = 0
        total += self.discover_trending()
        time.sleep(2)  # Be polite to GitHub API
        total += self.discover_rising_stars()
        return total
