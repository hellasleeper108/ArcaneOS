"""Reality veil state management for ArcaneOS."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class VeilState:
    veil_enabled: bool = True

    @property
    def mode(self) -> Literal["fantasy", "developer"]:
        return "fantasy" if self.veil_enabled else "developer"


_state = VeilState()


def get_veil_state() -> VeilState:
    return _state


def set_veil(enabled: bool) -> VeilState:
    if _state.veil_enabled != enabled:
        previous = _state.mode
        _state.veil_enabled = enabled
        logger.info("Reality veil switched: %s -> %s", previous, _state.mode)
    return _state


def toggle_veil() -> VeilState:
    return set_veil(not _state.veil_enabled)


def is_fantasy_mode() -> bool:
    return _state.veil_enabled
