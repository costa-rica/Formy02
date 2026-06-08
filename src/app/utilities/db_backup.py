"""
PostgreSQL backup and restore utilities.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from loguru import logger

from src.app.utilities import config


def _backups_dir() -> Path:
    if not config.PATH_PROJECT_RESOURCES:
        raise RuntimeError("PATH_PROJECT_RESOURCES is not configured.")
    backups_dir = Path(config.PATH_PROJECT_RESOURCES) / "backups_db"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def _postgres_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["PGPASSWORD"] = config.DB_PASSWORD
    if extra:
        env.update(extra)
    return env


def create_backup() -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dump_path = _backups_dir() / f"backup_{timestamp}.dump"
    cmd = [
        "pg_dump",
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        f"--file={dump_path}",
        f"--host={config.DB_HOST}",
        f"--port={config.DB_PORT}",
        f"--username={config.DB_USER}",
        config.DB_NAME,
    ]
    result = subprocess.run(cmd, env=_postgres_env(), capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"pg_dump failed: {result.stderr.strip()}")
        raise RuntimeError("pg_dump failed; backup did not complete")
    logger.info(f"Database backup created: {dump_path}")
    return dump_path


def list_backups() -> list[dict]:
    try:
        backups_dir = _backups_dir()
    except RuntimeError:
        return []

    backups = sorted(
        backups_dir.glob("backup_*.dump"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return [
        {
            "name": path.name,
            "size_kb": round(path.stat().st_size / 1024, 1),
            "modified": datetime.utcfromtimestamp(path.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        for path in backups
    ]


def get_backup_path(filename: str) -> Path:
    backups_dir = _backups_dir().resolve()
    target = (backups_dir / filename).resolve()
    try:
        target.relative_to(backups_dir)
    except ValueError as exc:
        raise ValueError("Invalid backup filename.") from exc
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"Backup not found: {filename}")
    return target


def restore_backup(dump_bytes: bytes) -> None:
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".dump", delete=False) as tmp:
            tmp.write(dump_bytes)
            tmp_path = tmp.name

        cmd = [
            "pg_restore",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            "--format=custom",
            f"--host={config.DB_HOST}",
            f"--port={config.DB_PORT}",
            f"--username={config.DB_USER}",
            f"--dbname={config.DB_NAME}",
            tmp_path,
        ]
        result = subprocess.run(
            cmd,
            env=_postgres_env({"PGOPTIONS": "-c lock_timeout=30s"}),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            logger.error(f"pg_restore failed: {result.stderr.strip()}")
            raise RuntimeError("pg_restore failed; restore did not complete")
        logger.info("Database restored from backup.")
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "pg_restore timed out after 300 seconds; restore did not complete"
        ) from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
