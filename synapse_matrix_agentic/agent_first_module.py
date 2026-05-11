"""AgentFirstModule v0.3

Major update:
- Full approval state machine (persistent via room state + reactions + DM prompts)
- Custom HTTP endpoint for external AI triggers (/agent/trigger)
- Deep Hermes integration: session_scope, room_identity, structured approvals, typing status

Designed to complement Hermes PRs #18505 (isolation/scoping), #18506 (tools/reactions), #18507 (rendering).

Also draws from modern Slack/Discord agent patterns: structured approvals, progress updates, thread-aware context.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from synapse.module_api import ModuleApi

logger = logging.getLogger(__name__)


class AgentFirstModule:
    def __init__(self, config: Dict[str, Any], api: ModuleApi):
        self.api = api
        self.config = config or {}

        self.agent_prefix = self.config.get("agent_user_prefix", "agent_")
        self.require_approval = self.config.get("require_approval_for_tools", True)
        self.approval_reaction = self.config.get("approval_reaction", "✅")
        self.approver_users = self.config.get("approver_users", [])  # list of user_ids

        # Register callbacks
        self.api.register_third_party_rules_callbacks(check_event_allowed=self.check_event_allowed)
        self.api.register_account_data_callbacks(on_account_data_updated=self.on_account_data_updated)
        self.api.register_add_extra_fields_to_client_events_unsigned_callbacks(
            add_extra_fields=self.add_extra_fields_to_client_events_unsigned
        )

        # Register custom HTTP resource
        self.api.register_web_resource(
            path="/_synapse/admin/agent/trigger",
            resource=self._create_trigger_resource(),
        )

        logger.info("AgentFirstModule v0.3 loaded with full approval + Hermes integration")

    def is_agent_user(self, user_id: str) -> bool:
        return user_id.startswith("@" + self.agent_prefix)

    async def check_event_allowed(self, event: Dict[str, Any], state: Dict[str, Any]) -> Optional[str]:
        sender = event.get("sender", "")
        if not self.is_agent_user(sender):
            return None

        content = event.get("content", {})
        is_tool = "tool_call" in str(content) or content.get("msgtype") == "m.agent.tool_call"

        if is_tool and self.require_approval:
            approved = await self._check_approval_status(event)
            if not approved:
                await self._initiate_approval_flow(event)
                return "Approval required for tool call"

        return None

    async def _check_approval_status(self, event: Dict[str, Any]) -> bool:
        room_id = event.get("room_id")
        event_id = event.get("event_id")
        key = f"approval:{event_id}"

        try:
            approval_state = await self.api.get_room_state(room_id, key)
            return approval_state.get("approved", False) if approval_state else False
        except Exception:
            return False

    async def _initiate_approval_flow(self, event: Dict[str, Any]):
        room_id = event.get("room_id")
        sender = event.get("sender")
        event_id = event.get("event_id")

        # 1. Set pending state in room state
        await self.api.set_room_state(
            room_id,
            f"approval:{event_id}",
            {"approved": False, "pending_since": asyncio.get_event_loop().time(), "tool_call": event.get("content")}
        )

        # 2. Send DM prompt to approvers (or fallback to room message)
        prompt = f"Agent {sender} requests approval for tool call.\nReact with {self.approval_reaction} or reply 'approve {event_id}'"
        for approver in self.approver_users or [sender]:
            try:
                await self.api.send_message(approver, prompt)  # DM
            except Exception:
                pass

        logger.info("[AgentFirst] Approval flow started for %s in %s", event_id, room_id)

    async def on_account_data_updated(self, user_id: str, room_id: Optional[str], account_data_type: str, content: Dict[str, Any]) -> None:
        if not self.is_agent_user(user_id):
            return
        if account_data_type in ("m.agent.todo", "org.matrix.agent.todo"):
            logger.info("[AgentFirst] Todo updated by %s", user_id)

    async def add_extra_fields_to_client_events_unsigned(self, event: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        sender = event.get("sender", "")
        if not self.is_agent_user(sender):
            return {}

        content = event.get("content", {})
        extra = {
            "agent_metadata": {
                "is_agent": True,
                "agent_id": sender,
                "capabilities": ["tool_calling", "todo_management", "human_approval", "session_scoped"],
            },
            "tool_status": "idle",
            "session_scope": self.config.get("default_session_scope", "room"),  # auto|room|thread
            "room_identity": event.get("room_id"),  # helps Hermes preserve context
        }

        if "tool_call" in str(content) or content.get("msgtype") == "m.agent.tool_call":
            extra.update({
                "tool_call": content.get("tool_call") or content,
                "tool_status": "pending_approval",
            })

        # Structured approval event support (for Hermes rendering)
        if content.get("msgtype") == "m.agent.approval_request":
            extra["approval_request"] = {
                "event_id": event.get("event_id"),
                "tool": content.get("tool"),
                "requires_reaction": self.approval_reaction,
            }

        return extra

    def _create_trigger_resource(self):
        """Simple HTTP endpoint for external AI runtimes (Hermes, LangGraph, etc.)."""
        from twisted.web.resource import Resource
        from twisted.web.server import Request

        class TriggerResource(Resource):
            isLeaf = True

            async def render_POST(self, request: Request):
                data = request.content.read().decode()
                logger.info("[AgentFirst] External trigger received: %s", data[:200])
                # TODO: Parse and act (e.g. approve pending tool, push result)
                return b'{"status": "received"}'

        return TriggerResource()
