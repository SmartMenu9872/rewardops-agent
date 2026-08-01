# Devpost submission draft

## Project name

RewardOps — Evidence Before Effort

## Tagline

A cross-channel agent that catches stale, closed, vague, and overcrowded software
rewards before developers waste hours on them.

## Inspiration

Software reward marketplaces are useful discovery layers, but their cards can
outlive the underlying source. During real reward research, we found pages still
advertising $100–$1,000 bounties whose GitHub issues had already closed. Other
opportunities hid dozens of active attempts, an assignee, or no concrete payout
mechanism.

The expensive failure is not missing a listing. It is spending a day building for
money that is no longer realistically claimable. RewardOps makes source evidence
the first step.

## What it does

A developer sends `scan <GitHub issue URL>` to RewardOps through email or Slack.
The agent:

1. verifies the public GitHub issue live;
2. extracts explicit reward evidence such as `$100`, `350 USDC`, or `/bounty 100`,
   while keeping token-only amounts unconverted rather than pretending they are USD;
3. counts visible `/attempt`, `/claim`, and work-intent comments;
4. detects bounty labels, payout mechanics, scope clarity, assignees, locks, age,
   and closed state;
5. applies explainable risk gates; and
6. returns `PURSUE`, `RESEARCH`, or `SKIP` with a score and evidence.

`watch` saves verified opportunities to SQLite. `digest` ranks them. A closed
source is always a hard stop, regardless of the marketplace card or advertised
amount.

## How we built it

- Python 3.11+
- `caspian-sdk` 0.6.1
- one Caspian `on_message` handler for every channel
- Caspian email and Slack connections
- GitHub REST API for live source evidence
- HTTPX for bounded, redirect-safe requests
- SQLite for a local evidence watchlist
- Pytest and Ruff in GitHub Actions
- Caspian rich blocks for native cards plus portable text fallbacks

No handler is duplicated per channel. Email reply history is stripped before
command parsing so quoting behavior cannot turn one instruction into many.

## Challenges

The most surprising challenge was stale marketplace state. A listing could look
funded and actionable while the issue of record was closed. That led to the
agent's defining rule: unreachable data is not scored from cache, and a closed
source cannot be outweighed by a large dollar amount.

Email also appends quoted conversation history. The first real channel test
exposed this immediately; RewardOps initially parsed the quoted text as extra
arguments. We added reply-safe extraction and a regression test, then repeated
the live email flow successfully.

## Accomplishments

- A real email round trip through Caspian, not a mocked transport.
- The same handler and scoring path on a second Slack channel.
- Live detection of a stale $1,000 bounty as `SKIP`.
- Explainable evidence and risk output instead of a black-box recommendation.
- Seven regression tests plus a public two-version CI matrix.
- Safe behavior: public metadata only, no maintainer outreach, no auto-claims, and
  no security testing.

## What we learned

Cross-channel behavior is not only transport plumbing. Email quotation, rich-card
support, threading, and response length all affect how an agent interprets and
communicates evidence. Caspian let the project keep those differences at the
communication layer while the verification workflow remained a single handler.

## What's next

- GitLab and Jira issue adapters
- signed marketplace adapters for direct pool verification
- scheduled re-verification and change alerts
- payout-currency conversion with timestamped FX evidence
- optional team policy profiles for minimum reward, maximum competition, and
  allowed payout rails
- human-approved claim preparation after a `PURSUE` decision

## Links

- Repository: https://github.com/SmartMenu9872/rewardops-agent
- Caspian Buildathon: https://caspian.devpost.com/
