"""
Spell Endpoints for ArcaneOS

These mystical routes allow mortals to interact with daemon entities
through the ancient arts of summoning, invocation, and banishment.
"""

from fastapi import APIRouter, HTTPException
from app.models.daemon import (
    SummonRequest,
    InvokeRequest,
    BanishRequest,
    DaemonResponse,
    DaemonType
)
from app.services.daemon_registry import daemon_registry
from app.services.arcane_event_bus import get_event_bus
import asyncio

# Create the spell router with fantasy-themed tags
router = APIRouter(
    prefix="",
    tags=["Spells"],
    responses={404: {"description": "The requested entity dwells not in this realm"}}
)


@router.post("/summon", response_model=DaemonResponse)
async def summon_daemon(request: SummonRequest):
    """
    🔮 SUMMON SPELL 🔮

    Draws a daemon from the ethereal void into the material realm.
    Once summoned, the daemon may be invoked to perform mystical tasks.

    The summoning ritual requires:
    - The daemon's true name (claude, gemini, or liquidmetal)
    - Sufficient ethereal energy in the realm

    Returns:
        A mystical response confirming the daemon's arrival
    """
    try:
        daemon = daemon_registry.summon(request.daemon_name)

        # Craft a fantasy-themed response based on the daemon type
        fantasy_messages = {
            DaemonType.CLAUDE: (
                "Through swirling mists of purple aether, "
                f"the daemon {daemon.name.value.upper()} materializes! "
                f"The {daemon.role} awakens from eternal slumber, "
                "its presence radiating waves of analytical power."
            ),
            DaemonType.GEMINI: (
                "Flames of golden amber dance and coalesce! "
                f"The daemon {daemon.name.value.upper()} emerges from the creative forge, "
                f"bringing forth the gifts of the {daemon.role}. "
                "Innovation crackles in the air!"
            ),
            DaemonType.LIQUIDMETAL: (
                "Ripples of cyan energy cascade through reality's fabric! "
                f"The daemon {daemon.name.value.upper()} flows into existence, "
                f"the {daemon.role} assuming corporeal form. "
                "Transformation energy permeates the realm!"
            )
        }

        return DaemonResponse(
            status="summoned",
            daemon=daemon,
            message=f"✨ {fantasy_messages[request.daemon_name]} ✨"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"The summoning ritual has failed! Dark forces intervene: {str(e)}"
        )


@router.post("/invoke", response_model=DaemonResponse)
async def invoke_daemon(request: InvokeRequest):
    """
    ⚡ INVOKE SPELL ⚡

    Commands a summoned daemon to channel its power and perform a task.
    The daemon applies its unique abilities through the Raindrop MCP interface.

    The invocation ritual requires:
    - The daemon's true name
    - A clear description of the task
    - The daemon must already be summoned

    Returns:
        A mystical response with MCP invocation results
    """
    try:
        # Invoke through enhanced registry with MCP routing
        result = daemon_registry.invoke_daemon(
            name=request.daemon_name,
            task=request.task,
            parameters=request.parameters
        )

        daemon = result["daemon"]
        mcp_result = result["result"]
        execution_time = result["execution_time"]

        # Craft invocation messages based on daemon type and task
        invocation_messages = {
            DaemonType.CLAUDE: (
                f"The {daemon.role} focuses its purple aura through MCP! "
                f"Task: '{request.task}' - analyzed with vast reasoning power. "
                f"Invocation #{daemon.invocation_count} completed in {execution_time:.3f}s. "
                f"Result: {mcp_result.get('output', 'Processing complete')}"
            ),
            DaemonType.GEMINI: (
                f"Flames of creativity surge through the MCP channel! "
                f"Task: '{request.task}' - golden light weaves innovative solutions. "
                f"Invocation #{daemon.invocation_count} processed in {execution_time:.3f}s. "
                f"Result: {mcp_result.get('output', 'Innovation manifest')}"
            ),
            DaemonType.LIQUIDMETAL: (
                f"Liquid cyan energy flows through MCP pathways! "
                f"The {daemon.role} adapts: '{request.task}'. "
                f"Transformation #{daemon.invocation_count} in {execution_time:.3f}s. "
                f"Result: {mcp_result.get('output', 'Transformation complete')}"
            )
        }

        return DaemonResponse(
            status="invoked",
            daemon=daemon,
            message=f"✨ {invocation_messages[request.daemon_name]} ✨"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"The invocation has gone awry! Mystical interference detected: {str(e)}"
        )


