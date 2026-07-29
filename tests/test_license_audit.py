import os
import pytest
import sqlite3
from src.database import init_db, get_db_connection
from src.license_module import (
    generate_license_key,
    generate_demo_license,
    validate_license,
    save_license,
    get_active_license
)
from src.audit import (
    log_audit_event,
    verify_audit_trail_integrity,
    get_all_audit_logs
)

TEST_DB_FILE = "test_lic_audit.db"

@pytest.fixture
def lic_audit_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    init_db(TEST_DB_FILE)
    yield TEST_DB_FILE
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_license_module(lic_audit_db):
    # Generate manual license
    ruc = "1234567-8"
    company = "La Pyme S.A."
    branch = "Asunción"
    expires = "2027-12-31"
    lic_type = "full"

    key = generate_license_key(ruc, company, branch, expires, lic_type)
    assert len(key) == 64  # SHA-256 hex is 64 chars

    # Validate correctly
    is_valid, msg = validate_license(ruc, company, branch, expires, lic_type, key)
    assert is_valid

    # Try with wrong company name
    is_valid, msg = validate_license(ruc, "Another Company", branch, expires, lic_type, key)
    assert not is_valid
    assert "firma" in msg.lower()

    # Try expired date
    expired_key = generate_license_key(ruc, company, branch, "2020-01-01", lic_type)
    is_valid, msg = validate_license(ruc, company, branch, "2020-01-01", lic_type, expired_key)
    assert not is_valid
    assert "expiró" in msg.lower()

    # Save to db
    success, msg = save_license(ruc, company, branch, expires, lic_type, key, db_path=lic_audit_db)
    assert success

    # Get active license
    active = get_active_license(db_path=lic_audit_db)
    assert active is not None
    assert active['ruc'] == ruc
    assert active['is_valid'] is True

def test_demo_license(lic_audit_db):
    demo = generate_demo_license()
    assert demo['license_type'] == 'demo'
    assert demo['ruc'] == "44444401-7"

    # Save demo to db
    success, msg = save_license(
        demo['ruc'], demo['company_name'], demo['branch'], demo['expires_at'], demo['license_type'], demo['license_key'],
        db_path=lic_audit_db
    )
    assert success

    active = get_active_license(db_path=lic_audit_db)
    assert active is not None
    assert active['license_type'] == 'demo'

def test_audit_log_trail(lic_audit_db):
    # Log some events
    hash1 = log_audit_event("admin", "login", "Admin logged in", db_path=lic_audit_db)
    hash2 = log_audit_event("admin", "import", "Imported sales", db_path=lic_audit_db)
    hash3 = log_audit_event("contador", "reconciliation", "Ran reconciliation", db_path=lic_audit_db)

    assert hash1 != ""
    assert hash2 != ""
    assert hash3 != ""

    # Get and check log order
    logs = get_all_audit_logs(db_path=lic_audit_db)
    assert len(logs) == 3
    # logs are in reverse order (DESC)
    assert logs[0]['event_type'] == 'reconciliation'
    assert logs[1]['event_type'] == 'import'
    assert logs[2]['event_type'] == 'login'

    assert logs[1]['event_hash'] == logs[0]['prev_hash']
    assert logs[2]['event_hash'] == logs[1]['prev_hash']
    assert logs[2]['prev_hash'] == "GENESIS_AUDIT"

    # Verify chain integrity
    is_valid, msg, errors = verify_audit_trail_integrity(db_path=lic_audit_db)
    assert is_valid
    assert not errors

def test_audit_log_tampering(lic_audit_db):
    log_audit_event("admin", "login", "Event A", db_path=lic_audit_db)
    log_audit_event("admin", "backup", "Event B", db_path=lic_audit_db)

    # Manually tamper with database to simulate an unauthorized modification
    conn = get_db_connection(lic_audit_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE audit_log SET description = 'Tampered description' WHERE id = 1")
    conn.commit()
    conn.close()

    # Verify should detect tampering
    is_valid, msg, errors = verify_audit_trail_integrity(db_path=lic_audit_db)
    assert not is_valid
    assert len(errors) > 0
    assert "Hash de evento inválido" in errors[0]['error'] or "Discrepancia en prev_hash" in errors[0]['error']
