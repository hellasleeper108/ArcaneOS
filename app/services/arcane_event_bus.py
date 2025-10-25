"""Backwards-compatible shim importing ArcaneOS.core.event_bus."""

from ArcaneOS.core.event_bus import ArcaneEvent, ArcaneEventBus, SpellType, get_event_bus

__all__ = [
    "ArcaneEvent",
    "ArcaneEventBus",
    "SpellType",
    "get_event_bus",
]
