"""
Core modules for ArcaneOS

Contains foundational components including the VibeCompiler for safe
code execution, ArcaneEventBus for WebSocket event broadcasting, and
Reality Veil for fantasy/developer mode toggling.
"""

from .vibecompiler import VibeCompiler
from .event_bus import ArcaneEventBus, get_event_bus
from .veil import get_veil, set_veil, toggle_veil, reveal, restore, get_mode

__all__ = [
    'VibeCompiler',
    'ArcaneEventBus',
    'get_event_bus',
    'get_veil',
    'set_veil',
    'toggle_veil',
    'reveal',
    'restore',
    'get_mode'
]
