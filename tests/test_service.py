from __future__ import annotations

from datetime import UTC, datetime

from rewardops.models import Opportunity
from rewardops.service import RewardOpsService
from rewardops.store import OpportunityStore


class FakeVerifier:
    def verify(self, url: str) -> Opportunity:
        return Opportunity(
            url=url,
            title="Verified reward",
            source="GitHub",
            state="open",
            reward_usd=150,
            competitor_count=1,
            updated_at=datetime.now(UTC),
            verified_at=datetime.now(UTC),
            score=82,
            recommendation="PURSUE",
            positive_signals=["payout mechanics are described"],
        )


def test_watch_then_digest(tmp_path) -> None:
    service = RewardOpsService(FakeVerifier(), OpportunityStore(tmp_path / "test.sqlite3"))
    watch_text, blocks = service.handle("watch https://github.com/acme/widget/issues/1")
    digest_text, _ = service.handle("digest")

    assert watch_text.startswith("Saved to digest.")
    assert blocks is not None
    assert "Verified reward" in digest_text
    assert "82/100" in digest_text


def test_help_works_from_any_greeting(tmp_path) -> None:
    service = RewardOpsService(FakeVerifier(), OpportunityStore(tmp_path / "test.sqlite3"))
    text, blocks = service.handle("hello")
    assert "same command handler" in text
    assert blocks is None
