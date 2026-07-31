from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest

from rewardops.github import (
    GitHubVerifier,
    UnsupportedOpportunity,
    extract_reward_amounts,
    parse_github_issue_url,
)


def test_parse_github_issue_url() -> None:
    assert parse_github_issue_url("https://github.com/acme/widget/issues/42") == (
        "acme",
        "widget",
        42,
    )
    with pytest.raises(UnsupportedOpportunity):
        parse_github_issue_url("https://example.com/acme/widget/issues/42")


def test_extract_reward_amounts_handles_common_bounty_formats() -> None:
    amounts, evidence = extract_reward_amounts(
        "Sponsor says /bounty 100\nPool: 350 USDC\nPayout is $25.50 after review"
    )
    assert amounts == [100.0, 350.0, 25.5]
    assert len(evidence) == 3


def test_live_verifier_hard_stops_closed_issue() -> None:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/comments"):
            return httpx.Response(200, json=[])
        return httpx.Response(
            200,
            json={
                "title": "Build a thing",
                "body": "/bounty 500\n\nRequirements\n- ship it",
                "state": "closed",
                "html_url": "https://github.com/acme/widget/issues/7",
                "updated_at": now,
                "comments": 0,
                "labels": [{"name": "bounty"}],
                "assignee": None,
                "assignees": [],
                "locked": False,
            },
        )

    client = httpx.Client(
        base_url="https://api.github.test",
        transport=httpx.MockTransport(handler),
    )
    opportunity = GitHubVerifier(client=client).verify("https://github.com/acme/widget/issues/7")
    assert opportunity.reward_usd == 500
    assert opportunity.recommendation == "SKIP"
    assert opportunity.score == 0
    assert "source is not open" in opportunity.risk_flags


def test_live_verifier_penalizes_visible_attempts() -> None:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/comments"):
            return httpx.Response(
                200,
                json=[
                    {"body": "/attempt #9"},
                    {"body": "I would like to work on this"},
                ],
            )
        return httpx.Response(
            200,
            json={
                "title": "$100 improve verification",
                "body": "Requirements\n" + ("clear implementation detail " * 20),
                "state": "open",
                "html_url": "https://github.com/acme/widget/issues/9",
                "updated_at": now,
                "comments": 2,
                "labels": [{"name": "Paid Bounty"}],
                "assignee": None,
                "assignees": [],
                "locked": False,
            },
        )

    client = httpx.Client(
        base_url="https://api.github.test",
        transport=httpx.MockTransport(handler),
    )
    opportunity = GitHubVerifier(client=client).verify("https://github.com/acme/widget/issues/9")
    assert opportunity.competitor_count == 2
    assert opportunity.reward_usd == 100
    assert opportunity.state == "open"
    assert opportunity.score > 0
