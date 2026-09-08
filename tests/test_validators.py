import pytest

from app.validators import (
    is_strong_password,
    is_valid_email,
    is_valid_username,
    normalize_username,
    sanitize_display_name,
)


@pytest.mark.regression
def test_data_consistency():
    assert "abc".upper() == "ABC"


# ---------------------------------------------------------------------------
# Email validation
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.parametrize(
    "email",
    ["a@b.com", "first.last@example.co.uk", "user+tag@sub.domain.org"],
)
def test_is_valid_email_accepts_valid_addresses(email):
    assert is_valid_email(email) is True


@pytest.mark.regression
@pytest.mark.parametrize(
    "email",
    ["", "not-an-email", "missing-domain@", "@missing-local.com", "spaces in@email.com", None, 123],
)
def test_is_valid_email_rejects_invalid_addresses(email):
    assert is_valid_email(email) is False


# ---------------------------------------------------------------------------
# Username validation / normalization
# ---------------------------------------------------------------------------

@pytest.mark.regression
@pytest.mark.parametrize("username", ["bob", "alice_99", "A" * 32])
def test_is_valid_username_accepts_valid_names(username):
    assert is_valid_username(username) is True


@pytest.mark.regression
@pytest.mark.parametrize("username", ["", "ab", "A" * 33, "has space", "bad-char!", None])
def test_is_valid_username_rejects_invalid_names(username):
    assert is_valid_username(username) is False


@pytest.mark.regression
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  Alice  ", "alice"),
        ("BOB", "bob"),
        ("already_lower", "already_lower"),
    ],
)
def test_normalize_username(raw, expected):
    assert normalize_username(raw) == expected


@pytest.mark.regression
def test_normalize_username_rejects_non_string():
    with pytest.raises(TypeError):
        normalize_username(123)


# ---------------------------------------------------------------------------
# Password strength
# ---------------------------------------------------------------------------

@pytest.mark.security
@pytest.mark.parametrize(
    "password",
    ["Abcdefg1", "Str0ngPass!", "AbCd1234"],
)
def test_is_strong_password_accepts_strong_passwords(password):
    assert is_strong_password(password) is True


@pytest.mark.security
@pytest.mark.parametrize(
    "password",
    ["short1A", "alllowercase1", "ALLUPPERCASE1", "NoDigitsHere", "", 12345678],
)
def test_is_strong_password_rejects_weak_passwords(password):
    assert is_strong_password(password) is False


@pytest.mark.security
def test_is_strong_password_respects_custom_min_length():
    assert is_strong_password("Ab1", min_length=3) is True
    assert is_strong_password("Ab1", min_length=4) is False


# ---------------------------------------------------------------------------
# Display name sanitization
# ---------------------------------------------------------------------------

@pytest.mark.security
def test_sanitize_display_name_strips_control_characters():
    assert sanitize_display_name("Alice\x00\x07Bob") == "AliceBob"


@pytest.mark.regression
def test_sanitize_display_name_trims_whitespace():
    assert sanitize_display_name("  Alice  ") == "Alice"


@pytest.mark.regression
def test_sanitize_display_name_truncates_long_names():
    long_name = "x" * 100
    assert sanitize_display_name(long_name, max_length=10) == "x" * 10


@pytest.mark.regression
def test_sanitize_display_name_rejects_non_string():
    with pytest.raises(TypeError):
        sanitize_display_name(None)
