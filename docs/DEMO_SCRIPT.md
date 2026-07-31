# Live demo script (target: 2:20)

The video must show real channel behavior. Do not splice a fake reply into the
recording.

## 0:00–0:15 — Problem

Show the public marketplace card for `BasedHardware/omi#2316` advertising a
$1,000 bounty.

Narration:

> A high reward is not evidence that work is still claimable. RewardOps checks
> the source of truth before a developer spends a day on it.

## 0:15–0:50 — Email channel

In the dedicated email thread, reply:

```text
scan https://github.com/BasedHardware/omi/issues/2316
```

Show RewardOps returning:

- `SKIP — 0/100`
- `$1,000.00`
- `State: closed`
- the live verification timestamp
- concrete signals and risks

Call out that the response came through the Caspian inbox.

## 0:50–1:25 — Slack channel

Send the same command in the dedicated RewardOps Slack workspace. Show the rich
card response. Explain that this is the same process and the same
`@client.on_message` handler, not a second Slack-specific implementation.

## 1:25–1:50 — Competition sensing

Send a currently open bounty URL with visible work-intent comments. Show the
attempt count and explain how competition lowers the score without creating an
opaque hard reject.

## 1:50–2:10 — Watchlist

Send:

```text
watch <open issue URL>
digest
```

Show the saved, evidence-ranked digest.

## 2:10–2:20 — Close

> RewardOps turns reward hunting from marketplace browsing into an evidence
> workflow: live source, explainable risk, one agent identity, every channel.

End on the public GitHub repository URL.

## Recording checklist

- Capture one continuous run for the two channel responses.
- Keep the video under three minutes.
- Hide personal inbox content; show only the dedicated RewardOps thread/workspace.
- Do not expose API keys, OAuth state, private email, or payment details.
- Host on Loom and keep the link publicly accessible for judging.

