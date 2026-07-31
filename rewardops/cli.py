from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .github import GitHubVerifier
from .service import RewardOpsService
from .store import OpportunityStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rewardops",
        description="Verify a software reward against its live source.",
    )
    parser.add_argument("command", choices=["scan", "watch", "digest"])
    parser.add_argument("url", nargs="?")
    parser.add_argument(
        "--database",
        default=os.getenv("REWARDOPS_DATABASE", "rewardops.sqlite3"),
    )
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    service = RewardOpsService(
        GitHubVerifier(),
        OpportunityStore(Path(args.database)),
    )
    raw = args.command if args.url is None else f"{args.command} {args.url}"
    text, _ = service.handle(raw)
    print(text)


if __name__ == "__main__":
    main()
