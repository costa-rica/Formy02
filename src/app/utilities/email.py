"""
Email utilities — send transactional emails via Gmail SMTP.
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.app.utilities import config


def send_verification_email(to_email: str, token: str) -> None:
    """
    Send an email verification link to the given address.
    The link points to {URL_BASE_WEBSITE}/verify?token={token}.
    """
    if not config.GMAIL_SMTP_USER or not config.GMAIL_SMTP_APP_PASSWORD:
        logger.error("Gmail SMTP credentials not configured — cannot send verification email.")
        return

    verify_url = f"{config.URL_BASE_WEBSITE}/verify?token={token}"

    subject = f"Verify your {config.NAME_APP} account"
    html_body = f"""
    <p>Hello,</p>
    <p>Thanks for registering with <strong>{config.NAME_APP}</strong>.</p>
    <p>Please verify your email address by clicking the link below.
       This link expires in 30 minutes.</p>
    <p><a href="{verify_url}">{verify_url}</a></p>
    <p>If you did not register, you can ignore this email.</p>
    """
    text_body = (
        f"Verify your {config.NAME_APP} account\n\n"
        f"Please click the link to verify your email (expires in 30 minutes):\n"
        f"{verify_url}\n\n"
        "If you did not register, ignore this email."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(config.GMAIL_SMTP_HOST, config.GMAIL_SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config.GMAIL_SMTP_USER, config.GMAIL_SMTP_APP_PASSWORD)
            smtp.sendmail(config.GMAIL_SMTP_USER, to_email, msg.as_string())
        logger.info(f"Verification email sent to {to_email}")
    except smtplib.SMTPException as exc:
        logger.error(f"Failed to send verification email to {to_email}: {exc}")
        raise


def send_password_reset_email(to_email: str, token: str) -> None:
    """
    Send a password reset link to the given address.
    The link points to {URL_BASE_WEBSITE}/reset-password/{token}.
    """
    if not config.GMAIL_SMTP_USER or not config.GMAIL_SMTP_APP_PASSWORD:
        logger.error("Gmail SMTP credentials not configured — cannot send password reset email.")
        return

    reset_url = f"{config.URL_BASE_WEBSITE}/reset-password/{token}"

    subject = f"Reset your {config.NAME_APP} password"

    # Load the HTML template from disk
    from pathlib import Path
    template_path = Path(__file__).parent.parent / "templates" / "email_reset_password.html"
    try:
        html_template = template_path.read_text(encoding="utf-8")
        html_body = (
            html_template
            .replace("{{ reset_url }}", reset_url)
            .replace("{{ app_name }}", config.NAME_APP or "Formy")
        )
    except FileNotFoundError:
        logger.warning("email_reset_password.html not found — falling back to plain HTML.")
        html_body = (
            f"<p>Hello,</p>"
            f"<p>A password reset was requested for your <strong>{config.NAME_APP}</strong> account.</p>"
            f"<p>Click the link below to set a new password. This link expires in 30 minutes.</p>"
            f"<p><a href=\"{reset_url}\">{reset_url}</a></p>"
            f"<p>If you did not request this, you can safely ignore this email.</p>"
        )

    text_body = (
        f"Reset your {config.NAME_APP} password\n\n"
        f"A password reset was requested for your account.\n"
        f"Click the link below to set a new password (expires in 30 minutes):\n"
        f"{reset_url}\n\n"
        "If you did not request this, ignore this email."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(config.GMAIL_SMTP_HOST, config.GMAIL_SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config.GMAIL_SMTP_USER, config.GMAIL_SMTP_APP_PASSWORD)
            smtp.sendmail(config.GMAIL_SMTP_USER, to_email, msg.as_string())
        logger.info(f"Password reset email sent to {to_email}")
    except smtplib.SMTPException as exc:
        logger.error(f"Failed to send password reset email to {to_email}: {exc}")
        raise
