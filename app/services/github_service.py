import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.models import Repository

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class GitHubService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.settings.github_token:
            self.headers["Authorization"] = f"Bearer {self.settings.github_token}"

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    def _get_repo_info(self, repo_full_name: str) -> dict:
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}"
        return self._get(url)

    def _get_contributor_count(self, repo_full_name: str) -> int:
        """Get approximate contributor count using per_page=1 and parsing Link header."""
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/contributors"
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                url, headers=self.headers, params={"per_page": 1, "anon": "false"}
            )
            response.raise_for_status()

        link_header = response.headers.get("Link", "")
        if 'rel="last"' in link_header:
            for part in link_header.split(","):
                if 'rel="last"' in part:
                    page_str = part.split("page=")[-1].split(">")[0]
                    try:
                        return int(page_str)
                    except ValueError:
                        pass
        return len(response.json())

    def _get_weekly_commit_frequency(self, repo_full_name: str) -> float:
        """Get average weekly commit count from the last year of participation stats."""
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/stats/participation"
        try:
            data = self._get(url)
            if isinstance(data, dict) and "all" in data:
                weekly_commits: list[int] = data["all"]
                if weekly_commits:
                    return sum(weekly_commits) / len(weekly_commits)
        except httpx.HTTPStatusError:
            logger.warning("Could not fetch commit frequency for %s", repo_full_name)
        return 0.0

    def collect_repository_data(self, technology: str, repo_full_name: str) -> Repository:
        logger.info("Collecting GitHub data for %s (%s)", technology, repo_full_name)

        repo_info = self._get_repo_info(repo_full_name)
        contributors = self._get_contributor_count(repo_full_name)
        commit_freq = self._get_weekly_commit_frequency(repo_full_name)

        record = Repository(
            technology=technology,
            github_repo=repo_full_name,
            stars=repo_info.get("stargazers_count", 0),
            forks=repo_info.get("forks_count", 0),
            open_issues=repo_info.get("open_issues_count", 0),
            contributors=contributors,
            commit_frequency_weekly=round(commit_freq, 2),
            collected_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info("Stored GitHub data for %s: %d stars", technology, record.stars)
        return record

    def collect_all(self, technologies: list[dict[str, str]] | None = None) -> list[Repository]:
        techs = technologies or self.settings.tracked_technologies
        results: list[Repository] = []
        for tech in techs:
            try:
                record = self.collect_repository_data(tech["name"], tech["github_repo"])
                results.append(record)
            except httpx.HTTPStatusError as e:
                logger.error("GitHub API error for %s: %s", tech["name"], e)
            except Exception as e:
                logger.error("Unexpected error collecting GitHub data for %s: %s", tech["name"], e)
        return results
