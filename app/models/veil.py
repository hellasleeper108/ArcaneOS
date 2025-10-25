from pydantic import BaseModel, Field


class VeilStatusResponse(BaseModel):
    veil: bool = Field(..., description="Whether the fantasy veil is active")
    mode: str = Field(..., description="Current response mode: fantasy or developer")


class VeilUpdateRequest(BaseModel):
    veil: bool = Field(..., description="Set to true for fantasy mode, false for developer mode")
