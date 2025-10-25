"""Reality veil endpoints for toggling fantasy/developer mode."""

from fastapi import APIRouter, HTTPException

from app.models.veil import VeilStatusResponse, VeilUpdateRequest
from ArcaneOS.core.veil import get_veil_state, set_veil


router = APIRouter(
    prefix="/veil",
    tags=["Veil"],
    responses={
        200: {"description": "Current veil status"},
        400: {"description": "Invalid veil state"},
    },
)


@router.get("", response_model=VeilStatusResponse)
async def get_veil_status():
    state = get_veil_state()
    return VeilStatusResponse(veil=state.veil_enabled, mode=state.mode)


@router.post("", response_model=VeilStatusResponse)
async def update_veil(request: VeilUpdateRequest):
    state = set_veil(request.veil)
    if state.mode not in {"fantasy", "developer"}:
        raise HTTPException(status_code=400, detail="Invalid veil mode")
    return VeilStatusResponse(veil=state.veil_enabled, mode=state.mode)
