"""
Authentication utilities:
  - Password hashing / verification (bcrypt directly)
  - JWT creation / decoding for email verification and password reset (python-jose)
  - Signed session cookie helpers (itsdangerous)
  - FastAPI dependencies: get_current_user, require_admin
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Cookie, Depends, HTTPException, Request, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from jose import JWTError, jwt
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from src.app.models.database import get_engine, get_session
from src.app.models.user import User
from src.app.utilities import config

# ---------------------------------------------------------------------------
# Password hashing  (bcrypt directly — passlib 1.7 is incompatible with bcrypt 4+)
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT — email verification tokens only (30-min expiry)
# ---------------------------------------------------------------------------
_JWT_ALGORITHM = "HS256"
_JWT_EXPIRY_MINUTES = 30


def create_verification_token(user_id: int, email: str) -> str:
    """Create a short-lived JWT for email address verification."""
    expire = datetime.utcnow() + timedelta(minutes=_JWT_EXPIRY_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "type": "email_verify",
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=_JWT_ALGORITHM)


def decode_verification_token(token: str) -> dict:
    """
    Decode and validate a verification JWT.
    Raises HTTPException 400 on invalid/expired token.
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[_JWT_ALGORITHM])
        if payload.get("type") != "email_verify":
            raise HTTPException(status_code=400, detail="Invalid token type.")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid or expired token: {exc}")


def create_password_reset_token(user_id: int, email: str) -> str:
    """Create a short-lived JWT for password reset (30-min expiry)."""
    expire = datetime.utcnow() + timedelta(minutes=_JWT_EXPIRY_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "type": "password_reset",
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=_JWT_ALGORITHM)


def decode_password_reset_token(token: str) -> dict:
    """
    Decode and validate a password reset JWT.
    Raises HTTPException 400 on invalid/expired token.
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[_JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type.")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid or expired token: {exc}")


# ---------------------------------------------------------------------------
# Signed session cookies (itsdangerous)
# ---------------------------------------------------------------------------
_serializer = URLSafeTimedSerializer(config.SECRET_KEY)
_COOKIE_NAME = "session"
_COOKIE_MAX_AGE = 60 * 60 * 8  # 8 hours


def create_session_cookie_value(user_id: int) -> str:
    return _serializer.dumps({"user_id": user_id})


def decode_session_cookie(value: str) -> Optional[int]:
    """Return the user_id from a session cookie, or None if invalid/expired."""
    try:
        data = _serializer.loads(value, max_age=_COOKIE_MAX_AGE)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------
def _validate_admin_cookie(request: Request, db: Session) -> User:
    session_cookie = request.cookies.get(_COOKIE_NAME)
    if not session_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    user_id = decode_session_cookie(session_cookie)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid.",
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


def get_current_user(
    session_cookie: Optional[str] = Cookie(default=None, alias=_COOKIE_NAME),
    db: Session = Depends(get_session),
) -> User:
    """Dependency — return the logged-in User or raise 401."""
    if not session_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    user_id = decode_session_cookie(session_cookie)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid.",
        )
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency — require the current user to be an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


def require_admin_for_restore(
    request: Request,
    engine: Engine = Depends(get_engine),
) -> User:
    """Authenticate admin and close the ORM session before pg_restore runs."""
    with Session(engine) as session:
        return _validate_admin_cookie(request, session)
