# Installation (v0.2)

## 1. Add the module

```yaml
modules:
  - module: synapse_matrix_agentic.AgentFirstModule
    config:
      agent_user_prefix: "agent_"
      require_approval_for_tools: true
      approval_reaction: "✅"
```

## 2. Restart Synapse

## 3. Test with an agent

Send a message containing "tool_call" from @agent_xxx:yourserver

Watch logs and check event `unsigned` fields in clients that support it (or via `/sync`).

## Recommended Clients
- Hermes Agent (your PRs)
- Custom Element fork with agent UI components
- Any client that reads `unsigned.agent_metadata`