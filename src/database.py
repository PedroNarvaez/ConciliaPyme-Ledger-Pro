import os
import sqlite3
import hashlib
import binascii
from datetime import datetime

DB_FILE = "conciliapyme.db"

def get_db_connection(db_path=DB_FILE):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    # PBKDF2-SHA256 hash format: pbkdf2_sha256$iterations$salt$hash
    salt = os.urandom(16)
    iterations = 100000
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    salt_hex = binascii.hexlify(salt).decode('utf-8')
    dk_hex = binascii.hexlify(dk).decode('utf-8')
    return f"pbkdf2_sha256${iterations}${salt_hex}${dk_hex}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        parts = hashed.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = binascii.unhexlify(parts[2])
        dk_expected = binascii.unhexlify(parts[3])
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return dk == dk_expected
    except Exception:
        return False

def init_db(db_path=DB_FILE):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL, -- admin, contador, gerente, auditor
        active INTEGER DEFAULT 1,
        failed_attempts INTEGER DEFAULT 0,
        lockout_until TEXT
    )
    """)

    # 2. Config/Rules Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # 3. Runs (Runs/Corridas) Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        code TEXT PRIMARY KEY, -- CONC-YYYYMMDD-HHMMSS
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        platform TEXT NOT NULL,
        rule_date_tolerance INTEGER,
        rule_amount_tolerance REAL,
        sales_count INTEGER,
        bank_count INTEGER,
        conciliated_count INTEGER,
        discrepancy_count INTEGER,
        pending_count INTEGER
    )
    """)

    # 4. Results (Detalle de conciliación) Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_code TEXT,
        sale_ref TEXT,
        sale_client TEXT,
        sale_date TEXT,
        sale_amount REAL,
        sale_currency TEXT,
        bank_ref TEXT,
        bank_desc TEXT,
        bank_date TEXT,
        bank_amount REAL,
        bank_currency TEXT,
        status TEXT, -- conciliada, discrepancia, pendiente
        difference REAL,
        row_hash TEXT,
        FOREIGN KEY(run_code) REFERENCES runs(code)
    )
    """)

    # 5. Ledger Table (Criptográfica local)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ledger (
        block_index INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        node TEXT NOT NULL,
        platform TEXT NOT NULL,
        prev_hash TEXT NOT NULL,
        tx_hash TEXT NOT NULL, -- Hash of results associated
        status TEXT NOT NULL,
        block_hash TEXT NOT NULL
    )
    """)

    # 6. Audit Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        actor TEXT NOT NULL,
        event_type TEXT NOT NULL, -- login, login_failed, import, reconciliation, export, verification, user_change, backup, sync
        description TEXT NOT NULL,
        prev_hash TEXT,
        event_hash TEXT NOT NULL
    )
    """)

    # 7. License Info Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS license_info (
        ruc TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        branch TEXT,
        license_key TEXT NOT NULL,
        license_type TEXT NOT NULL, -- demo, full
        expires_at TEXT NOT NULL
    )
    """)

    # 8. Quote Cache Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quote_cache (
        source TEXT PRIMARY KEY,
        compra REAL NOT NULL,
        venta REAL NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed Default Data
    # Default Admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        admin_pass = "Admin@2026!"
        h_pass = hash_password(admin_pass)
        cursor.execute("INSERT INTO users (username, password_hash, role, active) VALUES (?, ?, ?, ?)",
                       ('admin', h_pass, 'admin', 1))

    # Default settings
    defaults = {
        'theme': 'Sistema',
        'tolerance_days': '3',
        'tolerance_amount': '0.0',
        'blockchain_platform': 'Hyperledger Fabric (Permissioned)',
        'current_license_ruc': '',
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (k, v))

    # Seed initial exchange rate cache (USD to PYG)
    initial_rates = [
        ('bcp', 7250.0, 7290.0, '2026-01-01 08:00:00'),
        ('set', 7240.0, 7285.0, '2026-01-01 08:00:00'),
        ('familiar', 7230.0, 7310.0, '2026-01-01 08:00:00'),
        ('cambioschaco', 7245.0, 7295.0, '2026-01-01 08:00:00'),
        ('referencial', 7250.0, 7290.0, '2026-01-01 08:00:00')
    ]
    for source, buy, sell, updated in initial_rates:
        cursor.execute("INSERT OR IGNORE INTO quote_cache (source, compra, venta, updated_at) VALUES (?, ?, ?, ?)",
                       (source, buy, sell, updated))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