@router.post("/banish", response_model=DaemonResponse)
async def banish_daemon(request: BanishRequest):
    """
    🌙 BANISH SPELL 🌙

    Returns a daemon to the ethereal void, severing its MCP connection.
    Provides comprehensive statistics about the daemon's service.

    The banishment ritual requires:
    - The daemon's true name
    - The daemon must currently be summoned

    Returns:
        A mystical response with banishment statistics
    """
    try:
        # Banish through enhanced registry with MCP cleanup
        result = daemon_registry.banish_daemon(request.daemon_name)

        daemon = result["daemon"]
        stats = result["statistics"]

        # Craft banishment messages for each daemon type
        banishment_messages = {
            DaemonType.CLAUDE: (
                "Purple aether swirls and dissipates... "
                f"The daemon {daemon.name.value.upper()}, {daemon.role}, "
                f"bows gracefully after {stats['total_invocations']} faithful service(s). "
                f"Total service time: {stats['total_execution_time']}s. "
                "MCP connection severed. It fades back into the void."
            ),
            DaemonType.GEMINI: (
                "The creative flames dim and extinguish... "
                f"The daemon {daemon.name.value.upper()}, {daemon.role}, "
                f"departs after weaving {stats['total_invocations']} innovation(s). "
                f"Average execution: {stats['average_execution_time']}s. "
                "Golden light recedes into distant realms."
            ),
            DaemonType.LIQUIDMETAL: (
                "Cyan ripples slow and still... "
                f"The daemon {daemon.name.value.upper()}, {daemon.role}, "
                f"dissolves after {stats['total_invocations']} transformation(s). "
                f"Service duration: {stats['total_execution_time']}s. "
                "The flow returns to the eternal waters."
            )
        }

        return DaemonResponse(
            status="banished",
            daemon=daemon,
            message=f"✨ {banishment_messages[request.daemon_name]} ✨"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"The banishment has faltered! Mystical bonds resist: {str(e)}"
        )


@router.get("/daemons")
async def list_daemons():
    """
    📜 LIST DAEMONS 📜

    Reveals all daemons known to this realm and their current status.
    Use this to see which daemons are available for summoning.

    Returns:
        A grimoire of all daemon entities
    """
    all_daemons = daemon_registry.get_all_daemons()

    # Emit reveal event (async, run in background)
    event_bus = get_event_bus()
    asyncio.create_task(event_bus.emit_reveal(
        daemon_name=None,  # Query for all daemons
        is_active=False,
        metadata={"daemon_count": len(all_daemons), "query_type": "all"}
    ))

    return {
        "status": "revealed",
        "message": "✨ The ancient grimoire creaks open, its pages whispering the names of all known daemon entities... ✨",
        "daemons": all_daemons,
        "count": len(all_daemons)
    }


@router.get("/daemons/active")
async def list_active_daemons():
    """
    ⚡ ACTIVE DAEMONS ⚡

    Reveals only the daemons currently walking in the material realm.
    Shows which daemons are summoned and ready for invocation.

    Returns:
        A list of currently active daemon entities
    """
    active_daemons = daemon_registry.get_active_daemons()

    # Emit reveal event (async, run in background)
    event_bus = get_event_bus()
    asyncio.create_task(event_bus.emit_reveal(
        daemon_name=None,  # Query for active daemons
        is_active=True,
        metadata={"active_count": len(active_daemons), "query_type": "active"}
    ))

    return {
        "status": "scrying_complete",
        "message": f"✨ A scrying pool reveals {len(active_daemons)} daemonic essences currently manifest in this realm. ✨",
        "active_daemons": active_daemons,
        "count": len(active_daemons)
    }


@router.get("/statistics")
async def get_statistics():
    """
    📊 REGISTRY STATISTICS 📊

    Reveals comprehensive statistics about the entire daemon registry,
    including invocation history, execution times, and MCP registration status.

    Returns:
        Detailed statistics about all daemons and their activities
    """
    stats = daemon_registry.get_registry_statistics()

    # Emit reveal event (async, run in background)
    event_bus = get_event_bus()
    asyncio.create_task(event_bus.emit_reveal(
        daemon_name=None,  # Query for statistics
        is_active=False,
        metadata={
            "query_type": "statistics",
            "total_invocations": stats["total_invocations"],
            "active_daemons": stats["active_daemons"]
        }
    ))

    return {
        "status": "divination_complete",
        "message": "✨ The cosmic currents shift, revealing the following insights from the mystical archives... ✨",
        "statistics": stats
    }


@router.get("/daemon/{daemon_name}/state")
async def get_daemon_state(daemon_name: DaemonType):
    """
    🔍 DAEMON STATE 🔍

    Reveals detailed state information about a specific daemon,
    including invocation history and statistics.

    Args:
        daemon_name: The daemon to inspect

    Returns:
        Comprehensive state information for the requested daemon
    """
    state = daemon_registry.get_daemon_state(daemon_name)

    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"The daemon '{daemon_name}' is unknown to this realm"
        )

    stats = state.get_statistics()

    # Emit reveal event (async, run in background)
    event_bus = get_event_bus()
    asyncio.create_task(event_bus.emit_reveal(
        daemon_name=daemon_name.value,
        is_active=state.daemon.is_summoned,
        metadata={
            "query_type": "state",
            "is_active": stats["is_active"],
            "total_invocations": stats["total_invocations"]
        }
    ))

    return {
        "status": "inspection_complete",
        "message": f"✨ The very essence of {daemon_name.value} is laid bare for your inspection... ✨",
        "daemon_state": {
            "daemon": state.daemon,
            "statistics": stats,
            "invocation_history": state.invocation_history[-10:]  # Last 10 invocations
        }
    }
