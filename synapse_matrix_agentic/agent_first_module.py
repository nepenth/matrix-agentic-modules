"""AgentFirstModule - Advanced agentic features for Synapse

Version 0.2 - Includes:
- Extra fields callback for rich client rendering (key for Hermes integration)
- Improved agent registration via account data
- Approval workflow foundation (state machine stub + reaction support)
- Todo summary injection

Complements Hermes Agent PRs #18505 (room isolation), #18506 (tools/reactions), #18507 (rendering/E2EE).
"""

import logging
from typing import Any, Dict, List, Optional

from synapse.module_api import ModuleApi, UserID

logger = logging.getLogger(__name__)


class AgentFirstModule:
    def __init__(self, config: Dict[str, Any], api: ModuleApi):
        self.api = api
        self.config = config or {}

        self.agent_prefix = self.config.get("agent_user_prefix", "agent_")
        self.require_approval = self.config.get("require_approval_for_tools", True)
        self.approval_reaction = self.config.get("approval_reaction", "✅")  # white_check_mark

        # Register all callbacks
        self.api.register_third_party_rules_callbacks(
            check_event_allowed=self.check_event_allowed
        )
        self.api.register_account_data_callbacks(
            on_account_data_updated=self.on_account_data_updated
        )
        self.api.register_add_extra_fields_to_client_events_unsigned_callbacks(
            add_extra_fields=self.add_extra_fields_to_client_events_unsigned
        )

        logger.info("AgentFirstModule v0.2 loaded")

    def is_agent_user(self, user_id: str) -> bool:
        """Check if user is an agent (prefix or special account data)."""
        if user_id.startswith("@" + self.agent_prefix):
            return True
        # Future: check for m.agent.profile account data
        return False

    async def get_agent_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch agent-specific account data (extend with m.agent.* types)."""
        try:
            profile = await self.api.get_account_data(user_id, "m.agent.profile")
            return profile or {}
        except Exception:
            return {}

    async def check_event_allowed(
        self, event: Dict[str, Any], state: Dict[str, Any]
    ) -> Optional[str]:
        sender = event.get("sender", "")
        content = event.get("content", {})
        room_id = event.get("room_id")

        if not self.is_agent_user(sender):
            return None

        # Detect tool calls (support both simple and structured)
        is_tool_call = (
            "tool_call" in str(content.get("body", "")) or
            content.get("msgtype") == "m.agent.tool_call" or
            "function_call" in content
        )

        if is_tool_call and self.require_approval:
            # Check for existing approval (reaction or state)
            approved = await self._is_approved(room_id, event.get("event_id"))
            if not approved:
                logger.info("[AgentFirst] Blocking tool call from %s - awaiting approval", sender)
                # In production: send DM to approvers or create approval event
                return "Tool call pending human approval (reaction with ✅ required)"

        return None

    async def _is_approved(self, room_id: str, event_id: str) -> bool:
        """Stub: Check room state or reactions for approval. Extend with real logic."""
        # TODO: Query reactions or dedicated approval state event
        # For now return True after first tool call (demo mode)
        return True

    async def on_account_data_updated(
        self, user_id: str, room_id: Optional[str], account_data_type: str, content: Dict[str, Any]
    ) -> None:
        if not self.is_agent_user(user_id):
            return

        if account_data_type in ("m.agent.todo", "org.matrix.agent.todo"):
            logger.info("[AgentFirst] Todo list updated by agent %s", user_id)

    async def add_extra_fields_to_client_events_unsigned(
        self, event: Dict[str, Any], *args, **kwargs
    ) -> Dict[str, Any]:
        """Inject rich metadata for client rendering (Hermes, Element, custom clients)."""
        sender = event.get("sender", "")
        if not self.is_agent_user(sender):
            return {}

        content = event.get("content", {})
        extra = {
            "agent_metadata": {
                "is_agent": True,
                "agent_id": sender,
                "capabilities": ["tool_calling", "todo_management", "human_approval"],
            },
            "tool_status": "idle",
            "todo_summary": None,
        }

        # Tool call detection
        if "tool_call" in str(content.get("body", "")) or content.get("msgtype") == "m.agent.tool_call":
            extra["tool_call"] = content.get("tool_call") or {"raw": content.get("body")}
            extra["tool_status"] = "pending_approval" if self.require_approval else "executing"

        # Todo summary (if recent account data)
        try:
            todo = await self.api.get_account_data(sender, "m.agent.todo")
            if todo:
                extra["todo_summary"] = {
                    "pending": len(todo.get("items", [])),
                    "last_updated": todo.get("last_updated"),
                }
        except Exception:
            pass

        return extra
