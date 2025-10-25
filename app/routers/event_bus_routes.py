"""
WebSocket Routes for Core ArcaneEventBus

Provides channel-based WebSocket event broadcasting using the core event bus.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import sys
import os

# Add core to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.event_bus import get_event_bus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/events/{channel}")
async def websocket_channel_events(websocket: WebSocket, channel: str):
    """
    🔮 Channel-based WebSocket Event Endpoint 🔮

    Connect to this endpoint to receive real-time events on a specific channel.
    Messages are broadcast to all subscribers on the same channel.

    WebSocket URL: ws://localhost:8000/ws/events/{channel}

    Usage:
        1. Connect via WebSocket to a specific channel
        2. Receive welcome message
        3. Listen for events broadcast on that channel
        4. Automatically unsubscribed on disconnect

    Example channels:
        - route: Navigation and routing events
        - spell: Spell casting events
        - daemon: Daemon lifecycle events
    """
    event_bus = get_event_bus()

    await websocket.accept()

    # Subscribe to the channel
    await event_bus.subscribe(channel, websocket)

    # Send welcome message
    await websocket.send_json({
        "type": "connection",
        "message": f"✨ Connected to channel '{channel}' ✨",
        "channel": channel,
        "subscribers": event_bus.get_subscriber_count(channel)
    })

    logger.info(f"✨ WebSocket client connected to channel '{channel}'")

    try:
        # Keep connection alive and wait for messages
        while True:
            # Wait for client messages (ping/pong or other commands)
            try:
                data = await websocket.receive_text()
                # Echo back or handle commands if needed
                logger.debug(f"Received from client on '{channel}': {data}")
            except Exception:
                # If receive fails, connection is likely closed
                break

    except WebSocketDisconnect:
        logger.info(f"✨ WebSocket client disconnected from channel '{channel}'")
    except Exception as e:
        logger.error(f"WebSocket error on channel '{channel}': {e}")
    finally:
        # Unsubscribe from channel
        await event_bus.unsubscribe(channel, websocket)


@router.get("/channels")
async def get_channels():
    """
    📡 Get Active Channels 📡

    Retrieve list of all active channels and their subscriber counts.

    Returns:
        Dictionary with active channels and statistics
    """
    event_bus = get_event_bus()

    channels = event_bus.get_channels()
    channel_stats = {
        channel: event_bus.get_subscriber_count(channel)
        for channel in channels
    }

    return {
        "status": "success",
        "message": "✨ The ethereal channels pulse with energy... ✨",
        "channels": channel_stats,
        "total_channels": len(channels)
    }
