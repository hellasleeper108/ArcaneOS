"""
Grimoire Routes for ArcaneOS

These mystical endpoints allow you to record and recall spells from the eternal grimoire,
providing persistent memory across sessions.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.grimoire import (
    RecordSpellRequest,
    RecallSpellsResponse,
    GrimoireStatsResponse,
    PurgeSpellsResponse,
    SearchSpellsRequest,
    SearchSpellsResponse,
    GrimoireEntryResponse,
    SpellType
)
from app.services.grimoire import get_grimoire
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/grimoire",
    tags=["Grimoire"],
    responses={
        404: {"description": "The requested spell dwells not in the grimoire"},
        500: {"description": "Dark forces interfere with the grimoire"}
    }
)


@router.post("/record")
async def record_spell_endpoint(request: RecordSpellRequest):
    """
    📖 RECORD SPELL 📖

    Inscribes a spell into the eternal grimoire for all time.

    Every spell cast in ArcaneOS can be recorded here, creating a persistent
    memory layer that survives across sessions. The grimoire maintains:
    - Complete spell history with timestamps
    - Success/failure tracking
    - Execution time metrics
    - Daemon involvement records

    The recorded spells are stored in JSON Lines format (`grimoire_spells.jsonl`)
    and also logged to the standard logger (`arcane_log.txt`) for integrated tracking.

    **Use Cases:**
    - Track all daemon operations
    - Analyze spell patterns over time
    - Debug failed operations
    - Maintain session continuity

    Returns:
        Confirmation that the spell was inscribed
    """
    try:
        grimoire = get_grimoire()

        # Record the spell
        entry = grimoire.record_spell(
            spell_name=request.spell_name,
            command=request.command,
            result=request.result,
            spell_type=request.spell_type.value if request.spell_type else None,
            daemon_name=request.daemon_name,
            success=request.success,
            execution_time=request.execution_time
        )

        return {
            "status": "recorded",
            "message": f"✨ The spell '{request.spell_name}' has been inscribed in the eternal grimoire! ✨",
            "entry": entry.to_dict()
        }

    except Exception as e:
        logger.error(f"Failed to record spell: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"The grimoire refuses to record: {str(e)}"
        )


@router.get("/recall", response_model=RecallSpellsResponse)
async def recall_spells_endpoint(
    limit: int = Query(default=5, ge=1, le=100, description="Number of spells to recall"),
    spell_type: Optional[str] = Query(default=None, description="Filter by spell type"),
    daemon_name: Optional[str] = Query(default=None, description="Filter by daemon name"),
    success_only: bool = Query(default=False, description="Only recall successful spells")
):
    """
    🔮 RECALL SPELLS 🔮

    Summons recent spells from the grimoire's ancient pages.

    This endpoint retrieves spell history with optional filtering:
    - **limit**: How many spells to retrieve (default: 5, max: 100)
    - **spell_type**: Filter by type (summon, invoke, banish, etc.)
    - **daemon_name**: Show only spells involving a specific daemon
    - **success_only**: Only successful spells

    The spells are returned in reverse chronological order (most recent first).

    **Examples:**
    - `?limit=10` - Last 10 spells
    - `?spell_type=summon` - All summon spells
    - `?daemon_name=claude` - All spells involving Claude
    - `?success_only=true` - Only successful spells

    Returns:
        List of spell entries matching the criteria
    """
    try:
        grimoire = get_grimoire()

        spells = grimoire.recall_spells(
            limit=limit,
            spell_type=spell_type,
            daemon_name=daemon_name,
            success_only=success_only
        )

        # Convert to response models
        spell_responses = [
            GrimoireEntryResponse(**spell)
            for spell in spells
        ]

        # Build filter description
        filters = []
        if spell_type:
            filters.append(f"type={spell_type}")
        if daemon_name:
            filters.append(f"daemon={daemon_name}")
        if success_only:
            filters.append("successful only")

        filter_desc = f" ({', '.join(filters)})" if filters else ""

        return RecallSpellsResponse(
            status="success",
            message=f"✨ The grimoire reveals {len(spells)} spell(s){filter_desc}... ✨",
            spells=spell_responses,
            count=len(spells)
        )

    except Exception as e:
        logger.error(f"Failed to recall spells: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"The grimoire's pages remain sealed: {str(e)}"
        )


@router.get("/statistics", response_model=GrimoireStatsResponse)
async def get_grimoire_statistics():
    """
    📊 GRIMOIRE STATISTICS 📊

    Reveals comprehensive statistics about all spells in the grimoire.

    This endpoint provides deep insights into spell casting patterns:
    - **Total spells** recorded
    - **Spell type breakdown** (how many of each type)
    - **Daemon usage** (which daemons are most active)
    - **Success rate** (percentage of successful spells)
    - **Execution times** (total and average)
    - **Time range** (oldest and newest spells)
    - **File size** (grimoire storage usage)

    Perfect for:
    - Analyzing daemon performance
    - Identifying patterns in spell casting
    - Monitoring system health
    - Generating usage reports

    Returns:
        Comprehensive grimoire statistics
    """
    try:
        grimoire = get_grimoire()
        stats = grimoire.get_statistics()

        return GrimoireStatsResponse(
            status="success",
            message="✨ The grimoire's secrets are laid bare... ✨",
            statistics=stats
        )

    except Exception as e:
        logger.error(f"Failed to get grimoire statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"The grimoire guards its secrets: {str(e)}"
        )


@router.delete("/purge")
async def purge_old_spells_endpoint(
    days: int = Query(default=30, ge=1, le=365, description="Purge spells older than this many days")
) -> PurgeSpellsResponse:
    """
    🗑️ PURGE OLD SPELLS 🗑️

    Removes ancient spells from the grimoire to prevent infinite growth.

    This endpoint purges spells older than the specified number of days.
    Before deletion, old spells are archived to a backup file for safekeeping.

    **Safety Features:**
    - Spells are archived before deletion (no data loss)
    - Archive files are timestamped for easy recovery
    - Malformed entries are preserved to avoid corruption
    - Configurable retention period (1-365 days)

    **Default:** 30 days

    **Archive Location:** `grimoire_archive_<timestamp>.jsonl`

    Use this to:
    - Prevent grimoire from growing too large
    - Maintain performance
    - Archive historical data
    - Clean up old test entries

    Returns:
        Number of spells purged and archive file path
    """
    try:
        grimoire = get_grimoire()

        # Get archive file name before purging
        import time
        archive_file = f"grimoire_archive_{int(time.time())}.jsonl"

        purged_count = grimoire.purge_old_spells(days=days)

        return PurgeSpellsResponse(
            status="success",
            message=f"✨ Purged {purged_count} ancient spell(s) from the grimoire! ✨",
            purged_count=purged_count,
            archive_file=archive_file if purged_count > 0 else None
        )

    except Exception as e:
        logger.error(f"Failed to purge grimoire: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"The purging ritual has failed: {str(e)}"
        )


@router.post("/search", response_model=SearchSpellsResponse)
async def search_spells_endpoint(request: SearchSpellsRequest):
    """
    🔍 SEARCH SPELLS 🔍

    Searches the grimoire for spells containing specific text.

    This endpoint performs a text search across:
    - Spell names
    - Command parameters
    - Result data

    The search is case-insensitive and returns results in reverse
    chronological order (most recent first).

    **Search Tips:**
    - Use daemon names to find their spells: `claude`
    - Search for error messages: `failed` or `error`
    - Find specific operations: `write_haiku`
    - Look for parameters: `temperature`

    **Limit:** 1-100 results (default: 10)

    Returns:
        List of spell entries matching the search query
    """
    try:
        grimoire = get_grimoire()

        matches = grimoire.search_spells(
            query=request.query,
            limit=request.limit
        )

        spell_responses = [
            GrimoireEntryResponse(**spell)
            for spell in matches
        ]

        return SearchSpellsResponse(
            status="success",
            message=f"✨ Found {len(matches)} spell(s) matching '{request.query}'... ✨",
            query=request.query,
            spells=spell_responses,
            count=len(matches)
        )

    except Exception as e:
        logger.error(f"Failed to search grimoire: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"The search ritual has failed: {str(e)}"
        )


@router.get("/info")
async def grimoire_info():
    """
    ℹ️ GRIMOIRE INFORMATION ℹ️

    Provides basic information about the grimoire and its capabilities.

    Returns:
        Information about grimoire features and usage
    """
    return {
        "status": "active",
        "message": "✨ The Grimoire stands ready to record your spells! ✨",
        "description": "The Grimoire is ArcaneOS's persistent memory layer, recording all spells for eternal reference.",
        "features": [
            "Persistent spell history across sessions",
            "JSON Lines storage format",
            "Integrated with application logging",
            "Filtering by spell type and daemon",
            "Full-text search capabilities",
            "Automatic archiving of old spells",
            "Comprehensive statistics tracking"
        ],
        "storage": {
            "spell_file": "grimoire_spells.jsonl",
            "log_file": "arcane_log.txt",
            "format": "JSON Lines (one JSON object per line)"
        },
        "endpoints": {
            "POST /grimoire/record": "Record a new spell",
            "GET /grimoire/recall": "Retrieve recent spells",
            "GET /grimoire/statistics": "Get grimoire statistics",
            "DELETE /grimoire/purge": "Purge old spells",
            "POST /grimoire/search": "Search for spells",
            "GET /grimoire/info": "This endpoint"
        }
    }
