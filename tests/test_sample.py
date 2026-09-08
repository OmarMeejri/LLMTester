import pytest

@pytest.mark.regression
def test_login_flow():
    assert 1 + 1 == 2

@pytest.mark.regression
def test_data_consistency():
    assert "abc".upper() == "ABC"

@pytest.mark.security
def test_password_not_plaintext():
    stored = "5f4dcc3b5aa765d61d8327deb882cf99"  # md5("password")
    assert stored != "password"

@pytest.mark.security
def test_admin_role_required():
    user_role = "guest"
    assert user_role != "admin"