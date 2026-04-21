"""Minimal Pydantic schemas for the demo user routes."""

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Incoming request data for a demo user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=255)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    """Response data returned by the demo user routes."""

    id: str
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    persisted: bool = False
