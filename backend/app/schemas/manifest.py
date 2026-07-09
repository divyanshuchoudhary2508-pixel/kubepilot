"""
Pydantic models shared across the validate/fix endpoints.

These are intentionally flat and small — this project has no database,
so schemas exist purely to give the API a typed, predictable contract.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Severity = Literal["high", "medium", "low"]


class ManifestRequest(BaseModel):
    """Body for POST /validate and POST /fix."""

    content: str = Field(..., min_length=1, description="Raw YAML content to process")


class Issue(BaseModel):
    """A single error or warning found in the manifest."""

    line: Optional[int] = Field(
        default=None, description="1-indexed line number, if it could be determined"
    )
    severity: Severity
    title: str
    message: str
    suggestion: Optional[str] = None
    document_index: Optional[int] = Field(
        default=None,
        description="0-indexed document position in a multi-document YAML stream. None for single-doc.",
    )


class ValidationResponse(BaseModel):
    """Body returned by POST /validate."""

    valid: bool
    errors: list[Issue] = Field(default_factory=list)
    warnings: list[Issue] = Field(default_factory=list)
    passed_checks: list[str] = Field(default_factory=list)
    score: int = Field(..., ge=0, le=100)
    document_count: int = Field(default=1, description="Number of YAML documents validated")


class FixResponse(BaseModel):
    """Body returned by POST /fix."""

    fixed_content: str
    applied_fixes: list[str] = Field(default_factory=list)
