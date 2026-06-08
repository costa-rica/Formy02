"""
Audio file utilities — save uploaded audio recordings to the server.

Naming convention:
  {AUDIO_FILES_PATH}/YYYYMMDD/SurveyedPerson_{id:04d}_Question_{qid:03d}_YYYYMMDD_HHMMSS.<ext>

Returns the full path + filename string stored in the Responses table.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile
from loguru import logger

from src.app.utilities import config

_KNOWN_AUDIO_EXTENSIONS = {".webm", ".ogg", ".mp4", ".m4a", ".mp3", ".wav", ".aac"}
_CONTENT_TYPE_EXTENSIONS = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".m4a",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/aac": ".aac",
}


def _audio_extension(upload: UploadFile) -> str:
    if upload.filename:
        suffix = Path(upload.filename).suffix.lower()
        if suffix in _KNOWN_AUDIO_EXTENSIONS:
            return suffix
    if upload.content_type:
        mapped = _CONTENT_TYPE_EXTENSIONS.get(upload.content_type.lower())
        if mapped:
            return mapped
    return ".webm"


async def save_audio_file(
    upload: UploadFile,
    surveyed_person_id: int,
    question_id: int,
) -> str:
    """
    Save an uploaded audio file using the standard naming convention.
    Returns the full path (str) to the saved file.
    Raises RuntimeError if AUDIO_FILES_PATH is not configured.
    """
    if not config.AUDIO_FILES_PATH:
        raise RuntimeError("AUDIO_FILES_PATH is not configured.")

    now = datetime.utcnow()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")

    # Daily subdirectory
    day_dir = Path(config.AUDIO_FILES_PATH) / date_str
    day_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"SurveyedPerson_{surveyed_person_id:04d}"
        f"_Question_{question_id:03d}"
        f"_{date_str}_{time_str}{_audio_extension(upload)}"
    )
    dest = day_dir / filename

    # Write upload to disk
    with dest.open("wb") as f:
        content = await upload.read()
        f.write(content)

    full_path = str(dest)
    logger.info(f"Audio saved: {full_path}")
    return full_path
