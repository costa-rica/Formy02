"""
Admin routes (all require admin session):
  GET    /admin                        — admin dashboard (links + DB management)
  GET    /admin/questions              — questions management page
  POST   /admin/questions              — create a new question
  PUT    /admin/questions/{id}         — update a question
  DELETE /admin/questions/{id}         — delete a question
  GET    /admin/responses              — responses overview page
  GET    /admin/responses/{id}/detail  — JSON detail for modal
  POST   /admin/db/backup              — create a database backup dump
  POST   /admin/db/restore             — restore database from uploaded dump
  GET    /admin/db/backups/{filename}  — download a backup dump
  DELETE /admin/db/backups/{filename}  — delete a backup dump
  GET    /audio/{path:path}            — serve saved audio files
"""

from __future__ import annotations

import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from loguru import logger
from sqlmodel import Session, select

from src.app.models.database import get_session
from src.app.models.junction import SurveyedPersonQuestionResponse
from src.app.models.question import Question
from src.app.models.response import Response as QuestionResponse
from src.app.models.surveyed_person import SurveyedPerson
from src.app.utilities.auth import require_admin, require_admin_for_restore
from src.app.models.user import User
from src.app.utilities import db_backup
from src.app.utilities import config

router = APIRouter(prefix="/admin", tags=["admin"])


def _templates():
    from src.app.main import templates
    return templates


# ---------------------------------------------------------------------------
# GET /admin — dashboard
# ---------------------------------------------------------------------------
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_root(
    request: Request,
    current_user: User = Depends(require_admin),
):
    backups = db_backup.list_backups()
    return _templates().TemplateResponse(
        request,
        "admin/index.html",
        {"user": current_user, "backups": backups},
    )


