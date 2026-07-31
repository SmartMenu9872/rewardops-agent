from __future__ import annotations

from caspian_sdk import blocks as b

from .models import Opportunity

RECOMMENDATION_ICONS = {
    "PURSUE": "🟢",
    "RESEARCH": "🟡",
    "SKIP": "🔴",
}


def opportunity_text(opportunity: Opportunity) -> str:
    reward = (
        f"${opportunity.reward_usd:,.2f}" if opportunity.reward_usd is not None else "unverified"
    )
    lines = [
        f"{RECOMMENDATION_ICONS[opportunity.recommendation]} "
        f"{opportunity.recommendation} — {opportunity.score}/100",
        opportunity.title,
        f"Reward: {reward} · State: {opportunity.state} · "
        f"Visible attempts: {opportunity.competitor_count}",
        f"Verified live: {opportunity.verified_at.strftime('%Y-%m-%d %H:%M UTC')}",
    ]
    if opportunity.positive_signals:
        lines.append("Signals: " + "; ".join(opportunity.positive_signals))
    if opportunity.risk_flags:
        lines.append("Risks: " + "; ".join(opportunity.risk_flags))
    lines.append(opportunity.url)
    return "\n".join(lines)


def opportunity_blocks(opportunity: Opportunity) -> list[dict]:
    reward = (
        f"${opportunity.reward_usd:,.2f}" if opportunity.reward_usd is not None else "Not verified"
    )
    blocks: list[dict] = [
        b.heading(
            f"{RECOMMENDATION_ICONS[opportunity.recommendation]} "
            f"{opportunity.recommendation} · {opportunity.score}/100"
        ),
        b.card(
            title=opportunity.title,
            subtitle=f"{opportunity.source} · verified live",
            text=(
                f"Reward: {reward}\n"
                f"State: {opportunity.state}\n"
                f"Visible attempts: {opportunity.competitor_count}"
            ),
            buttons=[{"label": "Open source", "url": opportunity.url}],
        ),
    ]
    if opportunity.positive_signals:
        blocks.append(b.bullet_list([f"Signal: {item}" for item in opportunity.positive_signals]))
    if opportunity.risk_flags:
        blocks.append(b.bullet_list([f"Risk: {item}" for item in opportunity.risk_flags]))
    return blocks


def digest_text(opportunities: list[Opportunity]) -> str:
    if not opportunities:
        return "No watched opportunities yet. Send: watch <GitHub issue URL>"
    lines = ["RewardOps digest — evidence sorted by score"]
    for index, opportunity in enumerate(opportunities, start=1):
        reward = f"${opportunity.reward_usd:,.0f}" if opportunity.reward_usd is not None else "?"
        lines.append(
            f"{index}. {opportunity.recommendation} {opportunity.score}/100 · "
            f"{reward} · {opportunity.title}\n   {opportunity.url}"
        )
    return "\n".join(lines)
