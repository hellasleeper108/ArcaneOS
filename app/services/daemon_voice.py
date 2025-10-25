"""
Daemon Voice Service for ArcaneOS

Provides asynchronous integration with ElevenLabs to synthesize daemon dialogue.
Each daemon has a unique vocal profile and tone. When audio generation fails,
the service falls back to textual narration and emits a voice event so clients
can react accordingly.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import httpx
import logging

from app.config import settings
from app.models.daemon import DaemonType
from app.services.arcane_event_bus import get_event_bus
from ArcaneOS.core.veil import is_fantasy_mode

logger = logging.getLogger(__name__)


class VoiceEvent(str, Enum):
    """Lifecycle moments that trigger daemon voice lines."""

    SUMMON = "summon"
    INVOKE = "invoke"
    BANISH = "banish"
    FAILURE = "failure"


VOICE_LINES: Dict[VoiceEvent, str] = {
    VoiceEvent.SUMMON: "I rise from the depths of code.",
    VoiceEvent.INVOKE: "Let the code flow through me.",
    VoiceEvent.BANISH: "I return to the void.",
    VoiceEvent.FAILURE: "The incantation fractures; the ether recoils.",
}


@dataclass(frozen=True)
class VoiceProfile:
    """Configuration describing a daemon's vocal identity."""

    daemon: DaemonType
    voice_id: str
    tone: str
    stability: float = 0.5
    similarity_boost: float = 0.7


@dataclass
class VoiceResult:
    """Outcome of attempting to synthesize a voice line."""

    success: bool
    daemon: DaemonType
    event: VoiceEvent
    audio_path: Optional[str] = None
    fallback_message: str = ""
    error: Optional[str] = None


