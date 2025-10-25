"""
ArcaneEventBus - Real-time Event Dispatcher for ArcaneOS

Migrated into ArcaneOS.core.event_bus for consolidated backend structure.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ArcaneOS.core.veil import is_fantasy_mode

logger = logging.getLogger(__name__)


class SpellType(str, Enum):
    SUMMON = "summon"
    INVOKE = "invoke"
    BANISH = "banish"
    REVEAL = "reveal"
    PARSE = "parse"
    VOICE = "voice"
    ROUTE = "route"


class ArcaneEvent:
    def __init__(
        self,
        spell_name: SpellType,
        daemon_name: Optional[str] = None,
        success: bool = True,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.spell_name = spell_name
        self.daemon_name = daemon_name
        self.success = success
        self.description = description
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spell_name": self.spell_name.value,
            "daemon_name": self.daemon_name,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "description": self.description,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class ArcaneEventBus:
    def __init__(self) -> None:
        self._subscribers: Set[asyncio.Queue] = set()
        self._event_history: List[ArcaneEvent] = []
        self._max_history = 100
        self._lock = asyncio.Lock()
        logger.info("✨ ArcaneEventBus initialized - The ethereal channels are open")

    async def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    def _build_sync_directives(self, success: bool, failure_phrase: Optional[str] = None) -> Dict[str, Any]:
        if not is_fantasy_mode():
            directives: Dict[str, Any] = {
                "mode": "developer",
                "deadline_ms": 50,
                "animation": None,
                "particles": "halt",
                "audio": None,
                "invert": False,
            }
            if failure_phrase:
                directives["failure"] = failure_phrase
            return directives

        directives: Dict[str, Any] = {
            "mode": "fantasy",
            "deadline_ms": 200,
        }
        if success:
            directives.update({
                "animation": "pulse",
                "particles": "fade_to_idle",
                "audio": "success",
                "invert": False,
            })
        else:
            directives.update({
                "animation": "invert",
                "particles": "halt",
                "audio": "error",
                "invert": True,
                "text_color": "#ff1744",
            })
            if failure_phrase:
                directives["display_text"] = failure_phrase
        return directives

    async def emit(self, event: ArcaneEvent) -> None:
        async with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)

            dead: Set[asyncio.Queue] = set()
            for queue in self._subscribers:
                try:
                    await queue.put(event)
                except Exception:
                    dead.add(queue)

            for queue in dead:
                self._subscribers.discard(queue)

        logger.info("✨ Event emitted: %s - %s - %s", event.spell_name.value, event.daemon_name, event.success)

    async def emit_route(self, daemon_name: str, success: bool, metadata: Optional[Dict[str, Any]] = None) -> None:
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(success, metadata.get("failure_phrase")))
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.ROUTE,
                daemon_name=daemon_name,
                success=success,
                description="Route decision emitted",
                metadata=metadata,
            )
        )

    async def emit_summon(
        self,
        daemon_name: str,
        success: bool = True,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if description is None:
            description = (
                f"✨ The runes pulse as {daemon_name.upper()} materializes."
                if success
                else f"✨ {daemon_name.upper()} resists the call."
            )
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(success, metadata.get("failure_phrase")))
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.SUMMON,
                daemon_name=daemon_name,
                success=success,
                description=description,
                metadata=metadata,
            )
        )

    async def emit_invoke(
        self,
        daemon_name: str,
        task: str,
        success: bool = True,
        execution_time: Optional[float] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(success, metadata.get("failure_phrase")))
        metadata["task"] = task
        metadata["execution_time"] = execution_time
        if description is None:
            description = (
                f"✨ {daemon_name.upper()} completes '{task}'." if success else f"✨ {daemon_name.upper()} falters on '{task}'."
            )
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.INVOKE,
                daemon_name=daemon_name,
                success=success,
                description=description,
                metadata=metadata,
            )
        )

    async def emit_banish(
        self,
        daemon_name: str,
        invocation_count: int = 0,
        total_time: float = 0.0,
        success: bool = True,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(success, metadata.get("failure_phrase")))
        metadata["invocation_count"] = invocation_count
        metadata["total_time"] = total_time
        if description is None:
            description = (
                f"✨ {daemon_name.upper()} returns to the ethereal void."
                if success
                else f"✨ {daemon_name.upper()} resists banishment."
            )
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.BANISH,
                daemon_name=daemon_name,
                success=success,
                description=description,
                metadata=metadata,
            )
        )

    async def emit_reveal(
        self,
        daemon_name: Optional[str] = None,
        is_active: bool = False,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(True, metadata.get("failure_phrase")))
        if description is None:
            description = "✨ The veil parts, revealing the current realm state. ✨"
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.REVEAL,
                daemon_name=daemon_name,
                success=True,
                description=description,
                metadata=metadata,
            )
        )

    async def emit_parse(
        self,
        spell_text: str,
        success: bool,
        parsed_action: Optional[str] = None,
        daemon_name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(success, metadata.get("failure_phrase")))
        metadata["spell_text"] = spell_text
        metadata["parsed_action"] = parsed_action
        if description is None:
            description = (
                f"✨ Runes clarify '{spell_text}' → {parsed_action}. ✨" if success else f"✨ '{spell_text}' defies translation. ✨"
            )
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.PARSE,
                daemon_name=daemon_name,
                success=success,
                description=description,
                metadata=metadata,
            )
        )

    async def emit_voice(
        self,
        daemon_name: str,
        success: bool,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        metadata = dict(metadata or {})
        metadata.setdefault("sync", self._build_sync_directives(success, metadata.get("failure_phrase")))
        if description is None:
            description = (
                f"✨ {daemon_name.upper()} shares an utterance."
                if success
                else f"✨ {daemon_name.upper()} falls silent."
            )
        await self.emit(
            ArcaneEvent(
                spell_name=SpellType.VOICE,
                daemon_name=daemon_name,
                success=success,
                description=description,
                metadata=metadata,
            )
        )

    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        return [event.to_dict() for event in self._event_history[-count:]]

    def get_subscriber_count(self) -> int:
        return len(self._subscribers)


_event_bus: Optional[ArcaneEventBus] = None


def get_event_bus() -> ArcaneEventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = ArcaneEventBus()
    return _event_bus
