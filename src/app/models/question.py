"""
Questions table — survey questions managed by admins.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB


class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    is_active: bool = Field(default=True)
    # type: "yes/no", "text", "multiple_choice"
    type: str = Field(default="text")
    allows_for_audio: bool = Field(default=True)
    # None for non-multiple-choice questions.
    options: Optional[List[str]] = Field(default=None, sa_column=Column("options", JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
