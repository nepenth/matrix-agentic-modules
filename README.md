# matrix-agentic-modules

**Professional Synapse module that makes AI agents first-class citizens on Matrix.**

This module turns a standard Synapse homeserver into a powerful platform for agentic workflows — with rich tool calling, human-in-the-loop approvals, todo management, progress updates, and structured metadata that clients like Hermes Agent can consume.

It is designed to work seamlessly with [Hermes Agent](https://github.com/NousResearch/hermes-agent) while remaining fully optional and backward compatible.

## Features

### Core Capabilities
- **Structured Tool Calling** — Agents can send `m.agent.tool_call` events with full metadata
- **Human-in-the-Loop Approvals** — Configurable approval workflows using reactions, DM prompts, or room state
- **Todo Management** — Persistent todo lists via `m.agent.todo` account data
- **Rich Progress Updates** — Real-time `tool_status` and typing indicators
- **Session & Room Awareness** — Exposes `session_scope` and `room_identity` for proper context handling

### Client-Side Integration
- Injects rich metadata into every agent event via the `unsigned` field
- Supports structured `m.agent.tool_result` and `m.agent.approval_request` events
- Compatible with Slack/Discord-style UX patterns (approval buttons, progress indicators, rich embeds)

### Technical Highlights
- Built on official Synapse Module API
- Zero breaking changes — works on any Synapse >= 1.100
- Fully configurable agent detection (supports custom user IDs, not just `@agent_*`)

## Version History

- **v0.4** (current) — Real reaction listener, typing indicators, `m.agent.tool_result` support, improved approval state machine
- **v0.3** — Full approval state machine + HTTP trigger endpoint + deep Hermes integration
- **v0.2** — Extra fields callback + approval foundation
- **v0.1** — Initial release

## Installation

### 1. Install the module

```bash
git clone https://github.com/nepenth/matrix-agentic-modules.git
cd matrix-agentic-modules
pip install -e .
```

### 2. Configure in `homeserver.yaml`

```yaml
modules:
  - module: synapse_matrix_agentic.AgentFirstModule
    config:
      # Agent detection (supports custom user IDs - see below)
      agent_user_ids:
        - "@forge.mymatrixserver.com"
        - "@claude:yourserver.com"
      # Or use prefix (default)
      # agent_user_prefix: "agent_"

      require_approval_for_tools: true
      approval_reaction: "✅"
      approver_users:
        - "@admin:yourserver.com"
      default_session_scope: "room"   # auto | room | thread
```

### 3. Restart Synapse

## Agent Detection (Flexible)

The module supports multiple ways to identify agents:

- **Custom user IDs** (recommended for existing setups): List specific Matrix IDs in `agent_user_ids`
- **Prefix matching**: Users starting with `agent_user_prefix` (default: `agent_`)
- **Future**: `m.agent.profile` account data flag

This makes it easy to use with existing agents that don't follow the `@agent_*` naming convention.

## How It Works

The module intercepts events from registered agents and enriches them with structured metadata in the `unsigned` section of the event. This metadata is consumed by clients (e.g. Hermes Agent) to provide rich UI surfaces.

Key injected fields:
- `agent_metadata`
- `tool_call` / `tool_result`
- `tool_status`
- `approval_request`
- `session_scope` + `room_identity`
- `typing_status`
- `todo_summary`

## Integration with Hermes Agent

This module is the server-side companion to Hermes Agent. When both are used together, you get:

- Slack/Discord-quality agent experience on Matrix
- Proper session scoping and room isolation
- Interactive approval flows
- Structured tool execution feedback

See the [Hermes Agent PR](https://github.com/NousResearch/hermes-agent/pull/XXXX) for client-side implementation details.

## HTTP Endpoint

`POST /_synapse/admin/agent/trigger` — Allows external systems (Hermes, LangGraph, etc.) to trigger actions or push results.

## Roadmap

- Full persistent approval event type (`m.agent.approval`)
- Native reaction listener (instead of polling)
- Enhanced todo synchronization
- Admin UI for managing agent approvals

## License

AGPL-3.0

## Contributing

Issues and PRs welcome. Please open an issue first to discuss major changes.

## Related Projects

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — The leading open-source agent framework with Matrix support
- [Element](https://element.io) — Popular Matrix client

---

**Maintained by nepenth** — Built to push the boundaries of agentic collaboration on Matrix.