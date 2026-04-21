"""Minimal user model for the Module 11 demo."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String

from app.models.base import Base


class User(Base):
    """Simple ORM model students can later connect to auth and calculations."""

    __tablename__ = "demo_users"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
