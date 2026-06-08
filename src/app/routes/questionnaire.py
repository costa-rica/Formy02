"""
Questionnaire routes (public — no authentication required):
  GET  /          — display the questionnaire form
  POST /submit    — process form submission
  GET  /thank-you — confirmation page
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from loguru import logger
from sqlmodel import Session, select

from src.app.models.database import get_session
from src.app.models.junction import SurveyedPersonQuestionResponse
from src.app.models.question import Question
from src.app.models.response import Response as QuestionResponse
from src.app.models.surveyed_person import SurveyedPerson
from src.app.utilities.audio import save_audio_file

router = APIRouter(tags=["questionnaire"])


def _templates():
    from src.app.main import templates
    return templates


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
async def questionnaire_page(
    request: Request,
    db: Session = Depends(get_session),
):
    questions = db.exec(
        select(Question)
        .where(Question.is_active == True)  # noqa: E712
        .order_by(Question.id)
    ).all()
    return _templates().TemplateResponse(
        request,
        "questionnaire.html",
        {"questions": questions},
    )


# ---------------------------------------------------------------------------
# POST /submit
# ---------------------------------------------------------------------------
@router.post("/submit")
async def submit_questionnaire(
    request: Request,
    db: Session = Depends(get_session),
):
    form = await request.form()

    # ── SurveyedPerson ──────────────────────────────────────────────────────
    name = (form.get("name") or "").strip() or None
    email = (form.get("email") or "").strip() or None
    phone = (form.get("phone") or "").strip() or None

    person = SurveyedPerson(name=name, email=email, phone=phone)
    db.add(person)
    db.commit()
    db.refresh(person)
    logger.info(f"New SurveyedPerson created: id={person.id}")

    # ── Fetch active questions ──────────────────────────────────────────────
    questions = db.exec(
        select(Question)
        .where(Question.is_active == True)  # noqa: E712
        .order_by(Question.id)
    ).all()

    # ── Process each question ───────────────────────────────────────────────
    for q in questions:
        field_name = f"question_{q.id}"
        audio_field = f"audio_{q.id}"

        raw_response = form.get(field_name)
        audio_upload: Optional[UploadFile] = form.get(audio_field)  # type: ignore

        # Normalise text response — skip if blank/whitespace only
        text_response: Optional[str] = None
        if raw_response and str(raw_response).strip():
            text_response = str(raw_response).strip()

        # Check audio upload (UploadFile with actual content)
        has_audio = (
            audio_upload is not None
            and hasattr(audio_upload, "filename")
            and audio_upload.filename
        )

        # Skip if no text and no audio
        if not text_response and not has_audio:
            continue

        # Save audio if present
        audio_path: Optional[str] = None
        if has_audio:
            try:
                audio_path = await save_audio_file(audio_upload, person.id, q.id)
            except Exception as exc:
                logger.error(f"Could not save audio for question {q.id}: {exc}")

        # Create Response record
        resp = QuestionResponse(
            response=text_response,
            audio_file_path_and_filename=audio_path,
        )
        db.add(resp)
        db.commit()
        db.refresh(resp)

        # Create junction record
        link = SurveyedPersonQuestionResponse(
            surveyed_person_id=person.id,
            question_id=q.id,
            response_id=resp.id,
        )
        db.add(link)
        db.commit()

    logger.info(f"Questionnaire submitted for SurveyedPerson id={person.id}")
    return RedirectResponse(url="/thank-you", status_code=303)


# ---------------------------------------------------------------------------
# GET /thank-you
# ---------------------------------------------------------------------------
@router.get("/thank-you", response_class=HTMLResponse)
async def thank_you(request: Request):
    return _templates().TemplateResponse(request, "thank_you.html")
