"""Validation helpers for Archon directives."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError, conlist, constr

from ArcaneOS.core import grimoire

REDACT_PATTERN = re.compile(r"([A-Za-z]:\\[^\s]+|/[^\s]+)")


class SafetySettings(BaseModel):
    allow_shell: bool = False
    allow_net: bool = False


class StyleSettings(BaseModel):
    fantasy: bool = True
    voice: Literal["archon", "claude", "gemini"] = "archon"


class ArchonDirective(BaseModel):
    intent: Literal["summon", "invoke", "banish", "reveal"]
    daemon: Literal["claude", "gemini", "liquidmetal", "none"]
    task: constr(strip_whitespace=True, max_length=140)
    safety: SafetySettings
    style: StyleSettings
    parameters: Optional[Dict[str, Any]] = None
    plan: conlist(constr(strip_whitespace=True, min_length=1), min_length=1)


def _log_rejection(reason: str, payload: Dict[str, Any]) -> None:
    log_line = json.dumps({
        "event": "REJECTED_PAYLOAD",
        "reason": reason,
        "payload": payload,
    })
    with Path(grimoire.GRIMOIRE_FILE).open("a", encoding="utf-8") as handle:
        handle.write(log_line + "\n")


def _redact_paths(text: str) -> str:
    return REDACT_PATTERN.sub("[path-redacted]", text)


def validate_archon_payload(payload: Dict[str, Any], fantasy_mode: bool) -> Dict[str, Any]:
    try:
        directive = ArchonDirective.parse_obj(payload)
    except ValidationError as exc:
        _log_rejection("schema_validation_error", payload)
        raise ValueError("Invalid Archon directive") from exc

    if not directive.safety.allow_shell:
        text_sources: List[str] = [directive.task, *directive.plan]
        if any("shell" in text.lower() for text in text_sources):
            _log_rejection("shell_command_disallowed", payload)
            raise ValueError("Shell execution requested but disallowed")

    cleaned = directive.dict()

    if fantasy_mode:
        cleaned["plan"] = [_redact_paths(step) for step in directive.plan]
    else:
        cleaned.setdefault("style", {})
        cleaned["style"]["fantasy"] = False

    return cleaned
