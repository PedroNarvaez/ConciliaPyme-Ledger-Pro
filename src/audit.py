import hashlib
from datetime import datetime
from src.database import get_db_connection, DB_FILE

def compute_event_hash(prev_hash: str, timestamp: str, actor: str, event_type: str, description: str) -> str:
    """Computes SHA-256 of the concatenated event fields and previous hash."""
    payload = f"{prev_hash or ''}|{timestamp}|{actor}|{event_type}|{description}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def log_audit_event(actor: str, event_type: str, description: str, db_path: str = DB_FILE) -> str:
    """Logs an event in the audit trail with chained SHA-256 hashing."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Get last audit entry to get its hash as the prev_hash
        cursor.execute("SELECT event_hash FROM audit_log ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        prev_hash = last_row['event_hash'] if last_row else "GENESIS_AUDIT"

        timestamp = datetime.now().isoformat()
        event_hash = compute_event_hash(prev_hash, timestamp, actor, event_type, description)

        cursor.execute("""
            INSERT INTO audit_log (timestamp, actor, event_type, description, prev_hash, event_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, actor, event_type, description, prev_hash, event_hash))
        conn.commit()
        return event_hash
    except Exception as e:
        print(f"Error logging audit event: {e}")
        return ""
    finally:
        conn.close()

def verify_audit_trail_integrity(db_path: str = DB_FILE) -> tuple[bool, str, list[dict]]:
    """
    Verifies that no entries in the audit trail have been modified, deleted, or inserted out of order.
    Returns: (is_valid, message, list_of_errors)
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM audit_log ORDER BY id ASC")
        rows = cursor.fetchall()
        if not rows:
            return True, "El registro de auditoría está vacío. Integridad intacta.", []

        errors = []
        expected_prev_hash = "GENESIS_AUDIT"

        for i, row in enumerate(rows):
            entry_id = row['id']
            timestamp = row['timestamp']
            actor = row['actor']
            event_type = row['event_type']
            description = row['description']
            prev_hash = row['prev_hash']
            event_hash = row['event_hash']

            # Check link to previous
            if prev_hash != expected_prev_hash:
                errors.append({
                    'id': entry_id,
                    'error': f"Discrepancia en prev_hash. Esperado: {expected_prev_hash}, Encontrado: {prev_hash}"
                })

            # Verify current hash calculation
            calculated_hash = compute_event_hash(prev_hash, timestamp, actor, event_type, description)
            if calculated_hash != event_hash:
                errors.append({
                    'id': entry_id,
                    'error': f"Hash de evento inválido. Calculado: {calculated_hash}, Guardado: {event_hash}"
                })

            # Advance expected previous hash
            expected_prev_hash = event_hash

        if errors:
            return False, f"Se detectaron {len(errors)} fallos de integridad en la auditoría.", errors
        return True, "Integridad de la auditoría verificada con éxito. Todos los eslabones son válidos.", []
    except Exception as e:
        return False, f"Error durante la verificación: {str(e)}", []
    finally:
        conn.close()

def get_all_audit_logs(db_path: str = DB_FILE) -> list[dict]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_log ORDER BY id DESC")
    rows = cursor.fetchall()
    logs = [dict(row) for row in rows]
    conn.close()
    return logs
