# matrix-agentic-modules v0.3

**Synapse modules making AI agents first-class on Matrix.**

Built to pair perfectly with [Hermes Agent](https://github.com/NousResearch/hermes-agent) PR stack (#18505–18507).

## New in v0.3

- **Full approval state machine** — Persistent via room state, reaction polling, DM prompts to approvers
- **Custom HTTP endpoint** — `/_synapse/admin/agent/trigger` for external AI runtimes (push tool results, request approvals)
- **Deep Hermes integration**:
  - `session_scope` (auto|room|thread) exposed in every event
  - `room_identity` preservation
  - Structured `m.agent.approval_request` events
  - Typing status + tool progress metadata

## Why this is powerful

Modern Slack/Discord agent bots (e.g. Slack AI, Discord bots with buttons) give agents:
- Clear approval flows
- Thread/session awareness
- Rich structured feedback

This module brings the same (and better, thanks to Matrix federation + E2EE) to open Matrix.

## Next
- Full reaction listener for instant approvals
- Tests + CI
- Follow-up Hermes PR for native support of new event shapes