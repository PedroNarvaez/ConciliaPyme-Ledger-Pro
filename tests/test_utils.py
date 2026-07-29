import os
import time
import pytest
from src.database import init_db, get_db_connection
from src.api_quote import fetch_and_cache_quotes, read_cached_quotes, convert_usd_to_pyg, convert_pyg_to_usd
from src.backup import create_encrypted_backup, restore_encrypted_backup
from src.sync_server import LANSyncServer, import_snapshot_from_url

TEST_DB = "test_utils_main.db"
TEST_BACKUP = "test_backup.cplybak"
TEST_RESTORE_DB = "test_utils_restore.db"

@pytest.fixture
def fresh_db():
    for f in (TEST_DB, TEST_BACKUP, TEST_RESTORE_DB):
        if os.path.exists(f):
            os.remove(f)

    init_db(TEST_DB)
    yield TEST_DB

    for f in (TEST_DB, TEST_BACKUP, TEST_RESTORE_DB):
        if os.path.exists(f):
            os.remove(f)

def test_api_quote_caching(fresh_db):
    # Check that initial seeds exist in SQLite
    cached = read_cached_quotes(fresh_db)
    assert 'bcp' in cached
    assert cached['bcp']['compra'] == 7250.0
    assert cached['bcp']['venta'] == 7290.0

    # Check conversion
    converted = convert_usd_to_pyg(100.0, "bcp", db_path=fresh_db)
    assert converted == 729000.0

    converted_pyg = convert_pyg_to_usd(725000.0, "bcp", db_path=fresh_db)
    assert converted_pyg == 100.0

def test_encrypted_backup_flow(fresh_db):
    passphrase = "SecretBackupPassword123!"

    # Create backup
    success, msg = create_encrypted_backup(fresh_db, TEST_BACKUP, passphrase)
    assert success
    assert os.path.exists(TEST_BACKUP)

    # Try restoring to a different location with WRONG password (should fail)
    success, msg = restore_encrypted_backup(TEST_BACKUP, TEST_RESTORE_DB, "wrong_password",)
    assert not success
    assert "incorrecta" in msg or "integridad" in msg
    assert not os.path.exists(TEST_RESTORE_DB)

    # Restore with CORRECT password (should succeed)
    success, msg = restore_encrypted_backup(TEST_BACKUP, TEST_RESTORE_DB, passphrase)
    assert success
    assert os.path.exists(TEST_RESTORE_DB)

    # Verify contents of restored database
    cached = read_cached_quotes(TEST_RESTORE_DB)
    assert 'bcp' in cached

def test_lan_sync_server(fresh_db):
    # Setup server
    server = LANSyncServer(port=18080, db_path=fresh_db)
    server.start()

    # Wait half a second for server thread to start
    time.sleep(0.5)

    # Setup client db (clean)
    init_db(TEST_RESTORE_DB)

    # Sync from server
    url = "http://localhost:18080/snapshot"
    success, msg = import_snapshot_from_url(url, db_path=TEST_RESTORE_DB)

    # Stop server
    server.stop()

    assert success
    assert "Sincronización finalizada" in msg

    # rest of DB was synced properly
    conn = get_db_connection(TEST_RESTORE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM quote_cache")
    assert cursor.fetchone()[0] == 5
    conn.close()
