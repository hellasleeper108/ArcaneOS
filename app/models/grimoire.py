"""
Pydantic Models for The Grimoire

These models define the request and response structures for grimoire
spell history endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class SpellType(str, Enum):
    """Types of spells that can be recorded"""
    SUMMON = "summon"
    INVOKE = "invoke"
    BANISH = "banish"
    PARSE = "parse"
    COMPILE = "compile"
    REVEAL = "reveal"
    QUERY = "query"


class RecordSpellRequest(BaseModel):
    """Request to record a spell in the grimoire"""

    spell_name: str = Field(
        ...,
        description="Name of the spell being cast",
        min_length=1,
        max_length=200
    )

    command: Dict[str, Any] = Field(
        ...,
        description="The command/parameters of the spell"
    )

    result: Dict[str, Any] = Field(
        ...,
        description="The result of the spell casting"
    )

    spell_type: Optional[SpellType] = Field(
        None,
        description="Type of spell (summon, invoke, etc.)"
    )

    daemon_name: Optional[str] = Field(
        None,
        description="Name of daemon involved (if any)"
    )

    success: bool = Field(
        default=True,
        description="Whether the spell succeeded"
    )

    execution_time: Optional[float] = Field(
        None,
        description="How long the spell took to execute in seconds",
        ge=0
    )

    class Config:
        schema_extra = {
            "example": {
                "spell_name": "summon_claude",
                "command": {"daemon_name": "claude"},
                "result": {"status": "summoned", "message": "Claude awakens!"},
                "spell_type": "summon",
                "daemon_name": "claude",
                "success": True,
                "execution_time": 0.234
            }
        }


class GrimoireEntryResponse(BaseModel):
    """A single entry from the grimoire"""

    timestamp: float = Field(..., description="Unix timestamp of when spell was cast")
    datetime: str = Field(..., description="Human-readable datetime")
    spell_name: str = Field(..., description="Name of the spell")
    spell_type: Optional[str] = Field(None, description="Type of spell")
    daemon_name: Optional[str] = Field(None, description="Daemon involved")
    command: Dict[str, Any] = Field(..., description="Spell command/parameters")
    result: Dict[str, Any] = Field(..., description="Spell result")
    success: bool = Field(..., description="Whether spell succeeded")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

    class Config:
        schema_extra = {
            "example": {
                "timestamp": 1730000000.123,
                "datetime": "2025-10-24T12:34:56.123000",
                "spell_name": "summon_claude",
                "spell_type": "summon",
                "daemon_name": "claude",
                "command": {"daemon_name": "claude"},
                "result": {"status": "summoned"},
                "success": True,
                "execution_time": 0.234
            }
        }


class RecallSpellsResponse(BaseModel):
    """Response containing recalled spells"""

    status: str = Field(default="success")
    message: str = Field(..., description="Fantasy-themed message")
    spells: List[GrimoireEntryResponse] = Field(..., description="List of spell entries")
    count: int = Field(..., description="Number of spells returned")
    total_available: Optional[int] = Field(None, description="Total spells in grimoire")


class GrimoireStatsResponse(BaseModel):
    """Response containing grimoire statistics"""

    status: str = Field(default="success")
    message: str = Field(..., description="Fantasy-themed message")
    statistics: Dict[str, Any] = Field(..., description="Grimoire statistics")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "✨ The grimoire reveals its mysteries...",
                "statistics": {
                    "total_spells": 42,
                    "spell_types": {"summon": 15, "invoke": 20, "banish": 7},
                    "daemon_usage": {"claude": 25, "gemini": 12, "liquidmetal": 5},
                    "success_count": 40,
                    "fail_count": 2,
                    "success_rate": 95.24,
                    "total_execution_time": 12.345,
                    "average_execution_time": 0.294,
                    "oldest_spell": "2025-10-20T10:00:00",
                    "newest_spell": "2025-10-24T15:30:00",
                    "file_size_bytes": 25600
                }
            }
        }


class PurgeSpellsResponse(BaseModel):
    """Response from purging old spells"""

    status: str = Field(default="success")
    message: str = Field(..., description="Fantasy-themed message")
    purged_count: int = Field(..., description="Number of spells purged")
    archive_file: Optional[str] = Field(None, description="Path to archive file")


class SearchSpellsRequest(BaseModel):
    """Request to search spells"""

    query: str = Field(
        ...,
        description="Search query",
        min_length=1,
        max_length=200
    )

    limit: int = Field(
        default=10,
        description="Maximum number of results",
        ge=1,
        le=100
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "claude",
                "limit": 10
            }
        }


class SearchSpellsResponse(BaseModel):
    """Response containing search results"""

    status: str = Field(default="success")
    message: str = Field(..., description="Fantasy-themed message")
    query: str = Field(..., description="Search query used")
    spells: List[GrimoireEntryResponse] = Field(..., description="Matching spell entries")
    count: int = Field(..., description="Number of results")
