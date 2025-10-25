"""Proxy endpoints for forwarding Archon prompts to local Ollama and delegating design specs."""

from typing import Any, Dict, List, Literal, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ArcaneOS.daemons.claude_exec import execute as claude_execute
from app.config import settings

router = APIRouter(prefix="/archon", tags=["Archon"])


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ArchonChatRequest(BaseModel):
    prompt: str
    history: List[ChatTurn] = []


class ArchonChatResponse(BaseModel):
    message: Optional[str] = None
    raw: Dict[str, Any]


@router.post("/chat", response_model=ArchonChatResponse)
async def relay_archon_prompt(payload: ArchonChatRequest) -> ArchonChatResponse:
    ollama_url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    body = {
        "model": settings.ollama_model,
        "messages": [
            {
                "role": "system",
                "content": f"{settings.archon_console_prompt} {settings.archon_base_narration}",
            },
            *[turn.dict() for turn in payload.history],
            {"role": "user", "content": payload.prompt},
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
        response = await client.post(ollama_url, json=body)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail={"error": f"Ollama responded with {response.status_code}", "body": response.text},
        )

    data = response.json()
    message = (
        data.get("message", {}).get("content")
        or data.get("output")
        or ""
    )
    return ArchonChatResponse(message=message, raw=data)


class ClaudeCodeRequest(BaseModel):
    spec: Dict[str, Any]
    prompt: Optional[str] = None


class ClaudeCodeResponse(BaseModel):
    success: bool
    result: Dict[str, Any]


@router.post("/claude-code", response_model=ClaudeCodeResponse)
async def invoke_claude_code(payload: ClaudeCodeRequest) -> ClaudeCodeResponse:
    try:
        result = claude_execute("apply_spec", {"spec": payload.spec, "prompt": payload.prompt})
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=502, detail={"error": str(exc)}) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail={"error": "claude_exec returned an invalid response", "result": result},
        )

    success = bool(result.get("success", True))
    if not success and "error" in result:
        raise HTTPException(status_code=502, detail=result)

    return ClaudeCodeResponse(success=success, result=result)
