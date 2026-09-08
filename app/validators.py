"""Input validation and normalization helpers."""
from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def is_valid_username(username: str) -> bool:
    if not isinstance(username, str):
        return False
    return bool(_USERNAME_RE.match(username))


def is_strong_password(password: str, min_length: int = 8) -> bool:
    """A password is 'strong' if it meets a minimum length and mixes
    uppercase, lowercase, and digit characters."""
    if not isinstance(password, str) or len(password) < min_length:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit


def normalize_username(username: str) -> str:
    """Trim whitespace and lowercase a username for consistent lookups."""
    if not isinstance(username, str):
        raise TypeError("username must be a string")
    return username.strip().lower()


def sanitize_display_name(name: str, max_length: int = 64) -> str:
    """Strip control characters and cap length for values shown back to users."""
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    cleaned = "".join(ch for ch in name if ch.isprintable()).strip()
    return cleaned[:max_length]
