from __future__ import annotations

import os
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from .models import Opportunity
from .scoring import score_opportunity

GITHUB_ISSUE_PATH = re.compile(r"^/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<number>\d+)/?$")
MONEY_PATTERNS = (
    re.compile(r"(?:/bounty\s+|\$\s*)(?P<amount>\d[\d,]*(?:\.\d{1,2})?)", re.I),
    re.compile(
        r"(?P<amount>\d[\d,]*(?:\.\d{1,2})?)\s*(?:USD|USDC|USDT)\b",
        re.I,
    ),
    re.compile(
        r"(?:bounty|reward|payout)\D{0,20}(?P<amount>\d[\d,]*(?:\.\d{1,2})?)",
        re.I,
    ),
)
ATTEMPT_PATTERN = re.compile(
    r"(?:/attempt|/claim|i(?:'| a)?m working on|i would like to work|opened (?:a )?pr)",
    re.I,
)


class UnsupportedOpportunity(ValueError):
    pass


class GitHubVerifier:
    def __init__(
        self,
        token: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._owns_client = client is None
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rewardops-agent/0.1",
        }
        resolved_token = token or os.getenv("GITHUB_TOKEN")
        if resolved_token:
            headers["Authorization"] = f"Bearer {resolved_token}"
        self._client = client or httpx.Client(
            base_url="https://api.github.com",
            headers=headers,
            timeout=15,
            follow_redirects=True,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def verify(self, url: str) -> Opportunity:
        owner, repo, issue_number = parse_github_issue_url(url)
        issue = self._get_json(f"/repos/{owner}/{repo}/issues/{issue_number}")
        if "pull_request" in issue:
            raise UnsupportedOpportunity("RewardOps currently verifies GitHub issues, not PR URLs.")

        comments = self._get_json(
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            params={"per_page": 100},
        )
        if not isinstance(comments, list):
            comments = []

        body = str(issue.get("body") or "")
        comment_texts = [str(comment.get("body") or "") for comment in comments]
        evidence_text = "\n".join([issue.get("title") or "", body, *comment_texts])
        amounts, evidence = extract_reward_amounts(evidence_text)
        competitor_count = sum(bool(ATTEMPT_PATTERN.search(text)) for text in comment_texts)
        labels = [
            label.get("name", "") for label in issue.get("labels", []) if isinstance(label, dict)
        ]

        positive_signals: list[str] = []
        risk_flags: list[str] = []
        lowercase = evidence_text.lower()
        if any("bounty" in label.lower() or "reward" in label.lower() for label in labels):
            positive_signals.append("official bounty or reward label")
        if any(
            phrase in lowercase
            for phrase in ("receive payment", "payout", "/claim", "paid bounty", "usdc")
        ):
            positive_signals.append("payout mechanics are described")
        if len(body) >= 350 or any(
            marker in lowercase for marker in ("requirements", "acceptance criteria", "steps to")
        ):
            positive_signals.append("implementation scope is concrete")
        if len(body.strip()) < 80:
            risk_flags.append("issue description is unusually vague")
        if issue.get("assignee") or issue.get("assignees"):
            risk_flags.append("issue already has an assignee")
        if issue.get("locked"):
            risk_flags.append("discussion is locked")
        if amounts and max(amounts) > 100_000:
            risk_flags.append("reward amount looks implausible and needs manual confirmation")

        updated_at = _parse_timestamp(issue["updated_at"])
        opportunity = Opportunity(
            url=issue["html_url"],
            title=issue["title"],
            source="GitHub",
            state=issue["state"],
            reward_usd=max(amounts) if amounts else None,
            competitor_count=competitor_count,
            updated_at=updated_at,
            verified_at=datetime.now(UTC),
            reward_evidence=evidence[:5],
            positive_signals=positive_signals,
            risk_flags=risk_flags,
            metadata={
                "owner": owner,
                "repo": repo,
                "issue_number": issue_number,
                "comment_count": issue.get("comments", len(comments)),
                "labels": labels,
            },
        )
        return score_opportunity(opportunity)

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()


def parse_github_issue_url(url: str) -> tuple[str, str, int]:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise UnsupportedOpportunity("Send a public GitHub issue URL.")
    match = GITHUB_ISSUE_PATH.match(parsed.path)
    if not match:
        raise UnsupportedOpportunity("Expected https://github.com/<owner>/<repo>/issues/<number>.")
    return match["owner"], match["repo"], int(match["number"])


def extract_reward_amounts(text: str) -> tuple[list[float], list[str]]:
    amounts: list[float] = []
    evidence: list[str] = []
    for line in text.splitlines():
        for pattern in MONEY_PATTERNS:
            matches = list(pattern.finditer(line))
            if not matches:
                continue
            for match in matches:
                value = float(match["amount"].replace(",", ""))
                if value <= 0:
                    continue
                amounts.append(value)
                compact = " ".join(line.strip().split())
                if compact and compact not in evidence:
                    evidence.append(compact[:180])
            # Patterns intentionally overlap. The first matching grammar wins
            # for each line so "/bounty 100" is not counted twice.
            break
    return amounts, evidence


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
