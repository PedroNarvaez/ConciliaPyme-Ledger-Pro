import hmac
import hashlib
from datetime import datetime, date
from src.database import get_db_connection, DB_FILE

SECRET_LICENSE_KEY = b"ConciliaPymeSecret2026_Licensing_Token_99341"

def generate_license_key(ruc: str, company_name: str, branch: str, expires_at: str, license_type: str) -> str:
    """Generates an HMAC-SHA256 license signature."""
    payload = f"{ruc}|{company_name}|{branch}|{expires_at}|{license_type}"
    sig = hmac.new(SECRET_LICENSE_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return sig

def generate_demo_license(ruc: str = "44444401-7", company_name: str = "Demo S.A.") -> dict:
    """Generates a demo license valid for 30 days from now."""
    import datetime
    today = datetime.date.today()
    expires_at = (today + datetime.timedelta(days=30)).isoformat()
    branch = "Casa Central"
    license_type = "demo"
    key = generate_license_key(ruc, company_name, branch, expires_at, license_type)
    return {
        'ruc': ruc,
        'company_name': company_name,
        'branch': branch,
        'expires_at': expires_at,
        'license_type': license_type,
        'license_key': key
    }

def validate_license(ruc: str, company_name: str, branch: str, expires_at_str: str, license_type: str, license_key: str) -> tuple[bool, str]:
    """Validates the license key, expiration, and formatting."""
    try:
        # Check signature
        expected_key = generate_license_key(ruc, company_name, branch, expires_at_str, license_type)
        if not hmac.compare_digest(expected_key, license_key):
            return False, "La firma de la licencia es inválida o fue alterada."

        # Check expiration
        expires_at = datetime.fromisoformat(expires_at_str).date() if 'T' in expires_at_str else date.fromisoformat(expires_at_str)
        if date.today() > expires_at:
            return False, f"La licencia expiró el {expires_at_str}."

        return True, "Licencia válida."
    except Exception as e:
        return False, f"Error de validación de licencia: {str(e)}"

def save_license(ruc: str, company_name: str, branch: str, expires_at: str, license_type: str, license_key: str, db_path: str = DB_FILE) -> tuple[bool, str]:
    """Saves the license and updates config current RUC."""
    # Validate before saving
    is_valid, msg = validate_license(ruc, company_name, branch, expires_at, license_type, license_key)
    if not is_valid:
        return False, msg

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Save license info
        cursor.execute("""
            INSERT OR REPLACE INTO license_info (ruc, company_name, branch, license_key, license_type, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ruc, company_name, branch, license_key, license_type, expires_at))

        # Update current RUC in config
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('current_license_ruc', ?)", (ruc,))
        conn.commit()
        return True, "Licencia guardada y activada con éxito."
    except Exception as e:
        return False, f"Error al guardar la licencia: {str(e)}"
    finally:
        conn.close()

def get_active_license(db_path: str = DB_FILE) -> dict | None:
    """Reads current active license from DB and validates it."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM config WHERE key = 'current_license_ruc'")
        row = cursor.fetchone()
        if not row or not row['value']:
            return None

        ruc = row['value']
        cursor.execute("SELECT * FROM license_info WHERE ruc = ?", (ruc,))
        lic_row = cursor.fetchone()
        if not lic_row:
            return None

        lic = dict(lic_row)
        is_valid, msg = validate_license(
            lic['ruc'], lic['company_name'], lic['branch'], lic['expires_at'], lic['license_type'], lic['license_key']
        )
        lic['is_valid'] = is_valid
        lic['validation_message'] = msg
        return lic
    except Exception:
        return None
    finally:
        conn.close()
