# RewardOps

**Evidence before effort.**

RewardOps is a cross-channel agent that protects developers from wasting hours on
closed, stale, vague, or overcrowded software rewards. Send it a public GitHub
issue and it verifies the live source, extracts reward evidence, counts visible
attempts, applies hard-stop risk gates, and returns an explainable pursue/research/
skip decision.

The same Caspian `on_message` handler serves every connected channel. The
hackathon deployment is designed for email plus Discord; no handler is duplicated
and no channel-specific business logic exists.

## Why this exists

Reward marketplaces frequently preserve an old card after its underlying GitHub
issue has closed. A large dollar amount can also hide dozens of active attempts,
an assignee, missing payout mechanics, or a two-line scope. RewardOps checks the
source of truth at decision time and refuses to score unreachable sources from
stale cached data.

## What makes the agent different

- **Hard-stop verification:** a closed issue always scores `SKIP`, regardless of
  the advertised amount.
- **Evidence extraction:** common `$100`, `100 USD`, `350 USDC`, and `/bounty 100`
  formats are supported, with the matching source lines retained.
- **Competition sensing:** visible `/attempt`, `/claim`, and work-intent comments
  reduce the score.
- **Explainable decisions:** every score includes positive signals and risk flags.
- **Persistent watchlist:** `watch` saves evidence to SQLite; `digest` ranks it.
- **One Caspian handler:** email and Discord route through exactly the same command
  and response path, including rich cards and clean text fallbacks.
- **Reply-safe email parsing:** quoted reply history is removed before a command is
  evaluated, so email clients cannot accidentally turn one command into many.

## Commands

```text
scan https://github.com/<owner>/<repo>/issues/<number>
watch https://github.com/<owner>/<repo>/issues/<number>
digest
help
```

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

On Windows PowerShell, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

Create a Caspian project and connect two channels:

```bash
pip install caspian-cli
caspian init
caspian connect email
caspian connect discord
```

Authorize the returned Discord link, then start the one-handler agent:

```bash
rewardops-agent
```

For higher GitHub API limits, add `GITHUB_TOKEN` to `.env`. Never commit `.env`.

## Local evidence demo

The CLI exercises the exact same service used by Caspian:

```bash
rewardops scan https://github.com/BasedHardware/omi/issues/2316
```

Even if a marketplace still advertises this old `$1,000` bounty, RewardOps checks
GitHub live and returns `SKIP` because the issue is closed. That stale-card failure
mode is the core demo.

## Architecture

```text
Email ─────┐
           ├─ Caspian normalized message ─ one handler ─ evidence verifier
Discord ───┘                                      │
                                                  ├─ live GitHub API
                                                  ├─ scoring + risk gates
                                                  └─ SQLite watchlist
```

## Verification

```bash
ruff check .
ruff format --check .
pytest
```

Tests cover URL safety, reward extraction, the closed-source hard stop, competition
penalties, watchlist persistence, and channel-independent command handling.

## Responsible use

RewardOps only reads public issue metadata. It does not contact maintainers,
submit claims, scrape private data, or perform security testing. A high score is
evidence for human review, never a guarantee of payment.
