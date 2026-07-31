from __future__ import annotations

from .models import Opportunity


def score_opportunity(opportunity: Opportunity) -> Opportunity:
    """Score evidence, not marketplace marketing.

    A closed source is a hard stop. Active opportunities earn points for a
    concrete reward, current activity, explicit payout mechanics and clear
    requirements, then lose points for crowding, ambiguity and age.
    """

    if opportunity.state.lower() not in {"open", "active"}:
        opportunity.score = 0
        opportunity.recommendation = "SKIP"
        if "source is not open" not in opportunity.risk_flags:
            opportunity.risk_flags.insert(0, "source is not open")
        return opportunity

    score = 25

    if opportunity.reward_usd is None:
        score -= 20
        _append_unique(opportunity.risk_flags, "reward amount is not verified")
    else:
        score += min(35, int(opportunity.reward_usd / 4))

    if opportunity.age_days <= 14:
        score += 15
    elif opportunity.age_days <= 60:
        score += 10
    elif opportunity.age_days <= 180:
        score += 3
    else:
        score -= 20
        _append_unique(opportunity.risk_flags, "source has been quiet for over 180 days")

    if opportunity.competitor_count == 0:
        score += 10
    else:
        score -= min(30, opportunity.competitor_count * 3)
        if opportunity.competitor_count >= 8:
            _append_unique(
                opportunity.risk_flags,
                f"crowded: at least {opportunity.competitor_count} visible attempts",
            )

    score += min(15, len(opportunity.positive_signals) * 5)
    score -= min(20, len(opportunity.risk_flags) * 4)

    opportunity.score = max(0, min(100, score))
    if opportunity.score >= 70:
        opportunity.recommendation = "PURSUE"
    elif opportunity.score >= 45:
        opportunity.recommendation = "RESEARCH"
    else:
        opportunity.recommendation = "SKIP"
    return opportunity


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)