# ---------------------------------------------------------------------------
# GET /admin/questions
# ---------------------------------------------------------------------------
@router.get("/questions", response_class=HTMLResponse)
async def questions_page(
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    questions = db.exec(select(Question).order_by(Question.id)).all()
    return _templates().TemplateResponse(
        request,
        "admin/questions.html",
        {"questions": questions, "user": current_user},
    )


# ---------------------------------------------------------------------------
# POST /admin/questions — create
# ---------------------------------------------------------------------------
@router.post("/questions")
async def create_question(
    request: Request,
    question_text: str = Form(..., alias="question"),
    q_type: str = Form(..., alias="type"),
    is_active: bool = Form(True),
    allows_for_audio: bool = Form(True),
    options: Optional[str] = Form(None),  # JSON string from form
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    parsed_options: Optional[List[str]] = None
    if q_type == "multiple_choice" and options:
        try:
            parsed_options = [o.strip() for o in options.split("\n") if o.strip()]
        except Exception:
            parsed_options = None

    q = Question(
        question=question_text.strip(),
        type=q_type,
        is_active=is_active,
        allows_for_audio=allows_for_audio,
    )
    q.options = parsed_options
    db.add(q)
    db.commit()
    db.refresh(q)
    logger.info(f"Question created: id={q.id} type={q.type}")
    return RedirectResponse(url="/admin/questions", status_code=303)


# ---------------------------------------------------------------------------
# PUT /admin/questions/{id} — update (called via fetch/AJAX)
# ---------------------------------------------------------------------------
@router.put("/questions/{question_id}")
async def update_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    body = await request.json()
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    if "question" in body:
        q.question = body["question"].strip()
    if "type" in body:
        q.type = body["type"]
    if "is_active" in body:
        q.is_active = bool(body["is_active"])
    if "allows_for_audio" in body:
        q.allows_for_audio = bool(body["allows_for_audio"])
    if "options" in body:
        raw = body["options"]
        if q.type == "multiple_choice" and raw:
            q.options = [o.strip() for o in raw if o.strip()]
        else:
            q.options = None

    q.updated_at = datetime.utcnow()
    db.add(q)
    db.commit()
    db.refresh(q)
    logger.info(f"Question updated: id={q.id}")
    return JSONResponse({"ok": True, "id": q.id})


# ---------------------------------------------------------------------------
# DELETE /admin/questions/{id}
# ---------------------------------------------------------------------------
@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    q = db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    db.delete(q)
    db.commit()
    logger.info(f"Question deleted: id={question_id}")
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# GET /admin/responses
# ---------------------------------------------------------------------------
@router.get("/responses", response_class=HTMLResponse)
async def responses_page(
    request: Request,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    # All surveyed people, ordered by most recently updated junction entry
    people = db.exec(select(SurveyedPerson).order_by(SurveyedPerson.id)).all()

    # Build summary: { surveyed_person_id: { count, updated_at } }
    summaries: dict = {}
    for person in people:
        links = db.exec(
            select(SurveyedPersonQuestionResponse)
            .where(SurveyedPersonQuestionResponse.surveyed_person_id == person.id)
        ).all()
        count = len(links)
        latest = max((lnk.updated_at for lnk in links), default=person.updated_at)
        summaries[person.id] = {"count": count, "updated_at": latest}

    return _templates().TemplateResponse(
        request,
        "admin/responses.html",
        {
            "people": people,
            "summaries": summaries,
            "user": current_user,
        },
    )


# ---------------------------------------------------------------------------
# GET /admin/responses/{person_id}/detail — JSON for modal
# ---------------------------------------------------------------------------
@router.get("/responses/{person_id}/detail")
async def response_detail(
    person_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    person = db.get(SurveyedPerson, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Surveyed person not found.")

    links = db.exec(
        select(SurveyedPersonQuestionResponse)
        .where(SurveyedPersonQuestionResponse.surveyed_person_id == person_id)
    ).all()

    items = []
    for link in links:
        q = db.get(Question, link.question_id)
        r = db.get(QuestionResponse, link.response_id)
        if q and r:
            items.append(
                {
                    "question_id": q.id,
                    "question": q.question,
                    "type": q.type,
                    "response": r.response,
                    "audio_path": r.audio_file_path_and_filename,
                    "updated_at": r.updated_at.isoformat(),
                }
            )

    latest = max((i["updated_at"] for i in items), default=person.updated_at.isoformat())

    return JSONResponse(
        {
            "person": {
                "id": person.id,
                "name": person.name,
                "email": person.email,
                "phone": person.phone,
            },
            "updated_at": latest,
            "responses": items,
        }
    )


# ---------------------------------------------------------------------------
# DELETE /admin/responses/{person_id} — delete person + responses
# ---------------------------------------------------------------------------
@router.delete("/responses/{person_id}")
async def delete_responses_for_person(
    person_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    person = db.get(SurveyedPerson, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Surveyed person not found.")

    links = db.exec(
        select(SurveyedPersonQuestionResponse)
        .where(SurveyedPersonQuestionResponse.surveyed_person_id == person_id)
    ).all()
    response_ids = [link.response_id for link in links]

    responses = []
    if response_ids:
        responses = db.exec(
            select(QuestionResponse).where(QuestionResponse.id.in_(response_ids))
        ).all()

    audio_base = Path(config.AUDIO_FILES_PATH or "").resolve() if config.AUDIO_FILES_PATH else None
    for response in responses:
        audio_path = response.audio_file_path_and_filename
        if not audio_path:
            continue
        path_obj = Path(audio_path)
        if path_obj.is_absolute():
            target = path_obj
        else:
            if not audio_base:
                continue
            target = (audio_base / path_obj).resolve()
            if not str(target).startswith(str(audio_base)):
                continue
        if target.exists() and target.is_file():
            target.unlink()

    for link in links:
        db.delete(link)
    for response in responses:
        db.delete(response)
    db.delete(person)
    db.commit()

    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# GET /audio/{path} — serve saved audio files (admin only)
# ---------------------------------------------------------------------------
@router.get("/audio/{file_path:path}")
async def serve_audio(
    file_path: str,
    current_user: User = Depends(require_admin),
):
    from src.app.utilities import config
    base = Path(config.AUDIO_FILES_PATH or "")
    # Resolve and ensure the file is inside the audio root (path traversal guard)
    target = (base / file_path).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise HTTPException(status_code=403, detail="Access denied.")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    media_type, _ = mimetypes.guess_type(str(target))
    if not media_type or not media_type.startswith("audio/"):
        media_type = "audio/webm"
    return FileResponse(str(target), media_type=media_type)


# ---------------------------------------------------------------------------
# POST /admin/db/backup — create backup
# ---------------------------------------------------------------------------
@router.post("/db/backup")
async def create_backup(
    current_user: User = Depends(require_admin),
):
    try:
        dump_path = db_backup.create_backup()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse({"ok": True, "filename": dump_path.name})


# ---------------------------------------------------------------------------
# POST /admin/db/restore — restore from uploaded dump
# ---------------------------------------------------------------------------
@router.post("/db/restore")
async def restore_backup(
    backup_file: UploadFile = File(...),
    current_user: User = Depends(require_admin_for_restore),
):
    if not backup_file.filename or not backup_file.filename.endswith(".dump"):
        raise HTTPException(status_code=400, detail="Upload must be a .dump backup file.")
    try:
        dump_bytes = await backup_file.read()
        db_backup.restore_backup(dump_bytes)
    except RuntimeError as exc:
        logger.error(f"Restore failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Restore failed: {exc}")
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# GET /admin/db/backups/{filename} — download backup
# ---------------------------------------------------------------------------
@router.get("/db/backups/{filename}")
async def download_backup(
    filename: str,
    current_user: User = Depends(require_admin),
):
    try:
        path = db_backup.get_backup_path(filename)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return FileResponse(
        str(path),
        media_type="application/octet-stream",
        filename=filename,
    )


# ---------------------------------------------------------------------------
# DELETE /admin/db/backups/{filename} — delete backup
# ---------------------------------------------------------------------------
@router.delete("/db/backups/{filename}")
async def delete_backup(
    filename: str,
    current_user: User = Depends(require_admin),
):
    try:
        path = db_backup.get_backup_path(filename)
        path.unlink()
        logger.info(f"Backup deleted: {filename}")
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return JSONResponse({"ok": True})
