from __future__ import annotations

import shlex

import httpx

from .formatting import digest_text, opportunity_blocks, opportunity_text
from .github import GitHubVerifier, UnsupportedOpportunity
from .store import OpportunityStore

HELP_TEXT = """RewardOps verifies reward evidence before you invest effort.

Commands:
  scan <GitHub issue URL>   verify current state, reward and competition
  watch <GitHub issue URL>  verify and add it to the evidence digest
  digest                    rank watched opportunities
  help                      show this guide

The same command handler runs on every connected Caspian channel."""


class RewardOpsService:
    def __init__(self, verifier: GitHubVerifier, store: OpportunityStore) -> None:
        self.verifier = verifier
        self.store = store

    def handle(self, raw_text: str | None) -> tuple[str, list[dict] | None]:
        text = (raw_text or "").strip()
        if not text:
            return HELP_TEXT, None
        try:
            parts = shlex.split(text)
        except ValueError:
            return "I could not parse that command. Send `help` for examples.", None

        command = parts[0].lower()
        if command in {"help", "commands", "start", "hello", "hi"}:
            return HELP_TEXT, None
        if command == "digest":
            return digest_text(self.store.list()), None
        if command not in {"scan", "watch"}:
            return "Unknown command. Send `help` to see the evidence workflow.", None
        if len(parts) != 2:
            return f"Usage: {command} <GitHub issue URL>", None

        try:
            opportunity = self.verifier.verify(parts[1])
        except UnsupportedOpportunity as error:
            return str(error), None
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            return f"The source could not be verified live (HTTP {status}).", None
        except httpx.HTTPError:
            return "The source is temporarily unreachable. It was not scored from stale data.", None

        if command == "watch":
            self.store.save(opportunity)
        prefix = "Saved to digest.\n\n" if command == "watch" else ""
        return prefix + opportunity_text(opportunity), opportunity_blocks(opportunity)
