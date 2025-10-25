"""Pydantic schemas for ArcaneOS backend."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DaemonType(str, Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    LIQUIDMETAL = "liquidmetal"


class DaemonRole(str, Enum):
    LOGIC = "Keeper of Logic and Reason"
    CREATIVITY = "Weaver of Dreams and Innovation"
    ALCHEMY = "Master of Transformation and Flow"


class Daemon(BaseModel):
    name: DaemonType
    role: str
    color_code: str
    is_summoned: bool = False
    invocation_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


class SummonRequest(BaseModel):
    daemon_name: DaemonType


class InvokeRequest(BaseModel):
    daemon_name: DaemonType
    task: str
    parameters: Optional[Dict[str, Any]] = None


class BanishRequest(BaseModel):
    daemon_name: DaemonType


class DaemonResponse(BaseModel):
    status: str
    daemon: Optional[Daemon] = None
    message: str


class SpellParseRequest(BaseModel):
    spell: str = Field(..., description="Natural language spell command")


class ParsedSpellResponse(BaseModel):
    success: bool
    action: Optional[str] = None
    daemon: Optional[str] = None
    task: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    raw_input: Optional[str] = None
    error: Optional[str] = None
    suggestions: Optional[List[str]] = None
    archon_narration: Optional[str] = None
    archon_reasoning: Optional[str] = None
    archon_fallback_used: Optional[bool] = None
    archon_chain_of_thought: Optional[List[str]] = None
    archon_confidence: Optional[float] = None
    archon_raw_decision: Optional[Dict[str, Any]] = None


class VeilStatusResponse(BaseModel):
    veil: bool
    mode: str


class VeilUpdateRequest(BaseModel):
    veil: bool
