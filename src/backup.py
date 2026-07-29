import os
import hashlib
import hmac
import binascii

def derive_keys(passphrase: str, salt: bytes) -> tuple[bytes, bytes]:
    """Derives encryption and MAC keys from a passphrase and salt using PBKDF2-SHA256."""
    # Derive a 64-byte key stream, split into 32-byte encryption key and 32-byte MAC key
    key_material = hashlib.pbkdf2_hmac('sha256', passphrase.encode('utf-8'), salt, 10000, 64)
    return key_material[:32], key_material[32:]

def generate_keystream(key: bytes, iv: bytes, length: int) -> bytes:
    """Generates a keystream of specified length using HMAC-SHA256 in CTR-like mode."""
    keystream = bytearray()
    counter = 0
    while len(keystream) < length:
        # block payload = IV + counter (4 bytes big-endian)
        payload = iv + counter.to_bytes(4, byteorder='big')
        block = hmac.new(key, payload, hashlib.sha256).digest()
        keystream.extend(block)
        counter += 1
    return bytes(keystream[:length])

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def encrypt_data(data: bytes, passphrase: str) -> bytes:
    """
    Encrypts bytes using an authenticated stream cipher based on PBKDF2, HMAC, and CTR mode.
    Format of output: SALT (16) | IV (16) | HMAC-SHA256 of Ciphertext (32) | Ciphertext
    """
    salt = os.urandom(16)
    iv = os.urandom(16)

    k_enc, k_mac = derive_keys(passphrase, salt)

    # Generate keystream and XOR data to produce ciphertext
    keystream = generate_keystream(k_enc, iv, len(data))
    ciphertext = xor_bytes(data, keystream)

    # Compute MAC over ciphertext
    mac = hmac.new(k_mac, ciphertext, hashlib.sha256).digest()

    return salt + iv + mac + ciphertext

def decrypt_data(encrypted_data: bytes, passphrase: str) -> tuple[bool, bytes]:
    """
    Decrypts and validates the integrity of encrypted bytes.
    Returns: (is_valid, decrypted_bytes)
    """
    if len(encrypted_data) < 64:
        return False, b""

    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    mac_expected = encrypted_data[32:64]
    ciphertext = encrypted_data[64:]

    k_enc, k_mac = derive_keys(passphrase, salt)

    # Verify MAC first (Encrypt-then-MAC)
    mac_calculated = hmac.new(k_mac, ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac_calculated, mac_expected):
        return False, b"" # Tampered or invalid key

    # Decrypt
    keystream = generate_keystream(k_enc, iv, len(ciphertext))
    decrypted = xor_bytes(ciphertext, keystream)
    return True, decrypted

def create_encrypted_backup(db_filepath: str, backup_filepath: str, passphrase: str) -> tuple[bool, str]:
    """Reads SQLite database, encrypts it, and writes to a backup file."""
    try:
        if not os.path.exists(db_filepath):
            return False, "La base de datos original no existe."

        with open(db_filepath, 'rb') as f:
            data = f.read()

        encrypted = encrypt_data(data, passphrase)

        with open(backup_filepath, 'wb') as f:
            f.write(encrypted)

        return True, "Copia de seguridad cifrada creada con éxito."
    except Exception as e:
        return False, f"Error al realizar copia de seguridad: {str(e)}"

def restore_encrypted_backup(backup_filepath: str, db_filepath: str, passphrase: str) -> tuple[bool, str]:
    """Validates, decrypts backup file, and overwrites target database."""
    try:
        if not os.path.exists(backup_filepath):
            return False, "El archivo de copia de seguridad no existe."

        with open(backup_filepath, 'rb') as f:
            encrypted_data = f.read()

        success, decrypted = decrypt_data(encrypted_data, passphrase)
        if not success:
            return False, "Error de integridad o contraseña incorrecta. No se pudo restaurar."

        # Write to target database
        # If target db already exists, overwrite it safely
        with open(db_filepath, 'wb') as f:
            f.write(decrypted)

        return True, "Copia de seguridad restaurada con éxito."
    except Exception as e:
        return False, f"Error al restaurar: {str(e)}"
