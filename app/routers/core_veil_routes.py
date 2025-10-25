"""
Reality Veil FastAPI Routes

Provides endpoints to toggle between fantasy and developer mode.
"""

from fastapi import APIRouter
from pydantic import BaseModel
import sys
import os

# Add core to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import core.veil as veil_module

router = APIRouter()


class VeilResponse(BaseModel):
    """Response model for veil status"""
    veil: bool
    mode: str


class VeilUpdateRequest(BaseModel):
    """Request model for updating veil state"""
    veil: bool


@router.get("/veil")
async def get_veil_status() -> VeilResponse:
    """
    Get the current veil status.

    Returns:
        VeilResponse: Current veil state and mode
    """
    return VeilResponse(
        veil=veil_module.get_veil(),
        mode=veil_module.get_mode()
    )


@router.post("/veil")
async def update_veil(request: VeilUpdateRequest) -> VeilResponse:
    """
    Update the veil state.

    Args:
        request: VeilUpdateRequest with veil boolean

    Returns:
        VeilResponse: Updated veil state and mode
    """
    new_veil = veil_module.set_veil(request.veil)
    return VeilResponse(
        veil=new_veil,
        mode=veil_module.get_mode()
    )


@router.post("/reveal")
async def reveal_reality() -> VeilResponse:
    """
    Switch to developer mode (veil down).

    Returns:
        VeilResponse: Updated veil state (veil=False, mode="developer")
    """
    veil_module.reveal()
    return VeilResponse(
        veil=veil_module.get_veil(),
        mode=veil_module.get_mode()
    )


@router.post("/veil/restore")
async def restore_veil() -> VeilResponse:
    """
    Restore fantasy mode (veil up).

    Returns:
        VeilResponse: Updated veil state (veil=True, mode="fantasy")
    """
    veil_module.restore()
    return VeilResponse(
        veil=veil_module.get_veil(),
        mode=veil_module.get_mode()
    )
