# matrix-agentic-modules

**Synapse modules that make AI agents first-class citizens.**

Complements the excellent client-side work in [Hermes Agent](https://github.com/NousResearch/hermes-agent) (especially PRs #18505, #18506, #18507).

## Current Features (v0.2)

- **Extra fields callback** → Injects `agent_metadata`, `tool_call`, `tool_status`, `todo_summary` into every event’s `unsigned` section (perfect for rich client UIs)
- **Approval workflow foundation** → Blocks tool calls until human approval (reaction or DM-based)
- **Todo management** via account data (`m.agent.todo`)
- **Improved agent detection** (prefix + future account data profile)
- Logging and extensibility hooks

## Installation

See `docs/installation.md`

## Roadmap
- Full approval state machine with reaction support
- Custom HTTP endpoint for external AI triggers
- Tests + CI
- Native support for Hermes session scoping

## Why this matters

Together with your Hermes improvements (room isolation, reliable dispatch, tool/reaction handling), this creates a complete agent-native Matrix stack.