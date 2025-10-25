import asyncio

import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app
from ArcaneOS.core.event_bus import get_event_bus
from ArcaneOS.core.veil import set_veil


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_reveal_toggle(anyio_backend):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.post("/reveal")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["mode"] == "developer"

        resp = await client.get("/veil")
        assert resp.json()["mode"] == "developer"

        resp = await client.post("/reveal/restore")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["mode"] == "fantasy"


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_event_bus_route_sequence(anyio_backend):
    event_bus = get_event_bus()
    queue = await event_bus.subscribe()
    await event_bus.emit_route("claude", True, {"latency_ms": 123.4})
    event = await asyncio.wait_for(queue.get(), timeout=1)
    assert event.spell_name.value == "route"
    await event_bus.unsubscribe(queue)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_golden_fantasy_message(anyio_backend):
    set_veil(True)
    event_bus = get_event_bus()
    queue = await event_bus.subscribe()
    await event_bus.emit_summon("claude")
    event = await asyncio.wait_for(queue.get(), timeout=1)
    assert "✨" in event.description
    await event_bus.unsubscribe(queue)


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_archon_claude_code_proxy(anyio_backend):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "spec": {
                "title": "Test Design",
                "goal": "Ensure Claude proxy works.",
                "acceptance": ["proxy returns success"],
                "changes": [{"path": "src/test.ts", "action": "create"}],
            },
            "prompt": "Ship to Claude Code?",
        }
        resp = await client.post("/archon/claude-code", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["success"] is True
        assert data["result"]["parameters"]["spec"]["title"] == "Test Design"
