"""Live terminal spell streaming via Server-Sent Events."""

import json
import asyncio
from typing import AsyncGenerator, Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.terminal import TerminalSpellRequest
from app.services.archon_router import get_archon_router
from ArcaneOS.core.veil import is_fantasy_mode


TEAL = "#14b8a6"
AMBER = "#f59e0b"
CRIMSON = "#ef4444"


router = APIRouter(
    prefix="/terminal",
    tags=["Terminal"],
)


async def _tokenize(text: str) -> AsyncGenerator[str, None]:
    for segment in text.split():
        await asyncio.sleep(0)  # allow event loop to breathe
        yield segment


def _format_sse(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _wrap_rune(token: str) -> str:
    return f"ᚱ {token} ᚱ"


@router.post("", response_class=StreamingResponse)
async def terminal_stream(request: TerminalSpellRequest):
    archon = get_archon_router()
    fantasy = is_fantasy_mode()

    try:
        decision = archon.analyze_spell(request.spell)
        execution = archon.execute_decision(decision)
        status = "success"
    except HTTPException as exc:
        decision = None
        execution = {
            "status": "error",
            "error": exc.detail,
        }
        status = "failure"

    async def event_stream():
        if not fantasy:
            payload = {
                "mode": "developer",
                "status": status,
                "archon": decision.raw if decision else None,
                "execution": execution,
            }
            yield _format_sse({"text": json.dumps(payload, default=str), "color": TEAL if status == "success" else CRIMSON})
            return

        color = TEAL
        if decision and decision.fallback_used:
            color = AMBER
        if status == "failure":
            color = CRIMSON

        lines = []
        if decision:
            lines.append(decision.narration or "The Archon considers your plea.")
            if decision.reasoning:
                lines.append(decision.reasoning)
        if isinstance(execution, dict):
            lines.append(json.dumps(execution, ensure_ascii=False))

        for line in lines:
            async for token in _tokenize(line):
                rune = _wrap_rune(token)
                yield _format_sse({"text": rune, "color": color})

    headers = {"Content-Type": "text/event-stream", "Cache-Control": "no-cache", "Transfer-Encoding": "chunked"}
    return StreamingResponse(event_stream(), headers=headers)
