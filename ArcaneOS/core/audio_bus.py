"""Non-blocking audio controller for ArcaneOS."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

SFX_FILES = {
    "success": "/sounds/system/success-flare.mp3",
    "warn": "/sounds/system/warn-chime.mp3",
    "fail": "/sounds/system/failure-dim.mp3",
}

VOICE_TEMPLATES: Dict[str, str] = {
    "archon.route": "I weigh your intent and set the path.",
    "claude.invoke.ok": "The spell holds. Code is forged.",
    "gemini.invoke.fail": "Runes shattered. The pattern is flawed.",
}

VOICE_PRESETS = {
    "archon": "archon",
    "claude": "claude",
    "gemini": "gemini",
}


class AudioBus:
    def __init__(self) -> None:
        self._loop = asyncio.get_event_loop()
        self._play_tasks: Dict[str, asyncio.Task] = {}
        self._sfx_cache = SFX_FILES.copy()

    async def queue_voice(self, voice_id: str, text: str, effect: Optional[str] = None) -> None:
        logger.debug("Queueing voice %s: %s", voice_id, text)
        await asyncio.sleep(0)
        # In production, integrate ElevenLabs / actual playback here.

    async def _speak(self, key: str, rendered: str) -> None:
        await asyncio.sleep(0)
        logger.info("🎙️ %s", rendered)

    def speak(self, entity: str, line_key: str, vars: Optional[Dict[str, Any]] = None) -> None:
        template_key = f"{entity}.{line_key}"
        template = VOICE_TEMPLATES.get(template_key)
        if not template:
            logger.warning("Unknown voice template: %s", template_key)
            return
        rendered = template.format(**(vars or {}))

        if entity in self._play_tasks:
            self._play_tasks[entity].cancel()

        task = self._loop.create_task(self._speak(template_key, rendered))
        self._play_tasks[entity] = task


audio_bus = AudioBus()


def get_audio_bus() -> AudioBus:
    return audio_bus
