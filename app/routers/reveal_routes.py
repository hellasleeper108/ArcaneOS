"""Endpoints for revealing or restoring the veil in developer mode."""

from fastapi import APIRouter

from ArcaneOS.core.schemas import VeilStatusResponse
from ArcaneOS.core.veil import set_veil
from app.services.arcane_event_bus import get_event_bus

router = APIRouter(tags=["Veil Reveal"])


@router.post("/reveal", response_model=VeilStatusResponse)
async def reveal_developer_mode():
    state = set_veil(False)
    event_bus = get_event_bus()
    await event_bus.emit_reveal(
        daemon_name=None,
        is_active=False,
        description="Developer reality unveiled.",
        metadata={"from": "fantasy", "to": "developer"},
    )
    return VeilStatusResponse(veil=state.veil_enabled, mode=state.mode)


@router.post("/reveal/restore", response_model=VeilStatusResponse)
async def restore_fantasy_mode():
    state = set_veil(True)
    event_bus = get_event_bus()
    await event_bus.emit_reveal(
        daemon_name=None,
        is_active=False,
        description="Fantasy veil restored.",
        metadata={"from": "dev", "to": "fantasy"},
    )
    return VeilStatusResponse(veil=state.veil_enabled, mode=state.mode)
