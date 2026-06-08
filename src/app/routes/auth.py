"""
Authentication routes:
  GET  /login                    — login page
  POST /login                    — authenticate and set session cookie
  GET  /register                 — registration page
  POST /register                 — create account and send verification email
  GET  /verify                   — verify email via JWT token
  POST /logout                   — clear session cookie
  GET  /forgot-password          — forgot password page
  POST /forgot-password          — send password reset email
  GET  /reset-password/{token}   — reset password form
  POST /reset-password/{token}   — update password
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from loguru import logger
from sqlmodel import Session, select

from src.app.models.database import get_session
from src.app.models.user import User
from src.app.utilities import config
from src.app.utilities.auth import (
    create_password_reset_token,
    create_session_cookie_value,
    create_verification_token,
    decode_password_reset_token,
    decode_verification_token,
    hash_password,
    verify_password,
)
from src.app.utilities.email import send_password_reset_email, send_verification_email
from src.app.utilities.error_handlers import error_response

router = APIRouter(tags=["auth"])

_COOKIE_NAME = "session"


def _templates():
    from src.app.main import templates
    return templates


# ---------------------------------------------------------------------------
# GET /login
# ---------------------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return _templates().TemplateResponse(request, "login.html")


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    user = db.exec(select(User).where(User.email == email.strip().lower())).first()

    if not user or not verify_password(password, user.password):
        return _templates().TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid email or password."},
            status_code=401,
        )

    if not user.email_verified:
        return _templates().TemplateResponse(
            request,
            "login.html",
            {"error": "Please verify your email before logging in."},
            status_code=403,
        )

    logger.info(f"User logged in: {user.email}")
    cookie_value = create_session_cookie_value(user.id)
    redirect = RedirectResponse(url="/admin/questions", status_code=303)
    redirect.set_cookie(
        key=_COOKIE_NAME,
        value=cookie_value,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return redirect


# ---------------------------------------------------------------------------
# GET /register
# ---------------------------------------------------------------------------
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return _templates().TemplateResponse(request, "register.html")


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------
@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    normalised_email = email.strip().lower()

    # Check whitelist
    if normalised_email not in config.ALLOWED_ADMIN_EMAILS:
        return _templates().TemplateResponse(
            request,
            "register.html",
            {"error": "This email is not authorised to register."},
            status_code=403,
        )

    # Duplicate check
    existing = db.exec(select(User).where(User.email == normalised_email)).first()
    if existing:
        return _templates().TemplateResponse(
            request,
            "register.html",
            {"error": "An account with this email already exists."},
            status_code=409,
        )

    # Create user
    user = User(
        username=username.strip(),
        email=normalised_email,
        password=hash_password(password),
        is_admin=True,  # all registered users are admins (whitelist-gated)
        email_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email
    token = create_verification_token(user.id, user.email)
    try:
        send_verification_email(user.email, token)
    except Exception as exc:
        logger.error(f"Could not send verification email: {exc}")

    logger.info(f"New user registered: {user.email}")
    return _templates().TemplateResponse(
        request,
        "register.html",
        {"success": "Registration successful! Check your email to verify your account."},
    )


# ---------------------------------------------------------------------------
# GET /verify
# ---------------------------------------------------------------------------
@router.get("/verify", response_class=HTMLResponse)
async def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_session),
):
    payload = decode_verification_token(token)  # raises 400 on invalid
    user_id = int(payload["sub"])

    user = db.get(User, user_id)
    if not user:
        return _templates().TemplateResponse(
            request,
            "login.html",
            {"error": "User not found."},
            status_code=404,
        )

    if not user.email_verified:
        user.email_verified = True
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        logger.info(f"Email verified for user: {user.email}")

    return _templates().TemplateResponse(
        request,
        "login.html",
        {"success": "Email verified! You can now log in."},
    )


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------
@router.post("/logout")
async def logout():
    redirect = RedirectResponse(url="/login", status_code=303)
    redirect.delete_cookie(key=_COOKIE_NAME)
    return redirect


# ---------------------------------------------------------------------------
# GET /forgot-password
# ---------------------------------------------------------------------------
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return _templates().TemplateResponse(request, "forgot_password.html")


# ---------------------------------------------------------------------------
# POST /forgot-password
# ---------------------------------------------------------------------------
@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_session),
):
    normalised_email = email.strip().lower()
    user = db.exec(select(User).where(User.email == normalised_email)).first()

    # Always show the same success message to prevent email enumeration
    success_msg = (
        "If an account with that email exists, a password reset link has been sent. "
        "Check your inbox — the link expires in 30 minutes."
    )

    if user:
        token = create_password_reset_token(user.id, user.email)
        try:
            send_password_reset_email(user.email, token)
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as exc:
            logger.error(f"Could not send password reset email to {user.email}: {exc}")

    return _templates().TemplateResponse(
        request,
        "forgot_password.html",
        {"success": success_msg},
    )


# ---------------------------------------------------------------------------
# GET /reset-password/{token}
# ---------------------------------------------------------------------------
@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    # Pre-validate so we can show an error before the form if token is bad
    try:
        decode_password_reset_token(token)
    except Exception:
        return _templates().TemplateResponse(
            request,
            "reset_password.html",
            {"token": token, "token_error": True},
        )
    return _templates().TemplateResponse(
        request,
        "reset_password.html",
        {"token": token},
    )


# ---------------------------------------------------------------------------
# POST /reset-password/{token}
# ---------------------------------------------------------------------------
@router.post("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    token: str,
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    try:
        payload = decode_password_reset_token(token)
    except Exception:
        return _templates().TemplateResponse(
            request,
            "reset_password.html",
            {"token": token, "token_error": True},
        )

    user_id = int(payload["sub"])
    user = db.get(User, user_id)
    if not user:
        return _templates().TemplateResponse(
            request,
            "reset_password.html",
            {"token": token, "error": "User not found."},
        )

    user.password = hash_password(password)
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    logger.info(f"Password reset completed for user: {user.email}")

    return _templates().TemplateResponse(
        request,
        "login.html",
        {"success": "Password updated successfully. You can now sign in."},
    )
