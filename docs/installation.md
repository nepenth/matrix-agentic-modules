# v0.3 Installation

```yaml
modules:
  - module: synapse_matrix_agentic.AgentFirstModule
    config:
      agent_user_prefix: "agent_"
      require_approval_for_tools: true
      approver_users:
        - "@admin:yourserver.com"
      default_session_scope: "room"
```

**New endpoint:** POST `/_synapse/admin/agent/trigger` (for external triggers from Hermes or other AI systems).