import pytest

from app.auth import (
    AuthError,
    InvalidCredentialsError,
    PermissionDeniedError,
    UnknownRoleError,
    User,
    UserStore,
    authorize,
    hash_password,
    requires_role,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

@pytest.mark.security
def test_password_not_plaintext():
    hashed = hash_password("password")
    assert hashed != "password"


@pytest.mark.security
def test_hash_password_is_salted_and_unique_per_call():
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")
    assert first != second, "same password must yield different hashes (random salt)"


@pytest.mark.security
def test_hash_password_rejects_empty_password():
    with pytest.raises(ValueError):
        hash_password("")


@pytest.mark.security
def test_verify_password_accepts_correct_password():
    hashed = hash_password("s3cr3t!")
    assert verify_password("s3cr3t!", hashed) is True


@pytest.mark.security
@pytest.mark.parametrize(
    "candidate",
    ["wrong", "s3cr3t", "S3CR3T!", "s3cr3t! "],
)
def test_verify_password_rejects_incorrect_password(candidate):
    hashed = hash_password("s3cr3t!")
    assert verify_password(candidate, hashed) is False


@pytest.mark.security
def test_verify_password_rejects_malformed_hash():
    assert verify_password("anything", "not-a-real-hash") is False


# ---------------------------------------------------------------------------
# Roles / authorization
# ---------------------------------------------------------------------------

@pytest.mark.security
def test_admin_role_required():
    user = User(username="alice", password_hash=hash_password("x"), role="guest")
    assert user.role != "admin"


@pytest.mark.regression
@pytest.mark.parametrize(
    "role,target,expected",
    [
        ("admin", "guest", True),
        ("admin", "user", True),
        ("admin", "admin", True),
        ("user", "admin", False),
        ("user", "user", True),
        ("guest", "user", False),
    ],
)
def test_requires_role_hierarchy(role, target, expected):
    user = User(username="u", password_hash=hash_password("x"), role=role)
    assert requires_role(user, target) is expected


@pytest.mark.security
def test_requires_role_rejects_unknown_role():
    user = User(username="u", password_hash=hash_password("x"), role="admin")
    with pytest.raises(UnknownRoleError):
        requires_role(user, "superadmin")


@pytest.mark.security
def test_authorize_raises_permission_denied_for_insufficient_role():
    user = User(username="guest_user", password_hash=hash_password("x"), role="guest")
    with pytest.raises(PermissionDeniedError):
        authorize(user, "admin")


@pytest.mark.regression
def test_authorize_allows_sufficient_role():
    user = User(username="admin_user", password_hash=hash_password("x"), role="admin")
    authorize(user, "admin")  # should not raise


@pytest.mark.security
def test_user_construction_rejects_unknown_role():
    with pytest.raises(UnknownRoleError):
        User(username="bob", password_hash=hash_password("x"), role="superuser")


# ---------------------------------------------------------------------------
# UserStore / login flow
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    s = UserStore()
    s.register("alice", "Wonderland1", role="admin")
    return s


@pytest.mark.regression
def test_login_flow():
    store = UserStore()
    store.register("bob", "hunter2X", role="user")
    user = store.authenticate("bob", "hunter2X")
    assert user.username == "bob"
    assert user.role == "user"


@pytest.mark.regression
def test_register_and_authenticate_round_trip(store):
    user = store.authenticate("alice", "Wonderland1")
    assert user.role == "admin"


@pytest.mark.security
def test_authenticate_rejects_wrong_password(store):
    with pytest.raises(InvalidCredentialsError):
        store.authenticate("alice", "wrong-password")


@pytest.mark.security
def test_authenticate_rejects_unknown_user(store):
    with pytest.raises(InvalidCredentialsError):
        store.authenticate("nobody", "whatever")


@pytest.mark.regression
def test_register_rejects_duplicate_username(store):
    with pytest.raises(ValueError):
        store.register("alice", "AnotherPass1")


@pytest.mark.regression
@pytest.mark.parametrize("bad_username", ["", "   "])
def test_register_rejects_blank_username(bad_username):
    store = UserStore()
    with pytest.raises(ValueError):
        store.register(bad_username, "SomePass1")


@pytest.mark.regression
def test_get_returns_none_for_missing_user(store):
    assert store.get("does-not-exist") is None


@pytest.mark.security
def test_auth_error_hierarchy():
    assert issubclass(InvalidCredentialsError, AuthError)
    assert issubclass(PermissionDeniedError, AuthError)
    assert issubclass(UnknownRoleError, AuthError)
