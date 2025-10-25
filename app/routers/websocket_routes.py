"""
WebSocket Routes for ArcaneOS Event Streaming

This module provides WebSocket endpoints for real-time event streaming.
Clients can connect to receive live updates about daemon operations,
spell casting, and other mystical activities in the ArcaneOS realm.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.arcane_event_bus import get_event_bus
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    """
    🔮 WebSocket Endpoint for Real-time Arcane Events 🔮

    Connect to this endpoint to receive live updates about all mystical
    activities in the ArcaneOS realm. Events are broadcast in real-time
    as spells are cast, daemons are summoned, and tasks are completed.

    WebSocket URL: ws://localhost:8000/ws/events

    Event Format:
        {
            "spell_name": "summon|invoke|banish|reveal|parse|voice",
            "daemon_name": "claude|gemini|liquidmetal",
            "timestamp": "2025-10-24T12:34:56.789",
            "success": true,
            "description": "✨ Fantasy-themed event description ✨",
            "metadata": {
                "task": "...",
                "execution_time": 0.123,
                ...
            }
        }

    Usage:
        1. Connect via WebSocket
        2. Receive welcome message with recent events
        3. Listen for real-time events as they occur
        4. Handle disconnection gracefully
    """
    event_bus = get_event_bus()

    await websocket.accept()

    # Send welcome message
    await websocket.send_json({
        "type": "connection",
        "message": "✨ Welcome to the ArcaneOS event stream! The ethereal channels are now open. ✨",
        "subscriber_count": event_bus.get_subscriber_count(),
        "recent_events": event_bus.get_recent_events(5)
    })

    logger.info("✨ WebSocket client connected to /ws/events")

    # Subscribe to event bus
    queue = await event_bus.subscribe()

    try:
        while True:
            # Wait for next event
            event = await queue.get()

            # Send event to client
            await websocket.send_json(event.to_dict())

    except WebSocketDisconnect:
        logger.info("✨ WebSocket client disconnected from /ws/events")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Unsubscribe from event bus
        await event_bus.unsubscribe(queue)


@router.get("/events/recent")
async def get_recent_events(count: int = 10):
    """
    📜 Get Recent Events 📜

    Retrieve recent arcane events from the event history.
    Useful for checking what happened recently without maintaining
    a WebSocket connection.

    Args:
        count: Number of recent events to retrieve (default: 10, max: 100)

    Returns:
        List of recent event dictionaries
    """
    event_bus = get_event_bus()
    count = min(count, 100)  # Cap at 100 events

    return {
        "status": "success",
        "message": f"✨ The chronicles reveal the last {count} mystical occurrences... ✨",
        "count": count,
        "events": event_bus.get_recent_events(count)
    }


@router.get("/events/stats")
async def get_event_stats():
    """
    📊 Event Bus Statistics 📊

    Get statistics about the event bus, including the number of
    connected subscribers and recent activity.

    Returns:
        Dictionary with event bus statistics
    """
    event_bus = get_event_bus()

    return {
        "status": "success",
        "message": "✨ The ethereal network thrums with energy... ✨",
        "subscribers": event_bus.get_subscriber_count(),
        "history_size": len(event_bus.get_recent_events(1000)),
        "active": True
    }
