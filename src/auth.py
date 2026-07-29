import re
from datetime import datetime, timedelta
from src.database import get_db_connection, hash_password, verify_password, DB_FILE

def validate_strong_password(password: str) -> bool:
    """
    Política de contraseña fuerte:
    - mínimo 10 caracteres
    - mayúscula
    - minúscula
    - número
    - símbolo
    """
    if len(password) < 10:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    # symbols: any non-alphanumeric character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\[\]\\/\-+=\s~`';]", password):
        return False
    return True

def register_user(username: str, password_plain: str, role: str, active: int = 1, db_path: str = DB_FILE) -> tuple[bool, str]:
    if not username or not password_plain or not role:
        return False, "Todos los campos son obligatorios."
    if role not in ['admin', 'contador', 'gerente', 'auditor']:
        return False, "Rol inválido."
    if not validate_strong_password(password_plain):
        return False, "La contraseña no cumple con la política de seguridad (mínimo 10 caracteres, mayúscula, minúscula, número y símbolo)."

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            return False, "El usuario ya existe."

        h_pass = hash_password(password_plain)
        cursor.execute("INSERT INTO users (username, password_hash, role, active) VALUES (?, ?, ?, ?)",
                       (username, h_pass, role, active))
        conn.commit()
        return True, "Usuario registrado con éxito."
    except Exception as e:
        return False, f"Error al registrar usuario: {str(e)}"
    finally:
        conn.close()

def edit_user_role_and_status(username: str, role: str, active: int, db_path: str = DB_FILE) -> tuple[bool, str]:
    if role not in ['admin', 'contador', 'gerente', 'auditor']:
        return False, "Rol inválido."

    # Prevent deactivating the only active admin, or changing admin's role if it's the last one
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        if username == 'admin' and active == 0:
            # Check how many active admins are there
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND active=1")
            if cursor.fetchone()[0] <= 1:
                return False, "No se puede desactivar al único administrador activo."

        cursor.execute("UPDATE users SET role = ?, active = ? WHERE username = ?", (role, active, username))
        conn.commit()
        return True, "Usuario actualizado con éxito."
    except Exception as e:
        return False, f"Error al actualizar: {str(e)}"
    finally:
        conn.close()

def change_user_password(username: str, new_password_plain: str, db_path: str = DB_FILE) -> tuple[bool, str]:
    if not validate_strong_password(new_password_plain):
        return False, "La contraseña no cumple con la política de seguridad."

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        h_pass = hash_password(new_password_plain)
        cursor.execute("UPDATE users SET password_hash = ?, failed_attempts = 0, lockout_until = NULL WHERE username = ?",
                       (h_pass, username))
        conn.commit()
        return True, "Contraseña actualizada con éxito."
    except Exception as e:
        return False, f"Error al cambiar contraseña: {str(e)}"
    finally:
        conn.close()

def reset_admin_password(db_path: str = DB_FILE) -> tuple[bool, str]:
    """Resets admin password to default Admin@2026! and clears lockout/attempts."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        default_pass = "Admin@2026!"
        h_pass = hash_password(default_pass)
        cursor.execute("""
            UPDATE users
            SET password_hash = ?, failed_attempts = 0, lockout_until = NULL, active = 1
            WHERE username = 'admin'
        """, (h_pass,))
        conn.commit()
        return True, "Contraseña de admin reseteada a Admin@2026!"
    except Exception as e:
        return False, f"Error al resetear admin: {str(e)}"
    finally:
        conn.close()

def authenticate_user(username: str, password_plain: str, db_path: str = DB_FILE) -> tuple[bool, str, dict | None]:
    """
    Autentica al usuario.
    Retorna: (success, message, user_dict)
    Reglas:
    - Bloqueo tras 5 intentos fallidos.
    - Bloqueo temporal de 15 minutos.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return False, "Usuario o contraseña incorrectos.", None

        user_id = user['id']
        active = user['active']
        failed_attempts = user['failed_attempts'] or 0
        lockout_until_str = user['lockout_until']
        role = user['role']

        if not active:
            return False, "El usuario está inactivo. Contacte al administrador.", None

        # Check lockout
        if lockout_until_str:
            lockout_until = datetime.fromisoformat(lockout_until_str)
            if datetime.now() < lockout_until:
                remaining = (lockout_until - datetime.now()).total_seconds()
                mins = int(remaining // 60) + 1
                return False, f"Usuario bloqueado temporalmente. Intente en {mins} minutos.", None
            else:
                # Lockout period expired, clear it
                cursor.execute("UPDATE users SET failed_attempts = 0, lockout_until = NULL WHERE id = ?", (user_id,))
                conn.commit()
                failed_attempts = 0

        # Verify password
        if verify_password(password_plain, user['password_hash']):
            # Success: reset failed attempts
            cursor.execute("UPDATE users SET failed_attempts = 0, lockout_until = NULL WHERE id = ?", (user_id,))
            conn.commit()
            return True, "Login exitoso.", {
                'id': user_id,
                'username': username,
                'role': role,
                'active': active
            }
        else:
            # Failure: increment failed attempts
            failed_attempts += 1
            if failed_attempts >= 5:
                lockout_until = datetime.now() + timedelta(minutes=15)
                cursor.execute("UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE id = ?",
                               (failed_attempts, lockout_until.isoformat(), user_id))
                conn.commit()
                return False, "Usuario bloqueado por 15 minutos tras 5 intentos fallidos.", None
            else:
                cursor.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (failed_attempts, user_id))
                conn.commit()
                return False, f"Usuario o contraseña incorrectos. Intentos fallidos: {failed_attempts}/5", None
    except Exception as e:
        return False, f"Error de autenticación: {str(e)}", None
    finally:
        conn.close()

def get_all_users(db_path: str = DB_FILE) -> list[dict]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, active, failed_attempts, lockout_until FROM users")
    rows = cursor.fetchall()
    users = [dict(row) for row in rows]
    conn.close()
    return users
