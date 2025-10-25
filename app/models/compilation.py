"""
Pydantic Models for VibeCompiler

These models define the request and response structures for code compilation
and execution endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum


class CodeLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"


class CompileRequest(BaseModel):
    """Request to compile and execute code"""

    code: str = Field(
        ...,
        description="The code to compile and execute",
        min_length=1,
        max_length=10000
    )

    language: CodeLanguage = Field(
        ...,
        description="The programming language of the code"
    )

    dry_run: bool = Field(
        default=False,
        description="If true, validate without executing (safe demo mode)"
    )

    timeout: Optional[int] = Field(
        default=None,
        description="Optional custom timeout in seconds",
        ge=1,
        le=60
    )

    emit_events: bool = Field(
        default=True,
        description="Whether to emit events to the ArcaneEventBus"
    )

    @validator('code')
    def code_not_empty(cls, v):
        """Ensure code is not just whitespace"""
        if not v.strip():
            raise ValueError('Code cannot be empty or whitespace only')
        return v

    class Config:
        schema_extra = {
            "example": {
                "code": "print('Hello from the mystical realm!')",
                "language": "python",
                "dry_run": False,
                "timeout": 10,
                "emit_events": True
            }
        }


class NarrationEventResponse(BaseModel):
    """A single narration event"""

    phase: str = Field(..., description="The compilation phase")
    message: str = Field(..., description="The narration message")
    timestamp: str = Field(..., description="ISO timestamp of the event")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")


class CompileResponse(BaseModel):
    """Response from code compilation and execution"""

    success: bool = Field(..., description="Whether execution succeeded")

    output: str = Field(..., description="Standard output from the code")

    error: Optional[str] = Field(None, description="Error message if execution failed")

    execution_time: float = Field(..., description="Total execution time in seconds")

    narration: List[NarrationEventResponse] = Field(
        ...,
        description="List of narration events during execution"
    )

    narration_text: str = Field(
        ...,
        description="Full narration as formatted text"
    )

    language: str = Field(..., description="The programming language used")

    dry_run: bool = Field(..., description="Whether this was a dry-run execution")

    message: str = Field(..., description="Fantasy-themed status message")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "output": "Hello from the mystical realm!\n",
                "error": None,
                "execution_time": 0.123,
                "narration": [
                    {
                        "phase": "initiation",
                        "message": "✨ The mystical compiler awakens from its slumber...",
                        "timestamp": "2025-10-24T12:34:56.789000",
                        "details": {"language": "python", "dry_run": False}
                    }
                ],
                "narration_text": "✨ [INITIATION] The mystical compiler awakens...\n...",
                "language": "python",
                "dry_run": False,
                "message": "✨ The spell manifests successfully! Your code breathes life into the digital realm!"
            }
        }


class LanguageInfo(BaseModel):
    """Information about a supported language"""

    language: str = Field(..., description="Language identifier")
    theme: str = Field(..., description="Thematic element for narration")
    timeout: int = Field(..., description="Default timeout in seconds")
    extension: str = Field(..., description="File extension")


class SupportedLanguagesResponse(BaseModel):
    """Response listing all supported languages"""

    status: str = Field(default="success")
    message: str = Field(..., description="Fantasy-themed message")
    languages: List[LanguageInfo] = Field(..., description="List of supported languages")
    count: int = Field(..., description="Number of supported languages")
