from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class Opportunity:
    url: str
    title: str
    source: str
    state: str
    reward_usd: float | None
    competitor_count: int
    updated_at: datetime
    verified_at: datetime
    score: int = 0
    recommendation: str = "RESEARCH"
    reward_evidence: list[str] = field(default_factory=list)
    positive_signals: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def age_days(self) -> int:
        return max(0, (datetime.now(UTC) - self.updated_at).days)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["updated_at"] = self.updated_at.isoformat()
        payload["verified_at"] = self.verified_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Opportunity:
        data = dict(payload)
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        data["verified_at"] = datetime.fromisoformat(data["verified_at"])
        return cls(**data)
