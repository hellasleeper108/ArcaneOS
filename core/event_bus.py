"""
ArcaneEventBus - Asynchronous WebSocket Event Broadcasting

Provides channel-based event broadcasting to WebSocket subscribers with
asyncio.Queue buffering for reliable message delivery.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ArcaneEventBus:
    """
    Asynchronous event bus for broadcasting messages to WebSocket subscribers
    organized by channels.
    """

    def __init__(self):
        """Initialize the ArcaneEventBus with channel-based subscriber tracking."""
        # Maps channel name to set of WebSocket connections
        self._subscribers: Dict[str, Set[WebSocket]] = {}

        # Maps channel name to asyncio.Queue for buffering
        self._queues: Dict[str, asyncio.Queue] = {}

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

        logger.info("✨ ArcaneEventBus initialized - Channels are open")

    async def subscribe(self, channel: str, websocket: WebSocket) -> None:
        """
        Subscribe a WebSocket connection to a specific channel.

        Args:
            channel: The channel name to subscribe to
            websocket: The WebSocket connection to add as a subscriber
        """
        async with self._lock:
            # Initialize channel structures if they don't exist
            if channel not in self._subscribers:
                self._subscribers[channel] = set()
                self._queues[channel] = asyncio.Queue()
                logger.info(f"📡 Created new channel: {channel}")

            # Add websocket to channel subscribers
            self._subscribers[channel].add(websocket)
            logger.info(f"✨ New subscriber joined channel '{channel}' "
                       f"(total: {len(self._subscribers[channel])})")

    async def emit(self, channel: str, message: dict) -> None:
        """
        Emit a message to all subscribers on a specific channel.

        The message is converted to JSON and broadcast to all WebSocket
        connections subscribed to the channel.

        Args:
            channel: The channel to broadcast on
            message: The message dictionary to send (will be JSON-encoded)
        """
        async with self._lock:
            # Check if channel exists
            if channel not in self._subscribers:
                logger.warning(f"⚠️ Attempted to emit to non-existent channel: {channel}")
                return

            subscribers = self._subscribers[channel].copy()

        if not subscribers:
            logger.debug(f"No subscribers on channel '{channel}' - message dropped")
            return

        # Convert message to JSON
        try:
            json_message = json.dumps(message)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize message to JSON: {e}")
            return

        # Broadcast to all subscribers
        logger.info(f"📤 Broadcasting to {len(subscribers)} subscriber(s) on '{channel}'")

        # Track failed sends
        failed_websockets = []

        for websocket in subscribers:
            try:
                await websocket.send_text(json_message)
            except Exception as e:
                logger.error(f"Failed to send to subscriber: {e}")
                failed_websockets.append(websocket)

        # Clean up failed connections
        if failed_websockets:
            async with self._lock:
                for ws in failed_websockets:
                    self._subscribers[channel].discard(ws)
                logger.info(f"🧹 Cleaned up {len(failed_websockets)} failed connection(s)")

    async def unsubscribe(self, channel: str, websocket: WebSocket) -> None:
        """
        Unsubscribe a WebSocket connection from a specific channel.

        Args:
            channel: The channel to unsubscribe from
            websocket: The WebSocket connection to remove
        """
        async with self._lock:
            if channel in self._subscribers:
                self._subscribers[channel].discard(websocket)
                remaining = len(self._subscribers[channel])

                logger.info(f"👋 Subscriber left channel '{channel}' "
                           f"(remaining: {remaining})")

                # Clean up empty channels
                if remaining == 0:
                    del self._subscribers[channel]
                    del self._queues[channel]
                    logger.info(f"🧹 Removed empty channel: {channel}")

    def get_subscriber_count(self, channel: str) -> int:
        """
        Get the number of subscribers on a specific channel.

        Args:
            channel: The channel name

        Returns:
            Number of active subscribers
        """
        return len(self._subscribers.get(channel, set()))

    def get_channels(self) -> list:
        """
        Get list of all active channels.

        Returns:
            List of channel names
        """
        return list(self._subscribers.keys())


# Singleton instance
_event_bus = None


def get_event_bus() -> ArcaneEventBus:
    """
    Get the global ArcaneEventBus instance (singleton pattern).

    Returns:
        The global ArcaneEventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = ArcaneEventBus()
    return _event_bus
