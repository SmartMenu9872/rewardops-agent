from __future__ import annotations

import os
from pathlib import Path

from caspian_sdk import CommClient

from .github import GitHubVerifier
from .service import RewardOpsService
from .store import OpportunityStore


def build_service() -> RewardOpsService:
    database = Path(os.getenv("REWARDOPS_DATABASE", "rewardops.sqlite3"))
    return RewardOpsService(GitHubVerifier(), OpportunityStore(database))


def main() -> None:
    service = build_service()
    client = CommClient()

    @client.on_message
    def handle(message) -> None:
        """One handler for email, Discord, Slack and every future channel."""

        text, blocks = service.handle(message.text)
        message.reply(text=text, blocks=blocks)
        print(f"[{message.channel}] handled {message.id}")

    print("RewardOps is listening on every active Caspian connection.")
    client.listen()


if __name__ == "__main__":
    main()