class DaemonVoiceService:
    """
    Asynchronous voice synthesis orchestrator for ArcaneOS daemons.

    Uses ElevenLabs' REST API to render audio. Results are cached locally so
    clients can fetch the generated media. Failures are translated into
    textual narration to keep the experience immersive even without audio.
    """

    def __init__(self):
        self.enabled = settings.elevenlabs_enabled and bool(settings.elevenlabs_api_key)
        self.base_url = settings.elevenlabs_base_url.rstrip("/")
        self.model_id = settings.elevenlabs_model_id
        self.timeout = settings.elevenlabs_timeout
        self.cache_dir = Path(settings.voice_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.voice_profiles: Dict[DaemonType, VoiceProfile] = {
            DaemonType.CLAUDE: VoiceProfile(
                daemon=DaemonType.CLAUDE,
                voice_id=settings.voice_claude_id,
                tone="Measured resonance with analytical undertones",
                stability=0.65,
                similarity_boost=0.7,
            ),
            DaemonType.GEMINI: VoiceProfile(
                daemon=DaemonType.GEMINI,
                voice_id=settings.voice_gemini_id,
                tone="Warm, imaginative cadence with luminous flair",
                stability=0.55,
                similarity_boost=0.8,
            ),
            DaemonType.LIQUIDMETAL: VoiceProfile(
                daemon=DaemonType.LIQUIDMETAL,
                voice_id=settings.voice_liquidmetal_id,
                tone="Fluid metallic harmony with adaptive texture",
                stability=0.45,
                similarity_boost=0.75,
            ),
        }

    async def play_voice_line(
        self,
        daemon: DaemonType,
        event: VoiceEvent,
        override_text: Optional[str] = None
    ) -> VoiceResult:
        """
        Generate and cache a daemon voice line for the given event.

        Returns a VoiceResult describing either the audio path or fallback text.
        """
        phrase = override_text or VOICE_LINES[event]
        profile = self.voice_profiles.get(daemon)
        fallback_message = phrase

        if not is_fantasy_mode():
            reason = "Reality veil disabled"
            logger.info("Voice synthesis suppressed for %s (%s): %s", daemon.value, event.value, reason)
            await self._emit_voice_event(
                daemon_name=daemon.value,
                success=False,
                message=fallback_message,
                metadata={
                    "event": event.value,
                    "reason": reason,
                    "mode": "developer",
                },
            )
            return VoiceResult(
                success=False,
                daemon=daemon,
                event=event,
                fallback_message=fallback_message,
                error=reason,
            )

        if not self.enabled or profile is None:
            reason = (
                "Voice synthesis disabled"
                if not self.enabled
                else "Missing voice profile"
            )
            logger.warning(
                "Skipping voice synthesis for %s (%s): %s",
                daemon.value,
                event.value,
                reason,
            )
            await self._emit_voice_event(
                daemon_name=daemon.value,
                success=False,
                message=fallback_message,
                metadata={
                    "event": event.value,
                    "reason": reason,
                    "tone": profile.tone if profile else None,
                },
            )
            return VoiceResult(
                success=False,
                daemon=daemon,
                event=event,
                fallback_message=fallback_message,
                error=reason,
            )

        request_payload = {
            "text": phrase,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": profile.stability,
                "similarity_boost": profile.similarity_boost,
            },
            "output_format": "mp3_44100_128",
        }

        headers = {
            "xi-api-key": settings.elevenlabs_api_key or "",
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        try:
            logger.info(
                "Requesting ElevenLabs voice line for %s (%s)",
                daemon.value,
                event.value,
            )
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/text-to-speech/{profile.voice_id}",
                    headers=headers,
                    json=request_payload,
                )
            response.raise_for_status()
            audio_bytes = response.content
            audio_path = await self._persist_audio(daemon, event, audio_bytes)

            await self._emit_voice_event(
                daemon_name=daemon.value,
                success=True,
                message=f"{daemon.value} voiced the {event.value} ritual.",
                metadata={
                    "event": event.value,
                    "tone": profile.tone,
                    "audio_path": audio_path,
                },
            )

            return VoiceResult(
                success=True,
                daemon=daemon,
                event=event,
                audio_path=audio_path,
                fallback_message=fallback_message,
            )

        except Exception as exc:
            logger.exception(
                "Voice synthesis failed for %s (%s): %s",
                daemon.value,
                event.value,
                exc,
            )
            failure_message = (
                f"{phrase} [audio unavailable: {exc}]"
            )
            await self._emit_voice_event(
                daemon_name=daemon.value,
                success=False,
                message=failure_message,
                metadata={
                    "event": event.value,
                    "tone": profile.tone,
                    "error": str(exc),
                },
            )
            return VoiceResult(
                success=False,
                daemon=daemon,
                event=event,
                fallback_message=failure_message,
                error=str(exc),
            )

    async def _persist_audio(
        self,
        daemon: DaemonType,
        event: VoiceEvent,
        audio_bytes: bytes,
    ) -> str:
        """
        Persist audio bytes to the configured cache directory.

        Saves asynchronously using a worker thread to avoid blocking the event loop.
        """
        timestamp = int(time.time() * 1000)
        filename = f"{daemon.value}_{event.value}_{timestamp}.mp3"
        path = self.cache_dir / filename

        await asyncio.to_thread(path.write_bytes, audio_bytes)
        logger.info("Cached voice line for %s at %s", daemon.value, path)
        return str(path)

    async def _emit_voice_event(
        self,
        daemon_name: str,
        success: bool,
        message: str,
        metadata: Optional[Dict[str, object]] = None,
    ):
        """Emit a voice event through the ArcaneEventBus."""
        metadata = metadata or {}
        metadata.setdefault("success", success)
        event_bus = get_event_bus()
        await event_bus.emit_voice(
            daemon_name=daemon_name,
            success=success,
            description=message,
            metadata=metadata,
        )


# Singleton instance
_daemon_voice_service: Optional[DaemonVoiceService] = None


def get_daemon_voice_service() -> DaemonVoiceService:
    """Return the singleton DaemonVoiceService instance."""
    global _daemon_voice_service
    if _daemon_voice_service is None:
        _daemon_voice_service = DaemonVoiceService()
    return _daemon_voice_service
