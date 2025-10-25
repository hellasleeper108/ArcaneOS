"""
Daemon Models for ArcaneOS

Defines the mystical entities that serve the ArcaneOS realm.
Each daemon possesses unique attributes and capabilities.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class DaemonType(str, Enum):
    """The three primary daemon archetypes in ArcaneOS"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    LIQUIDMETAL = "liquidmetal"


class DaemonRole(str, Enum):
    """Roles that daemons can fulfill in the mystical realm"""
    LOGIC = "Keeper of Logic and Reason"
    CREATIVITY = "Weaver of Dreams and Innovation"
    ALCHEMY = "Master of Transformation and Flow"


class Daemon(BaseModel):
    """
    A mystical daemon entity in ArcaneOS.

    Each daemon serves a unique purpose in the operating environment,
    wielding specific powers and manifesting in a distinct ethereal hue.
    """
    name: DaemonType = Field(
        ...,
        description="The daemon's true name, which grants power over it"
    )
    role: str = Field(
        ...,
        description="The mystical role this daemon fulfills in the realm"
    )
    color_code: str = Field(
        ...,
        description="The ethereal hue in which this daemon manifests (hex code)"
    )
    is_summoned: bool = Field(
        default=False,
        description="Whether the daemon currently walks among us"
    )
    invocation_count: int = Field(
        default=0,
        description="Number of times this daemon has been invoked"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional mystical properties of the daemon"
    )


class SummonRequest(BaseModel):
    """Request to summon a daemon into the realm"""
    daemon_name: DaemonType = Field(
        ...,
        description="The name of the daemon to summon"
    )


class InvokeRequest(BaseModel):
    """Request to invoke a daemon's power"""
    daemon_name: DaemonType = Field(
        ...,
        description="The name of the daemon to invoke"
    )
    task: str = Field(
        ...,
        description="The mystical task to request of the daemon"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional parameters for the invocation"
    )


class BanishRequest(BaseModel):
    """Request to banish a daemon from the realm"""
    daemon_name: DaemonType = Field(
        ...,
        description="The name of the daemon to banish"
    )


class DaemonResponse(BaseModel):
    """Response from daemon operations"""
    status: str = Field(..., description="Status message in fantasy prose")
    daemon: Optional[Daemon] = Field(None, description="The affected daemon")
    message: str = Field(..., description="A mystical message about the operation")


class SpellParseRequest(BaseModel):
    """Request to parse a natural language spell"""
    spell: str = Field(
        ...,
        description="Natural language spell command",
        examples=["invoke claude to write code", "summon gemini"]
    )


class ParsedSpellResponse(BaseModel):
    """Response from spell parsing"""
    success: bool = Field(..., description="Whether parsing succeeded")
    action: Optional[str] = Field(None, description="Extracted action (summon/invoke/banish)")
    daemon: Optional[str] = Field(None, description="Extracted daemon name")
    task: Optional[str] = Field(None, description="Extracted task description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Extracted parameters")
    confidence: Optional[float] = Field(None, description="Parse confidence (0-1)")
    raw_input: Optional[str] = Field(None, description="Original input")
    error: Optional[str] = Field(None, description="Error message if parsing failed")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions if parsing failed")
    archon_narration: Optional[str] = Field(
        None,
        description="Roleplay narration supplied by The Archon"
    )
    archon_reasoning: Optional[str] = Field(
        None,
        description="Explanation of the Archon's decision"
    )
    archon_fallback_used: Optional[bool] = Field(
        None,
        description="Whether the Archon had to fall back to heuristic parsing"
    )
    archon_chain_of_thought: Optional[List[str]] = Field(
        None,
        description="Chain-of-thought steps provided by the Archon"
    )
    archon_confidence: Optional[float] = Field(
        None,
        description="Archon's self-reported confidence"
    )
    archon_raw_decision: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw decision payload returned by the Archon orchestrator"
    )
