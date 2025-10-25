from pydantic import BaseModel, Field


class TerminalSpellRequest(BaseModel):
    spell: str = Field(..., description="Raw spell text to route through the Archon")
