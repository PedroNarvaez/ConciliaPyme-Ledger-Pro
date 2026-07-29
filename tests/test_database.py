import os
import sqlite3
import pytest
from src.database import init_db, get_db_connection, verify_password, hash_password

TEST_DB_FILE = "test_conciliapyme.db"

@pytest.fixture
def test_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    init_db(TEST_DB_FILE)
    yield TEST_DB_FILE
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_database_creation(test_db):
    conn = get_db_connection(test_db)
    cursor = conn.cursor()

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    assert 'users' in tables
    assert 'config' in tables
    assert 'runs' in tables
    assert 'results' in tables
    assert 'ledger' in tables
    assert 'audit_log' in tables
    assert 'license_info' in tables
    assert 'quote_cache' in tables

    # Verify default admin seed
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    admin = cursor.fetchone()
    assert admin is not None
    assert admin['role'] == 'admin'
    assert verify_password("Admin@2026!", admin['password_hash']) is True

    # Verify initial config seeds
    cursor.execute("SELECT value FROM config WHERE key='theme'")
    theme = cursor.fetchone()
    assert theme['value'] == 'Sistema'

    conn.close()

def test_password_hash():
    p = "SuperSecret123!"
    hp = hash_password(p)
    assert verify_password(p, hp) is True
    assert verify_password("wrong", hp) is False
