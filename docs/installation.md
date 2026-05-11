# Installation & Configuration

## Prerequisites
- Synapse >= 1.100
- Python 3.10+

## Steps

1. Clone or copy this package into your Synapse environment
   (or `pip install -e .` after adding to PYTHONPATH)

2. Add to your `homeserver.yaml`:

```yaml
modules:
  - module: synapse_matrix_agentic.AgentFirstModule
    config:
      agent_user_prefix: "agent_"
      require_approval_for_tools: true
```

3. Restart Synapse.

## Testing
Create an agent account (@agent_grok:your.domain) and send messages containing "tool_call".

Check logs for [AgentFirst] messages.

## Next Steps
- Implement full approval state machine
- Add extra_fields callback for rich client metadata
- Add custom web resource for external AI triggers
