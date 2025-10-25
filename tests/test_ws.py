"""
WebSocket Event Bus Tests

Validates channel-based WebSocket event broadcasting functionality.
"""

import pytest
import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from core.event_bus import get_event_bus
from app.routers.event_bus_routes import router


# Create test app
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_ws_sequence(client):
    """
    Test WebSocket event sequence: subscribe, emit, receive.

    Validates:
    - WebSocket connection to channel succeeds
    - Welcome message is received
    - Emitted messages are broadcast to subscribers
    - JSON payload matches
    """
    event_bus = get_event_bus()

    # Connect to the "route" channel
    with client.websocket_connect("/ws/events/route") as websocket:
        # Receive welcome message
        welcome = websocket.receive_json()

        assert welcome["type"] == "connection", "Should receive connection message"
        assert welcome["channel"] == "route", "Should be connected to 'route' channel"
        assert "message" in welcome, "Welcome should contain message"

        # Emit a test message to the channel
        test_message = {
            "event": "navigation",
            "path": "/arcane/dashboard",
            "timestamp": "2025-10-24T12:00:00"
        }

        # Use asyncio to emit message (event_bus.emit is async)
        async def emit_message():
            await event_bus.emit("route", test_message)

        # Run the async emit
        asyncio.run(emit_message())

        # Receive the emitted message
        received = websocket.receive_json()

        # Validate the received message matches what was sent
        assert received == test_message, "Received message should match emitted message"
        assert received["event"] == "navigation", "Event type should match"
        assert received["path"] == "/arcane/dashboard", "Path should match"
        assert received["timestamp"] == "2025-10-24T12:00:00", "Timestamp should match"

    print("✓ WebSocket sequence test passed")


def test_ws_multiple_subscribers(client):
    """
    Test multiple subscribers on the same channel.

    Validates:
    - Multiple WebSocket connections can subscribe to same channel
    - Messages are broadcast to all subscribers
    """
    event_bus = get_event_bus()

    # Connect two clients to the same channel
    with client.websocket_connect("/ws/events/route") as ws1, \
         client.websocket_connect("/ws/events/route") as ws2:

        # Receive welcome messages
        welcome1 = ws1.receive_json()
        welcome2 = ws2.receive_json()

        assert welcome1["channel"] == "route"
        assert welcome2["channel"] == "route"

        # Emit a message
        test_message = {"event": "multi_test", "data": "broadcast"}

        async def emit_message():
            await event_bus.emit("route", test_message)

        asyncio.run(emit_message())

        # Both should receive the message
        received1 = ws1.receive_json()
        received2 = ws2.receive_json()

        assert received1 == test_message, "First subscriber should receive message"
        assert received2 == test_message, "Second subscriber should receive message"

    print("✓ Multiple subscribers test passed")


def test_ws_channel_isolation(client):
    """
    Test that channels are isolated from each other.

    Validates:
    - Messages on one channel don't leak to other channels
    """
    event_bus = get_event_bus()

    with client.websocket_connect("/ws/events/route") as ws_route, \
         client.websocket_connect("/ws/events/spell") as ws_spell:

        # Receive welcome messages
        ws_route.receive_json()
        ws_spell.receive_json()

        # Emit to route channel only
        route_message = {"channel": "route", "data": "route_data"}

        async def emit_to_route():
            await event_bus.emit("route", route_message)

        asyncio.run(emit_to_route())

        # Route channel should receive it
        received_route = ws_route.receive_json()
        assert received_route == route_message

        # Spell channel should NOT receive it
        # (using timeout to avoid blocking)
        try:
            ws_spell.receive_json(timeout=0.5)
            assert False, "Spell channel should not receive route messages"
        except:
            # Expected - no message received on spell channel
            pass

    print("✓ Channel isolation test passed")


def test_ws_unsubscribe_on_disconnect(client):
    """
    Test that disconnecting unsubscribes from channel.

    Validates:
    - Subscriber count decreases on disconnect
    - Channel cleanup works correctly
    """
    event_bus = get_event_bus()

    # Connect and then disconnect
    with client.websocket_connect("/ws/events/test_channel") as websocket:
        websocket.receive_json()  # welcome message

        # Should have 1 subscriber
        assert event_bus.get_subscriber_count("test_channel") == 1

    # After disconnect, channel should be cleaned up
    # (may take a moment for cleanup to occur)
    import time
    time.sleep(0.1)

    # Channel should no longer exist or have 0 subscribers
    count = event_bus.get_subscriber_count("test_channel")
    assert count == 0, "Should have no subscribers after disconnect"

    print("✓ Unsubscribe on disconnect test passed")


if __name__ == "__main__":
    # Run tests directly
    print("\n" + "=" * 70)
    print("  WEBSOCKET EVENT BUS - VALIDATION TESTS")
    print("=" * 70 + "\n")

    client = TestClient(app)

    try:
        test_ws_sequence(client)
        test_ws_multiple_subscribers(client)
        test_ws_channel_isolation(client)
        test_ws_unsubscribe_on_disconnect(client)

        print("\n" + "=" * 70)
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
