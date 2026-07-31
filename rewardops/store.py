from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Opportunity


class OpportunityStore:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS opportunities (
                    url TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    verified_at TEXT NOT NULL
                )
                """
            )

    def save(self, opportunity: Opportunity) -> None:
        payload = json.dumps(opportunity.to_dict(), separators=(",", ":"), sort_keys=True)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO opportunities(url, payload, score, verified_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    payload = excluded.payload,
                    score = excluded.score,
                    verified_at = excluded.verified_at
                """,
                (
                    opportunity.url,
                    payload,
                    opportunity.score,
                    opportunity.verified_at.isoformat(),
                ),
            )

    def list(self, limit: int = 10) -> list[Opportunity]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM opportunities
                ORDER BY score DESC, verified_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [Opportunity.from_dict(json.loads(row["payload"])) for row in rows]
