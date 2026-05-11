"""AgentFirstModule

Makes AI agents first-class participants on Synapse.

Features:
- Agent detection
- Tool call / result metadata enrichment
- Human approval workflows (stub for now, extensible)
- Todo list management via account data
- Logging and audit hooks

Complements client-side Hermes Agent improvements.
"""

import logging
from typing import Any, Dict, Optional

from synapse.module_api import ModuleApi

logger = logging.getLogger(__name__)


class AgentFirstModule:
    """Core module for agentic Matrix features."""

    def __init__(self, config: Dict[str, Any], api: ModuleApi):
        self.api = api
        self.config = config or {}

        self.agent_prefix = self.config.get("agent_user_prefix", "agent_")
        self.require_approval = self.config.get("require_approval_for_tools", True)

        # Register callbacks
        self.api.register_third_party_rules_callbacks(
            check_event_allowed=self.check_event_allowed
        )
        self.api.register_account_data_callbacks(
            on_account_data_updated=self.on_account_data_updated
        )

        logger.info("AgentFirstModule loaded successfully")

    def is_agent_user(self, user_id: str) -> bool:
        return user_id.startswith("@" + self.agent_prefix) or "agent" in user_id.lower()

    async def check_event_allowed(
        self, event: Dict[str, Any], state: Dict[str, Any]
    ) -> Optional[str]:
        sender = event.get("sender", "")
        content = event.get("content", {})

        if not self.is_agent_user(sender):
            return None

        # Tool call detection (extend with your schema)
        body = content.get("body", "")
        if "tool_call" in body or content.get("msgtype") == "m.agent.tool_call":
            if self.require_approval:
                logger.info("[AgentFirst] Tool call from %s requires approval (stub)", sender)
                # TODO: Real implementation - check room state for approval reaction
                # or query external approval service
                # return "Tool call pending human approval"

        return None  # Allow for now

    async def on_account_data_updated(
        self,
        user_id: str,
        room_id: Optional[str],
        account_data_type: str,
        content: Dict[str, Any],
    ) -> None:
        if not self.is_agent_user(user_id):
            return

        if account_data_type in ("m.agent.todo", "org.matrix.agent.todo"):
            logger.info("[AgentFirst] Todo updated by %s in %s", user_id, room_id)
            # Future: Mirror to audit room or trigger notifications
