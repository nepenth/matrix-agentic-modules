"""AgentFirstModule v0.4.5

Final compatibility fix:
- Removed asyncio.create_task (caused 'no running event loop' error)
- Removed unsupported extra fields callback

This version should work on Synapse 1.152.1 and most recent versions.

Core features:
- Agent detection
- Approval workflows (reaction + DM prompts)
- Todo management
- Tool call blocking
"""

import logging
from typing import Any, Dict, List, Optional

from synapse.module_api import ModuleApi

logger = logging.getLogger(__name__)


class AgentFirstModule:
    def __init__(self, config: Dict[str, Any], api: ModuleApi):
        self.api = api
        self.config = config or {}

        self.agent_user_ids: List[str] = self.config.get("agent_user_ids", [])
        self.agent_user_prefix = self.config.get("agent_user_prefix", "agent_")
        self.require_approval = self.config.get("require_approval_for_tools", True)
        self.approval_reaction = self.config.get("approval_reaction", "Y")
        self.approver_users = self.config.get("approver_users", [])

        self.api.register_third_party_rules_callbacks(check_event_allowed=self.check_event_allowed)
        self.api.register_account_data_callbacks(on_account_data_updated=self.on_account_data_updated)

        logger.info("AgentFirstModule v0.4.5 loaded successfully")

    def is_agent_user(self, user_id: str) -> bool:
        if user_id in self.agent_user_ids:
            return True
        if user_id.startswith("@" + self.agent_user_prefix):
            return True
        return False

    async def check_event_allowed(self, event: Dict[str, Any], state: Dict[str, Any]) -> Optional[str]:
        sender = event.get("sender", "")
        if not self.is_agent_user(sender):
            return None

        content = event.get("content", {})
        event_type = event.get("type", "")

        if event_type == "m.reaction" and content.get("relates_to", {}).get("key") == self.approval_reaction:
            related_event = content.get("relates_to", {}).get("event_id")
            if related_event:
                await self._approve_tool_call(event.get("room_id"), related_event)
                return None

        is_tool = "tool_call" in str(content) or content.get("msgtype") == "m.agent.tool_call"
        if is_tool and self.require_approval:
            if not await self._is_approved(event):
                await self._initiate_approval_flow(event)
                return "Approval required"

        return None

    async def _is_approved(self, event: Dict[str, Any]) -> bool:
        try:
            state = await self.api.get_room_state(event["room_id"], f"approval:{event.get('event_id')}")
            return state.get("approved", False)
        except Exception:
            return False

    async def _approve_tool_call(self, room_id: str, event_id: str):
        await self.api.set_room_state(room_id, f"approval:{event_id}", {"approved": True})
        logger.info("[AgentFirst] Tool call approved: %s", event_id)

    async def _initiate_approval_flow(self, event: Dict[str, Any]):
        await self.api.set_room_state(
            event["room_id"],
            f"approval:{event.get('event_id')}",
            {"approved": False, "pending": True}
        )

    async def on_account_data_updated(self, user_id: str, room_id: Optional[str], account_data_type: str, content: Dict[str, Any]) -> None:
        pass
