#!/usr/bin/env python3
"""
ArcaneOS WebSocket Client Example (Python)

This example demonstrates how to connect to the ArcaneOS WebSocket endpoint
and receive real-time events about daemon operations.

Usage:
    python examples/websocket_client.py

Requirements:
    pip install websockets asyncio
"""

import asyncio
import websockets
import json
from datetime import datetime


async def listen_to_arcane_events():
    """
    Connect to the ArcaneOS event stream and print events in real-time
    """
    uri = "ws://localhost:8000/ws/events"

    print("=" * 80)
    print("🔮 ArcaneOS WebSocket Client 🔮")
    print("=" * 80)
    print(f"Connecting to: {uri}")
    print()

    try:
        async with websockets.connect(uri) as websocket:
            print("✨ Connected to ArcaneOS event stream!")
            print("Listening for mystical events...\n")
            print("-" * 80)

            # Listen for events indefinitely
            async for message in websocket:
                try:
                    event = json.loads(message)

                    # Handle connection message
                    if event.get("type") == "connection":
                        print(f"📡 {event['message']}")
                        print(f"   Active subscribers: {event.get('subscriber_count', 0)}")

                        # Show recent events if available
                        recent = event.get("recent_events", [])
                        if recent:
                            print(f"   Recent events: {len(recent)}")
                        print("-" * 80)
                        continue

                    # Parse event timestamp
                    timestamp = event.get("timestamp", "")
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime("%H:%M:%S")
                    else:
                        time_str = datetime.now().strftime("%H:%M:%S")

                    # Get event details
                    spell_name = event.get("spell_name", "unknown")
                    daemon_name = event.get("daemon_name", "N/A")
                    success = event.get("success", False)
                    description = event.get("description", "")

                    # Format event display
                    status_icon = "✅" if success else "❌"

                    # Color-code by spell type
                    spell_icons = {
        "summon": "🔮",
        "invoke": "⚡",
        "banish": "🌙",
        "reveal": "📜",
        "parse": "📖",
        "voice": "🎙️"
    }
                    icon = spell_icons.get(spell_name, "✨")

                    print(f"[{time_str}] {icon} {spell_name.upper()} {status_icon}")
                    print(f"   Daemon: {daemon_name}")
                    print(f"   {description}")

                    # Show metadata if present
                    metadata = event.get("metadata", {})
                    if metadata:
                        # Filter interesting metadata
                        if "execution_time" in metadata:
                            print(f"   ⏱️  Execution time: {metadata['execution_time']:.3f}s")
                        if "task" in metadata:
                            task = metadata["task"]
                            task_preview = task[:50] + "..." if len(task) > 50 else task
                            print(f"   📋 Task: {task_preview}")
                        if "invocation_count" in metadata:
                            print(f"   🔢 Invocations: {metadata['invocation_count']}")
                        sync = metadata.get("sync")
                        if sync:
                            print(f"   🔄 Sync cues: {sync}")

                    print("-" * 80)

                except json.JSONDecodeError:
                    print(f"⚠️  Received non-JSON message: {message}")
                except Exception as e:
                    print(f"⚠️  Error processing event: {e}")

    except websockets.exceptions.ConnectionClosed:
        print("\n🔌 Connection closed by server")
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Disconnecting from ArcaneOS event stream...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def main():
    """
    Main entry point for the WebSocket client
    """
    try:
        asyncio.run(listen_to_arcane_events())
    except KeyboardInterrupt:
        print("\n✨ May the mystical forces guide your path! ✨")


if __name__ == "__main__":
    main()
