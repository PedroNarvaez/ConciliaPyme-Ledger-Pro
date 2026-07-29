import os
import pytest
from datetime import datetime, timedelta
from src.database import init_db, get_db_connection
from src.auth import (
    validate_strong_password,
    register_user,
    edit_user_role_and_status,
    change_user_password,
    authenticate_user,
    reset_admin_password,
    get_all_users
)

TEST_DB_FILE = "test_auth.db"

@pytest.fixture
def auth_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    init_db(TEST_DB_FILE)
    yield TEST_DB_FILE
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_password_policy():
    # Invalid: less than 10
    assert not validate_strong_password("Ab1!")
    # Invalid: no uppercase
    assert not validate_strong_password("abcde12345!")
    # Invalid: no lowercase
    assert not validate_strong_password("ABCDE12345!")
    # Invalid: no number
    assert not validate_strong_password("ABCDEfghij!")
    # Invalid: no symbol
    assert not validate_strong_password("ABCDEfghij1234")
    # Valid
    assert validate_strong_password("Admin@2026!")

def test_user_registration_and_auth(auth_db):
    # Try invalid password
    success, msg = register_user("juan", "weak123", "contador", db_path=auth_db)
    assert not success
    assert "La contraseña no cumple" in msg

    # Try valid password and user
    success, msg = register_user("juan", "Juan@2026!Pro", "contador", db_path=auth_db)
    assert success
    assert "registrado con éxito" in msg

    # Duplicate registration should fail
    success, msg = register_user("juan", "Juan@2026!Pro", "contador", db_path=auth_db)
    assert not success
    assert "ya existe" in msg

    # Check login success
    success, msg, user = authenticate_user("juan", "Juan@2026!Pro", db_path=auth_db)
    assert success
    assert msg == "Login exitoso."
    assert user['username'] == 'juan'
    assert user['role'] == 'contador'

    # Check login failure
    success, msg, user = authenticate_user("juan", "wrongpass", db_path=auth_db)
    assert not success
    assert "incorrectos" in msg

def test_lockout_mechanism(auth_db):
    # Register test user
    register_user("testlock", "Lock@2026!Safe", "contador", db_path=auth_db)

    # Fail 4 times
    for i in range(1, 5):
        success, msg, user = authenticate_user("testlock", "wrong", db_path=auth_db)
        assert not success
        assert f"Intentos fallidos: {i}/5" in msg

    # 5th failure should trigger 15-minute lockout
    success, msg, user = authenticate_user("testlock", "wrong", db_path=auth_db)
    assert not success
    assert "Usuario bloqueado por 15 minutos" in msg

    # 6th attempt should immediately return lockout message
    success, msg, user = authenticate_user("testlock", "wrong", db_path=auth_db)
    assert not success
    assert "Usuario bloqueado temporalmente." in msg

def test_admin_password_reset(auth_db):
    # Lock the admin
    for i in range(5):
        authenticate_user("admin", "wrong", db_path=auth_db)

    # Try login admin (should be locked)
    success, msg, user = authenticate_user("admin", "Admin@2026!", db_path=auth_db)
    assert not success
    assert "Usuario bloqueado" in msg

    # Reset admin password
    success, msg = reset_admin_password(db_path=auth_db)
    assert success
    assert "reseteada" in msg

    # Try login admin now (should succeed)
    success, msg, user = authenticate_user("admin", "Admin@2026!", db_path=auth_db)
    assert success
    assert user['username'] == 'admin'

def test_edit_user_role_and_status(auth_db):
    register_user("test_edit", "Edit@2026!Safe", "contador", db_path=auth_db)

    # Update to manager & deactivate
    success, msg = edit_user_role_and_status("test_edit", "gerente", 0, db_path=auth_db)
    assert success

    # Login should fail since they are inactive
    success, msg, user = authenticate_user("test_edit", "Edit@2026!Safe", db_path=auth_db)
    assert not success
    assert "inactivo" in msg

    # List all users
    users = get_all_users(db_path=auth_db)
    usernames = [u['username'] for u in users]
    assert "test_edit" in usernames
