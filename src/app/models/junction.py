"""
ContractSurveyedPersonQuestionsResponses junction table —
links a SurveyedPerson to a Question and its Response.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SurveyedPersonQuestionResponse(SQLModel, table=True):
    __tablename__ = "contract_surveyed_person_questions_responses"

    id: Optional[int] = Field(default=None, primary_key=True)
    surveyed_person_id: int = Field(foreign_key="surveyed_person.id", index=True)
    question_id: int = Field(foreign_key="questions.id", index=True)
    response_id: int = Field(foreign_key="responses.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
