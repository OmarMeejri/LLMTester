"""Minimal authentication/authorization logic used by the sample app.

Password hashing here uses salted SHA-256 via hashlib.pbkdf2_hmac. It is
intentionally dependency-free (stdlib only) since this is a demo project;
a real system should use a purpose-built KDF library (e.g. argon2, bcrypt).
"""
from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass

ROLES = ("guest", "user", "admin")

PBKDF2_ITERATIONS = 100_000


class AuthError(Exception):
    """Base class for authentication/authorization failures."""


class InvalidCredentialsError(AuthError):
    pass


class UnknownRoleError(AuthError):
    pass


class PermissionDeniedError(AuthError):
    pass


@dataclass
class User:
    username: str
    password_hash: str
    role: str = "guest"

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise UnknownRoleError(f"Unknown role: {self.role!r}")


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Return a salted PBKDF2-HMAC-SHA256 hash, encoded as 'salt$hash' hex."""
    if not password:
        raise ValueError("password must not be empty")
    salt = salt if salt is not None else os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time comparison of a candidate password against a stored hash."""
    try:
        salt_hex, _ = password_hash.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    candidate = hash_password(password, salt=salt)
    return hmac.compare_digest(candidate, password_hash)


class UserStore:
    """In-memory user directory, keyed by username."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def register(self, username: str, password: str, role: str = "guest") -> User:
        if not username or not username.strip():
            raise ValueError("username must not be empty")
        if username in self._users:
            raise ValueError(f"user already exists: {username}")
        user = User(username=username, password_hash=hash_password(password), role=role)
        self._users[username] = user
        return user

    def get(self, username: str) -> User | None:
        return self._users.get(username)

    def authenticate(self, username: str, password: str) -> User:
        user = self._users.get(username)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("invalid username or password")
        return user


def requires_role(user: User, role: str) -> bool:
    """True if `user`'s role meets or exceeds the required `role` in ROLES order."""
    if role not in ROLES:
        raise UnknownRoleError(f"Unknown role: {role!r}")
    return ROLES.index(user.role) >= ROLES.index(role)


def authorize(user: User, role: str) -> None:
    """Raise PermissionDeniedError unless `user` satisfies `role`."""
    if not requires_role(user, role):
        raise PermissionDeniedError(f"user {user.username!r} lacks role {role!r}")
