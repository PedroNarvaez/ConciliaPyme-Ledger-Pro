"""
ConciliaPyme Ledger Pro - Aplicación de Escritorio para Conciliación Financiera
Versión 2.3.0
Basada en tesis: "Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permissionada"

Copyright 2026 © Creado por Pedro Narváez y Ariel Torres.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
import base64
import csv
import io
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Any, Tuple
import threading
import http.server
import socketserver
import re

# Constantes
VERSION = "2.3.0"
APP_NAME = "ConciliaPyme Ledger Pro"
COPYRIGHT = "2026 © Creado por Pedro Narváez y Ariel Torres."
DB_NAME = "conciliapyme.db"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 15
COTIZACION_API_URL = "https://dolar.melizeche.com/api/1.0/"

# Rutas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DEMO_DIR = BASE_DIR / "demo"
FABRIC_DIR = BASE_DIR / "fabric"

DATA_DIR.mkdir(exist_ok=True)
DEMO_DIR.mkdir(exist_ok=True)


class DatabaseManager:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DATA_DIR / DB_NAME)
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializa todas las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'contador',
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Tabla de intentos de login
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                attempt_time TEXT NOT NULL,
                success INTEGER NOT NULL
            )
        ''')
        
        # Tabla de configuración de empresa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_config (
                id INTEGER PRIMARY KEY,
                name TEXT,
                ruc TEXT,
                branch TEXT,
                license_holder TEXT,
                license_key TEXT,
                license_expires TEXT,
                license_signature TEXT
            )
        ''')
        
        # Tabla de reglas de conciliación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reconciliation_rules (
                id INTEGER PRIMARY KEY,
                date_tolerance_days INTEGER DEFAULT 3,
                amount_tolerance REAL DEFAULT 0.01,
                blockchain_platform TEXT DEFAULT 'hyperledger'
            )
        ''')
        
        # Tabla de corridas de conciliación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reconciliation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_code TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                total_sales INTEGER,
                total_bank_movements INTEGER,
                reconciled_count INTEGER,
                discrepancy_count INTEGER,
                pending_count INTEGER,
                status TEXT NOT NULL
            )
        ''')
        
        # Tabla de resultados de conciliación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reconciliation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                sale_ref TEXT,
                bank_ref TEXT,
                customer TEXT,
                description TEXT,
                sale_date TEXT,
                bank_date TEXT,
                sale_amount REAL,
                bank_amount REAL,
                currency TEXT,
                status TEXT NOT NULL,
                tx_hash TEXT,
                FOREIGN KEY (run_id) REFERENCES reconciliation_runs(id)
            )
        ''')
        
        # Tabla de ledger blockchain
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                node TEXT NOT NULL,
                platform TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                tx_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                block_hash TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Tabla de auditoría
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                description TEXT,
                prev_hash TEXT,
                event_hash TEXT NOT NULL
            )
        ''')
        
        # Tabla de preferencias de tema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Tabla de caché de cotización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizacion_cache (
                id INTEGER PRIMARY KEY,
                source TEXT,
                buy_price REAL,
                sell_price REAL,
                reference_price REAL,
                updated_at TEXT
            )
        ''')
        
        # Tabla de ventas importadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT,
                customer TEXT,
                date TEXT,
                amount REAL,
                currency TEXT,
                imported_at TEXT
            )
        ''')
        
        # Tabla de movimientos bancarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT,
                description TEXT,
                date TEXT,
                amount REAL,
                currency TEXT,
                imported_at TEXT
            )
        ''')
        
        # Insertar datos iniciales si no existen
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            self._create_admin_user(cursor)
        
        cursor.execute('SELECT COUNT(*) FROM reconciliation_rules')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO reconciliation_rules (date_tolerance_days, amount_tolerance, blockchain_platform)
                VALUES (3, 0.01, 'hyperledger')
            ''')
        
        cursor.execute('SELECT COUNT(*) FROM preferences WHERE key = "theme"')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO preferences (key, value) VALUES ("theme", "system")')
        
        # Insertar caché inicial de cotización
        cursor.execute('SELECT COUNT(*) FROM cotizacion_cache')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO cotizacion_cache (source, buy_price, sell_price, reference_price, updated_at)
                VALUES ('BCP', 7850.0, 7950.0, 7900.0, ?)
            ''', (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
    
    def _create_admin_user(self, cursor):
        """Crea el usuario admin por defecto"""
        salt = secrets.token_hex(32)
        password = "Admin@2026!"
        password_hash = self._hash_password(password, salt)
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt, role, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', password_hash, salt, 'admin', 1, now, now))
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash de contraseña usando PBKDF2-SHA256"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def validate_login(self, username: str, password: str) -> Tuple[bool, str]:
        """Valida credenciales de usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar bloqueos
        cursor.execute('''
            SELECT attempt_time FROM login_attempts 
            WHERE username = ? AND success = 0 
            ORDER BY attempt_time DESC LIMIT ?
        ''', (username, MAX_LOGIN_ATTEMPTS))
        
        attempts = cursor.fetchall()
        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            last_attempt = datetime.fromisoformat(attempts[-1][0])
            lockout_end = last_attempt + timedelta(minutes=LOCKOUT_TIME_MINUTES)
            if datetime.now() < lockout_end:
                remaining = (lockout_end - datetime.now()).seconds // 60
                conn.close()
                return False, f"Cuenta bloqueada. Intente en {remaining} minutos."
        
        # Buscar usuario
        cursor.execute('SELECT * FROM users WHERE username = ? AND active = 1', (username,))
        user = cursor.fetchone()
        
        if not user:
            self._log_login_attempt(username, False)
            conn.close()
            return False, "Usuario o contraseña incorrectos."
        
        # Validar contraseña
        expected_hash = self._hash_password(password, user['salt'])
        if user['password_hash'] != expected_hash:
            self._log_login_attempt(username, False)
            conn.close()
            return False, "Usuario o contraseña incorrectos."
        
        self._log_login_attempt(username, True)
        conn.close()
        return True, user['role']
    
    def _log_login_attempt(self, username: str, success: bool):
        """Registra intento de login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO login_attempts (username, attempt_time, success)
            VALUES (?, ?, ?)
        ''', (username, datetime.now().isoformat(), 1 if success else 0))
        conn.commit()
        conn.close()
    
    def log_audit_event(self, event_type: str, user_id: int = None, description: str = ""):
        """Registra evento de auditoría con hash encadenado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener último hash
        cursor.execute('SELECT event_hash FROM audit_log ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        prev_hash = row[0] if row else "0" * 64
        
        # Crear hash del evento
        event_data = f"{event_type}:{user_id}:{description}:{prev_hash}"
        event_hash = hashlib.sha256(event_data.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO audit_log (timestamp, event_type, user_id, description, prev_hash, event_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), event_type, user_id, description, prev_hash, event_hash))
        
        conn.commit()
        conn.close()
        return event_hash
    
    def verify_audit_integrity(self) -> Tuple[bool, str]:
        """Verifica integridad de la cadena de auditoría"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM audit_log ORDER BY id')
        events = cursor.fetchall()
        
        prev_hash = "0" * 64
        for event in events:
            event_data = f"{event['event_type']}:{event['user_id']}:{event['description']}:{prev_hash}"
            expected_hash = hashlib.sha256(event_data.encode()).hexdigest()
            
            if event['event_hash'] != expected_hash:
                conn.close()
                return False, f"Integridad comprometida en evento ID {event['id']}"
            
            prev_hash = event['event_hash']
        
        conn.close()
        return True, "Auditoría íntegra"
    
    def get_preference(self, key: str, default: str = "") -> str:
        """Obtiene preferencia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    
    def set_preference(self, key: str, value: str):
        """Guarda preferencia"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()
    
    def add_to_ledger(self, actor: str, node: str, platform: str, tx_data: str, status: str) -> dict:
        """Agrega entrada al ledger blockchain"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener último índice y hash
        cursor.execute('SELECT * FROM blockchain_ledger ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            index = row['index'] + 1
            prev_hash = row['block_hash']
        else:
            index = 0
            prev_hash = "0" * 64
        
        timestamp = datetime.now().isoformat()
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        block_data = f"{index}:{timestamp}:{actor}:{node}:{platform}:{prev_hash}:{tx_hash}:{status}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO blockchain_ledger (index, timestamp, actor, node, platform, prev_hash, tx_hash, status, block_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (index, timestamp, actor, node, platform, prev_hash, tx_hash, status, block_hash))
        
        conn.commit()
        conn.close()
        
        return {
            'index': index,
            'timestamp': timestamp,
            'actor': actor,
            'node': node,
            'platform': platform,
            'prev_hash': prev_hash,
            'tx_hash': tx_hash,
            'status': status,
            'block_hash': block_hash
        }
    
    def verify_ledger_integrity(self) -> Tuple[bool, str]:
        """Verifica integridad del ledger blockchain"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM blockchain_ledger ORDER BY id')
        blocks = cursor.fetchall()
        
        prev_hash = "0" * 64
        for block in blocks:
            if block['prev_hash'] != prev_hash:
                conn.close()
                return False, f"Integridad comprometida en bloque {block['index']}"
            
            # Verificar hash del bloque
            block_data = f"{block['index']}:{block['timestamp']}:{block['actor']}:{block['node']}:{block['platform']}:{block['prev_hash']}:{block['tx_hash']}:{block['status']}"
            expected_hash = hashlib.sha256(block_data.encode()).hexdigest()
            
            if block['block_hash'] != expected_hash:
                conn.close()
                return False, f"Hash inválido en bloque {block['index']}"
            
            prev_hash = block['block_hash']
        
        conn.close()
        return True, "Ledger íntegro"
    
    def get_dashboard_metrics(self) -> dict:
        """Obtiene métricas para el dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metrics = {}
        
        cursor.execute('SELECT COUNT(*) FROM sales')
        metrics['total_sales'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM bank_movements')
        metrics['total_bank'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM reconciliation_results WHERE status = "conciliada"')
        metrics['reconciled'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM reconciliation_results WHERE status = "discrepancia"')
        metrics['discrepancies'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM reconciliation_results WHERE status = "pendiente"')
        metrics['pending'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM blockchain_ledger')
        metrics['blocks'] = cursor.fetchone()[0]
        
        conn.close()
        return metrics
    
    def create_backup(self, backup_path: str, encryption_key: str) -> bool:
        """Crea backup cifrado de la base de datos"""
        try:
            # Leer base de datos
            with open(self.db_path, 'rb') as f:
                db_data = f.read()
            
            # Generar clave de cifrado desde la contraseña
            key = hashlib.pbkdf2_hmac('sha256', encryption_key.encode(), b'conciliapyme_backup', 100000, 32)
            
            # Cifrado XOR simple (para producción usar AES)
            encrypted = bytes(a ^ b for a, b in zip(db_data, (key * (len(db_data) // 32 + 1))[:len(db_data)]))
            
            # Agregar HMAC
            hmac_value = hmac.new(key, encrypted, hashlib.sha256).digest()
            
            # Escribir archivo
            with open(backup_path, 'wb') as f:
                f.write(struct.pack('>I', len(hmac_value)))
                f.write(hmac_value)
                f.write(encrypted)
            
            return True
        except Exception as e:
            print(f"Error creando backup: {e}")
            return False
    
    def restore_backup(self, backup_path: str, encryption_key: str) -> bool:
        """Restaura backup cifrado"""
        try:
            with open(backup_path, 'rb') as f:
                hmac_len = struct.unpack('>I', f.read(4))[0]
                stored_hmac = f.read(hmac_len)
                encrypted = f.read()
            
            # Generar clave
            key = hashlib.pbkdf2_hmac('sha256', encryption_key.encode(), b'conciliapyme_backup', 100000, 32)
            
            # Verificar HMAC
            expected_hmac = hmac.new(key, encrypted, hashlib.sha256).digest()
            if not hmac.compare_digest(stored_hmac, expected_hmac):
                return False
            
            # Descifrar
            decrypted = bytes(a ^ b for a, b in zip(encrypted, (key * (len(encrypted) // 32 + 1))[:len(encrypted)]))
            
            # Escribir base de datos
            with open(self.db_path, 'wb') as f:
                f.write(decrypted)
            
            return True
        except Exception as e:
            print(f"Error restaurando backup: {e}")
            return False


class CotizacionManager:
    """Gestor de cotización USD/PYG"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.cached_data = None
    
    def fetch_cotizacion(self) -> Optional[dict]:
        """Obtiene cotización de la API"""
        try:
            req = urllib.request.Request(COTIZACION_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                result = {
                    'updated': data.get('updated', datetime.now().isoformat()),
                    'sources': {}
                }
                
                # Parsear fuentes
                if 'dolarpy' in data:
                    dolarpy = data['dolarpy']
                    for source in ['bcp', 'set', 'familiar', 'cambioschaco']:
                        if source in dolarpy:
                            src_data = dolarpy[source]
                            result['sources'][source.upper()] = {
                                'buy': float(src_data.get('compra', 0)),
                                'sell': float(src_data.get('venta', 0)),
                                'reference': float(src_data.get('promedio', (src_data.get('compra', 0) + src_data.get('venta', 0)) / 2))
                            }
                
                self.cached_data = result
                self._save_to_cache(result)
                return result
                
        except Exception as e:
            print(f"Error fetching cotización: {e}")
            return self._load_from_cache()
    
    def _save_to_cache(self, data: dict):
        """Guarda cotización en caché"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        for source, values in data['sources'].items():
            cursor.execute('''
                INSERT OR REPLACE INTO cotizacion_cache (source, buy_price, sell_price, reference_price, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (source, values['buy'], values['sell'], values['reference'], data['updated']))
        
        conn.commit()
        conn.close()
    
    def _load_from_cache(self) -> Optional[dict]:
        """Carga cotización desde caché"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cotizacion_cache')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
        
        result = {'sources': {}, 'updated': rows[0]['updated_at'] if rows else datetime.now().isoformat()}
        for row in rows:
            result['sources'][row['source']] = {
                'buy': row['buy_price'],
                'sell': row['sell_price'],
                'reference': row['reference_price']
            }
        
        return result


class ThemeManager:
    """Gestor de temas visuales"""
    
    THEMES = {
        'light': {
            'bg': '#ffffff',
            'fg': '#000000',
            'frame_bg': '#f0f0f0',
            'button_bg': '#e1e1e1',
            'button_fg': '#000000',
            'accent': '#007acc',
            'header_bg': '#007acc',
            'header_fg': '#ffffff'
        },
        'dark': {
            'bg': '#1a1a2e',
            'fg': '#eaeaea',
            'frame_bg': '#16213e',
            'button_bg': '#0f3460',
            'button_fg': '#eaeaea',
            'accent': '#00d9ff',
            'header_bg': '#0f3460',
            'header_fg': '#00d9ff'
        }
    }
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.current_theme = 'light'
    
    def get_theme(self, theme_name: str) -> dict:
        """Obtiene configuración de tema"""
        return self.THEMES.get(theme_name, self.THEMES['light'])
    
    def apply_theme(self, root: tk.Tk, theme_name: str):
        """Aplica tema a la ventana principal"""
        theme = self.get_theme(theme_name)
        
        root.configure(bg=theme['bg'])
        style = ttk.Style(root)
        
        style.theme_create("custom", parent="clam", settings={
            "TFrame": {"configure": {"background": theme['frame_bg']}},
            "TLabel": {"configure": {"background": theme['frame_bg'], "foreground": theme['fg']}},
            "TButton": {"configure": {"background": theme['button_bg'], "foreground": theme['button_fg']}},
            "TLabelframe": {"configure": {"background": theme['frame_bg'], "foreground": theme['accent']}},
            "TLabelframe.Label": {"configure": {"background": theme['frame_bg'], "foreground": theme['accent']}},
            "Treeview": {"configure": {"background": theme['bg'], "foreground": theme['fg'], "fieldbackground": theme['bg']}},
            "Treeview.Heading": {"configure": {"background": theme['header_bg'], "foreground": theme['header_fg']}},
            "TNotebook": {"configure": {"background": theme['frame_bg']}},
            "TNotebook.Tab": {"configure": {"background": theme['button_bg'], "foreground": theme['fg']}},
            "TEntry": {"configure": {"background": theme['bg'], "foreground": theme['fg'], "fieldbackground": theme['bg']}},
            "TCombobox": {"configure": {"background": theme['button_bg'], "foreground": theme['fg'], "fieldbackground": theme['bg']}},
        })
        
        style.theme_use("custom")
        self.current_theme = theme_name


class LoginWindow:
    """Ventana de login"""
    
    def __init__(self, root: tk.Tk, db: DatabaseManager, on_login_success):
        self.root = root
        self.db = db
        self.on_login_success = on_login_success
        
        self.root.title(f"{APP_NAME} - Login")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Configura interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text=APP_NAME, font=('Arial', 16, 'bold'))
        title_label.pack(pady=(20, 5))
        
        version_label = ttk.Label(main_frame, text=f"Versión {VERSION}", font=('Arial', 10))
        version_label.pack(pady=(0, 30))
        
        # Logo placeholder
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=20)
        
        canvas = tk.Canvas(logo_frame, width=100, height=100, bg='#0f3460', highlightthickness=0)
        canvas.pack()
        canvas.create_oval(20, 20, 80, 80, outline='#00d9ff', width=2)
        canvas.create_text(50, 50, text='CP', fill='#00d9ff', font=('Arial', 20, 'bold'))
        
        # Usuario
        user_frame = ttk.Frame(main_frame)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Usuario:").pack(anchor=tk.W)
        self.user_entry = ttk.Entry(user_frame)
        self.user_entry.pack(fill=tk.X)
        self.user_entry.focus()
        
        # Contraseña
        pass_frame = ttk.Frame(main_frame)
        pass_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pass_frame, text="Contraseña:").pack(anchor=tk.W)
        self.pass_entry = ttk.Entry(pass_frame, show="•")
        self.pass_entry.pack(fill=tk.X)
        self.pass_entry.bind('<Return>', lambda e: self.login())
        
        # Botón login
        login_btn = ttk.Button(main_frame, text="Iniciar Sesión", command=self.login)
        login_btn.pack(pady=20, fill=tk.X)
        
        # Mensaje de error
        self.error_label = ttk.Label(main_frame, text="", foreground='red')
        self.error_label.pack()
        
        # Copyright
        copyright_label = ttk.Label(main_frame, text=COPYRIGHT, font=('Arial', 8), foreground='gray')
        copyright_label.pack(side=tk.BOTTOM, pady=10)
    
    def login(self):
        """Procesa login"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        
        if not username or not password:
            self.error_label.config(text="Complete todos los campos")
            return
        
        success, message = self.db.validate_login(username, password)
        
        if success:
            self.on_login_success(username)
        else:
            self.error_label.config(text=message)
            self.pass_entry.delete(0, tk.END)


class DashboardWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root: tk.Tk, db: DatabaseManager, username: str):
        self.root = root
        self.db = db
        self.username = username
        self.user_id = self._get_user_id()
        
        self.theme_manager = ThemeManager(db)
        self.cotizacion_manager = CotizacionManager(db)
        
        self.root.title(APP_NAME)
        self.root.geometry("1200x800")
        
        self.setup_ui()
        self.load_theme()
        self.refresh_metrics()
        
        # Log audit event
        self.db.log_audit_event('login', self.user_id, f'Usuario {username} inició sesión')
    
    def _get_user_id(self) -> int:
        """Obtiene ID del usuario"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (self.username,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 1
    
    def load_theme(self):
        """Carga tema guardado"""
        theme_pref = self.db.get_preference('theme', 'system')
        
        if theme_pref == 'system':
            # Intentar detectar tema del sistema (simplificado)
            theme_pref = 'dark'  # Default a dark para look futurista
        
        self.theme_manager.apply_theme(self.root, theme_pref)
    
    def setup_ui(self):
        """Configura interfaz principal"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Backup", command=self.create_backup)
        file_menu.add_command(label="Restaurar Backup", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Usuarios", command=self.open_users_window)
        tools_menu.add_command(label="Configuración Empresa", command=self.open_company_config)
        tools_menu.add_command(label="Reglas de Conciliación", command=self.open_rules_window)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Manual de Usuario", command=self.open_manual)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
        # Frame principal con notebook
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña Dashboard
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.setup_dashboard_tab()
        
        # Pestaña Importar
        self.import_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_frame, text="Importar Datos")
        self.setup_import_tab()
        
        # Pestaña Conciliación
        self.recon_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recon_frame, text="Conciliación")
        self.setup_reconciliation_tab()
        
        # Pestaña Historial
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Historial")
        self.setup_history_tab()
        
        # Pestaña Cotización
        self.cotizacion_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cotizacion_frame, text="Cotización USD/PYG")
        self.setup_cotizacion_tab()
        
        # Pestaña Auditoría
        self.audit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audit_frame, text="Auditoría")
        self.setup_audit_tab()
        
        # Barra de estado
        self.status_bar = ttk.Label(main_frame, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_dashboard_tab(self):
        """Configura pestaña Dashboard"""
        # Frame de métricas
        metrics_frame = ttk.LabelFrame(self.dashboard_frame, text="Métricas", padding="10")
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Grid de métricas
        self.metrics_labels = {}
        metrics = [
            ('Ventas Procesadas', 'total_sales'),
            ('Movimientos Bancarios', 'total_bank'),
            ('Conciliadas', 'reconciled'),
            ('Discrepancias', 'discrepancies'),
            ('Pendientes', 'pending'),
            ('Bloques Ledger', 'blocks')
        ]
        
        for i, (label, key) in enumerate(metrics):
            col = i % 3
            row = i // 3
            
            frame = ttk.Frame(metrics_frame)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(frame, text=label, font=('Arial', 10)).pack()
            value_label = ttk.Label(frame, text="0", font=('Arial', 18, 'bold'), foreground='#00d9ff')
            value_label.pack()
            self.metrics_labels[key] = value_label
        
        # Botones de acción rápida
        actions_frame = ttk.Frame(self.dashboard_frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(actions_frame, text="Cargar Datos Demo", command=self.load_demo_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Importar Ventas", command=lambda: self.notebook.select(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Importar Banco", command=lambda: self.notebook.select(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Ejecutar Conciliación", command=lambda: self.notebook.select(2)).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Verificar Ledger", command=self.verify_ledger).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Exportar JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Exportar CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        
        # Selector de tema
        theme_frame = ttk.LabelFrame(self.dashboard_frame, text="Tema Visual", padding="10")
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value=self.db.get_preference('theme', 'system'))
        
        ttk.Radiobutton(theme_frame, text="Sistema", variable=self.theme_var, value='system', 
                       command=self.change_theme).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(theme_frame, text="Claro", variable=self.theme_var, value='light', 
                       command=self.change_theme).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(theme_frame, text="Oscuro", variable=self.theme_var, value='dark', 
                       command=self.change_theme).pack(side=tk.LEFT, padx=10)
    
    def setup_import_tab(self):
        """Configura pestaña de importación"""
        # Frame de selección de tipo
        type_frame = ttk.LabelFrame(self.import_frame, text="Tipo de Importación", padding="10")
        type_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.import_type_var = tk.StringVar(value='ventas')
        
        ttk.Radiobutton(type_frame, text="Ventas CSV", variable=self.import_type_var, value='ventas').pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Banco CSV", variable=self.import_type_var, value='banco').pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="MT940", variable=self.import_type_var, value='mt940').pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="CAMT.053 XML", variable=self.import_type_var, value='camt').pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="SIFEN/DTE XML", variable=self.import_type_var, value='sifen').pack(side=tk.LEFT, padx=10)
        
        # Frame de preset bancario
        bank_frame = ttk.LabelFrame(self.import_frame, text="Preset Bancario (para CSV)", padding="10")
        bank_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.bank_preset_var = tk.StringVar(value='familiar')
        banks = ['Banco Familiar', 'Banco Continental', 'Banco Itaú', 'Banco Basa']
        
        for bank in banks:
            ttk.Radiobutton(bank_frame, text=bank, variable=self.bank_preset_var, value=bank.lower().replace(' ', '_')).pack(side=tk.LEFT, padx=5)
        
        # Botones de acción
        btn_frame = ttk.Frame(self.import_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(btn_frame, text="Seleccionar Archivo", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Importar", command=self.import_data).pack(side=tk.LEFT, padx=5)
        
        # Área de log
        log_frame = ttk.LabelFrame(self.import_frame, text="Log de Importación", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.import_log = scrolledtext.ScrolledText(log_frame, height=15)
        self.import_log.pack(fill=tk.BOTH, expand=True)
    
    def setup_reconciliation_tab(self):
        """Configura pestaña de conciliación"""
        # Frame de configuración
        config_frame = ttk.LabelFrame(self.recon_frame, text="Configuración de Conciliación", padding="10")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Reglas actuales
        rules = self.get_reconciliation_rules()
        
        ttk.Label(config_frame, text=f"Tolerancia de Fecha: {rules['date_tolerance']} días").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(config_frame, text=f"Tolerancia de Monto: {rules['amount_tolerance']}").grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(config_frame, text=f"Plataforma: {rules['platform']}").grid(row=0, column=2, padx=10, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(self.recon_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Ejecutar Conciliación", command=self.run_reconciliation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Guardar Resultados", command=self.save_reconciliation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar Payload Fabric", command=self.export_fabric_payload).pack(side=tk.LEFT, padx=5)
        
        # Treeview de resultados
        results_frame = ttk.LabelFrame(self.recon_frame, text="Resultados", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Referencia Venta', 'Ref Banco', 'Cliente', 'Fecha Venta', 'Fecha Banco', 'Monto Venta', 'Monto Banco', 'Moneda', 'Estado')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_history_tab(self):
        """Configura pestaña de historial"""
        # Lista de corridas
        list_frame = ttk.LabelFrame(self.history_frame, text="Corridas Anteriores", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Código', 'Fecha', 'Usuario', 'Ventas', 'Banco', 'Conciliadas', 'Discrepancias', 'Pendientes', 'Estado')
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        self.history_tree.bind('<Double-1>', self.load_historical_run)
        
        # Botones
        btn_frame = ttk.Frame(self.history_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Cargar Selección", command=self.load_selected_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar Lista", command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        
        self.refresh_history()
    
    def setup_cotizacion_tab(self):
        """Configura pestaña de cotización"""
        # Frame de información
        info_frame = ttk.LabelFrame(self.cotizacion_frame, text="Cotización USD/PYG", padding="15")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botón de actualización
        ttk.Button(info_frame, text="Actualizar Cotización", command=self.refresh_cotizacion).pack(pady=10)
        
        # Grid de fuentes
        self.cotizacion_labels = {}
        sources_frame = ttk.Frame(info_frame)
        sources_frame.pack(fill=tk.X, pady=10)
        
        # Actualizar datos
        self.refresh_cotizacion()
    
    def setup_audit_tab(self):
        """Configura pestaña de auditoría"""
        # Botones
        btn_frame = ttk.Frame(self.audit_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Verificar Integridad", command=self.verify_audit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar Log", command=self.export_audit_log).pack(side=tk.LEFT, padx=5)
        
        # Treeview de eventos
        events_frame = ttk.LabelFrame(self.audit_frame, text="Eventos de Auditoría", padding="10")
        events_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Fecha', 'Evento', 'Usuario', 'Descripción', 'Hash Previo', 'Hash Evento')
        self.audit_tree = ttk.Treeview(events_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.audit_tree.heading(col, text=col)
            if col in ['Hash Previo', 'Hash Evento']:
                self.audit_tree.column(col, width=200)
            else:
                self.audit_tree.column(col, width=100)
        
        self.audit_tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_audit_log()
    
    # Métodos de funcionalidad
    
    def refresh_metrics(self):
        """Actualiza métricas del dashboard"""
        metrics = self.db.get_dashboard_metrics()
        
        for key, label in self.metrics_labels.items():
            label.config(text=str(metrics.get(key, 0)))
    
    def change_theme(self):
        """Cambia tema visual"""
        theme = self.theme_var.get()
        self.db.set_preference('theme', theme)
        self.theme_manager.apply_theme(self.root, theme)
    
    def load_demo_data(self):
        """Carga datos demo"""
        try:
            # Crear archivos demo si no existen
            self.create_demo_files()
            
            # Cargar ventas demo
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Limpiar datos existentes
            cursor.execute('DELETE FROM sales')
            cursor.execute('DELETE FROM bank_movements')
            
            # Insertar ventas demo
            demo_sales = [
                ('VNT-001', 'Cliente A', '2026-01-15', 1500000, 'PYG'),
                ('VNT-002', 'Cliente B', '2026-01-16', 2300000, 'PYG'),
                ('VNT-003', 'Cliente C', '2026-01-17', 1800000, 'PYG'),
                ('VNT-004', 'Cliente D', '2026-01-18', 3200000, 'PYG'),
                ('VNT-005', 'Cliente E', '2026-01-19', 950000, 'PYG'),
            ]
            
            for sale in demo_sales:
                cursor.execute('''
                    INSERT INTO sales (reference, customer, date, amount, currency, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (*sale, datetime.now().isoformat()))
            
            # Insertar movimientos bancarios demo
            demo_bank = [
                ('REF-001', 'Transferencia Cliente A', '2026-01-15', 1500000, 'PYG'),
                ('REF-002', 'Depósito Cliente B', '2026-01-16', 2300000, 'PYG'),
                ('REF-003', 'Transferencia Cliente C', '2026-01-17', 1750000, 'PYG'),  # Discrepancia
                ('REF-004', 'Depósito Cliente D', '2026-01-19', 3200000, 'PYG'),  # Fecha diferente
            ]
            
            for movement in demo_bank:
                cursor.execute('''
                    INSERT INTO bank_movements (reference, description, date, amount, currency, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (*movement, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.db.log_audit_event('demo_data_loaded', self.user_id, 'Datos demo cargados')
            messagebox.showinfo("Éxito", "Datos demo cargados correctamente")
            self.refresh_metrics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando datos demo: {e}")
    
    def create_demo_files(self):
        """Crea archivos demo en la carpeta demo"""
        # CSV Ventas
        ventas_csv = DEMO_DIR / "ventas_demo.csv"
        with open(ventas_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['referencia', 'cliente', 'fecha', 'monto', 'moneda'])
            writer.writerow(['VNT-001', 'Cliente A', '2026-01-15', 1500000, 'PYG'])
            writer.writerow(['VNT-002', 'Cliente B', '2026-01-16', 2300000, 'PYG'])
            writer.writerow(['VNT-003', 'Cliente C', '2026-01-17', 1800000, 'PYG'])
        
        # CSV Banco
        banco_csv = DEMO_DIR / "banco_demo.csv"
        with open(banco_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['referencia', 'descripcion', 'fecha', 'monto', 'moneda'])
            writer.writerow(['REF-001', 'Transferencia Cliente A', '2026-01-15', 1500000, 'PYG'])
            writer.writerow(['REF-002', 'Depósito Cliente B', '2026-01-16', 2300000, 'PYG'])
            writer.writerow(['REF-003', 'Transferencia Cliente C', '2026-01-17', 1750000, 'PYG'])
        
        # MT940 demo
        mt940_file = DEMO_DIR / "mt940_demo.txt"
        with open(mt940_file, 'w', encoding='utf-8') as f:
            f.write(":20:REFERENCE\n")
            f.write(":25:ACCOUNT\n")
            f.write(":28C:STATEMENT\n")
            f.write(":60F:C260115PYG1000000,00\n")
            f.write(":61:2601150115DR1500000,00NTRFREF-001\n")
            f.write(":86:Transferencia Cliente A\n")
            f.write(":61:2601160116CR2300000,00NTRFREF-002\n")
            f.write(":86:Depósito Cliente B\n")
            f.write(":62F:C260116PYG1800000,00\n")
        
        # CAMT.053 demo
        camt_file = DEMO_DIR / "camt053_demo.xml"
        with open(camt_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">\n')
            f.write('  <BkToCstmrStmt>\n')
            f.write('    <Stmt>\n')
            f.write('      <Acct><Id><IBAN>PY123456789</IBAN></Id></Acct>\n')
            f.write('      <Ntry>\n')
            f.write('        <Amt Ccy="PYG">1500000.00</Amt>\n')
            f.write('        <CdtDbtInd>CR</CdtDbtInd>\n')
            f.write('        <BookgDt><Dt>2026-01-15</Dt></BookgDt>\n')
            f.write('        <NtryDtls><TxDtls><Refs><AcctSvcrRef>REF-001</AcctSvcrRef></Refs></TxDtls></NtryDtls>\n')
            f.write('      </Ntry>\n')
            f.write('    </Stmt>\n')
            f.write('  </BkToCstmrStmt>\n')
            f.write('</Document>\n')
        
        # SIFEN XML demo
        sifen_file = DEMO_DIR / "sifen_demo.xml"
        with open(sifen_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<DTE xmlns="http://www.set.gov.py/dte/sifen">\n')
            f.write('  <DE>\n')
            f.write('    <dNrDocumento>VNT-001</dNrDocumento>\n')
            f.write('    <dFEmi>2026-01-15</dFEmi>\n')
            f.write('    <dRazSoc>Cliente A</dRazSoc>\n')
            f.write('    <dTotalGsPagar>1500000</dTotalGsPagar>\n')
            f.write('  </DE>\n')
            f.write('</DTE>\n')
    
    def select_file(self):
        """Selecciona archivo para importar"""
        filetypes = [
            ('Archivos CSV', '*.csv'),
            ('Archivos MT940', '*.txt'),
            ('Archivos XML', '*.xml'),
            ('Todos los archivos', '*.*')
        ]
        
        filename = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=filetypes)
        if filename:
            self.import_log.insert(tk.END, f"Archivo seleccionado: {filename}\n")
    
    def import_data(self):
        """Importa datos según tipo seleccionado"""
        import_type = self.import_type_var.get()
        
        if import_type == 'ventas':
            self.import_sales_csv()
        elif import_type == 'banco':
            self.import_bank_csv()
        elif import_type == 'mt940':
            self.import_mt940()
        elif import_type == 'camt':
            self.import_camt()
        elif import_type == 'sifen':
            self.import_sifen()
    
    def import_sales_csv(self):
        """Importa ventas desde CSV"""
        filename = filedialog.askopenfilename(filetypes=[('CSV', '*.csv')])
        if not filename:
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            count = 0
            
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute('''
                        INSERT INTO sales (reference, customer, date, amount, currency, imported_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('referencia', row.get('reference', '')),
                        row.get('cliente', row.get('customer', '')),
                        row.get('fecha', row.get('date', '')),
                        float(row.get('monto', row.get('amount', 0))),
                        row.get('moneda', row.get('currency', 'PYG')),
                        datetime.now().isoformat()
                    ))
                    count += 1
            
            conn.commit()
            conn.close()
            
            self.import_log.insert(tk.END, f"Ventas importadas: {count}\n")
            self.db.log_audit_event('sales_imported', self.user_id, f'{count} ventas importadas')
            self.refresh_metrics()
            
        except Exception as e:
            self.import_log.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"Error importando ventas: {e}")
    
    def import_bank_csv(self):
        """Importa movimientos bancarios desde CSV"""
        filename = filedialog.askopenfilename(filetypes=[('CSV', '*.csv')])
        if not filename:
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            count = 0
            
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute('''
                        INSERT INTO bank_movements (reference, description, date, amount, currency, imported_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('referencia', row.get('reference', '')),
                        row.get('descripcion', row.get('description', '')),
                        row.get('fecha', row.get('date', '')),
                        float(row.get('monto', row.get('amount', 0))),
                        row.get('moneda', row.get('currency', 'PYG')),
                        datetime.now().isoformat()
                    ))
                    count += 1
            
            conn.commit()
            conn.close()
            
            self.import_log.insert(tk.END, f"Movimientos bancarios importados: {count}\n")
            self.db.log_audit_event('bank_imported', self.user_id, f'{count} movimientos importados')
            self.refresh_metrics()
            
        except Exception as e:
            self.import_log.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"Error importando banco: {e}")
    
    def import_mt940(self):
        """Importa archivo MT940"""
        filename = filedialog.askopenfilename(filetypes=[('MT940', '*.txt')])
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parseo simplificado de MT940
            movements = []
            lines = content.split('\n')
            current_ref = ''
            current_amount = 0
            current_date = ''
            current_desc = ''
            
            for line in lines:
                if line.startswith(':61:'):
                    # Línea de transacción
                    parts = line[4:].split('NTRF')
                    if len(parts) > 1:
                        current_ref = parts[1].strip()
                        # Extraer monto y fecha (simplificado)
                        date_str = parts[0][:6]
                        if 'C' in parts[0]:
                            current_amount = float(parts[0].split('C')[1].split('DR')[0].replace(',', '.'))
                        elif 'DR' in parts[0]:
                            current_amount = -float(parts[0].split('DR')[0].replace(',', '.'))
                
                if line.startswith(':86:'):
                    current_desc = line[4:].strip()
                    if current_ref:
                        movements.append({
                            'reference': current_ref,
                            'description': current_desc,
                            'date': f"20{date_str[:2]}-{date_str[2:4]}-{date_str[4:6]}",
                            'amount': abs(current_amount),
                            'currency': 'PYG'
                        })
            
            # Guardar en base de datos
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            for mvt in movements:
                cursor.execute('''
                    INSERT INTO bank_movements (reference, description, date, amount, currency, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (mvt['reference'], mvt['description'], mvt['date'], mvt['amount'], mvt['currency'], datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.import_log.insert(tk.END, f"MT940 importado: {len(movements)} movimientos\n")
            self.db.log_audit_event('mt940_imported', self.user_id, f'{len(movements)} movimientos MT940')
            self.refresh_metrics()
            
        except Exception as e:
            self.import_log.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"Error importando MT940: {e}")
    
    def import_camt(self):
        """Importa archivo CAMT.053 XML"""
        filename = filedialog.askopenfilename(filetypes=[('XML', '*.xml')])
        if not filename:
            return
        
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            ns = {'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'}
            
            movements = []
            for entry in root.findall('.//camt:Ntry', ns):
                amount_elem = entry.find('camt:Amt', ns)
                amount = float(amount_elem.text) if amount_elem is not None else 0
                
                date_elem = entry.find('camt:BookgDt/camt:Dt', ns)
                date = date_elem.text if date_elem is not None else ''
                
                ref_elem = entry.find('camt:NtryDtls/camt:TxDtls/camt:Refs/camt:AcctSvcrRef', ns)
                ref = ref_elem.text if ref_elem is not None else ''
                
                desc_elem = entry.find('camt:NtryDtls/camt:TxDtls/camt:RltdPties/camt:CdtrNm', ns)
                desc = desc_elem.text if desc_elem is not None else ''
                
                movements.append({
                    'reference': ref,
                    'description': desc,
                    'date': date,
                    'amount': amount,
                    'currency': amount_elem.get('Ccy', 'PYG') if amount_elem is not None else 'PYG'
                })
            
            # Guardar en base de datos
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            for mvt in movements:
                cursor.execute('''
                    INSERT INTO bank_movements (reference, description, date, amount, currency, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (mvt['reference'], mvt['description'], mvt['date'], mvt['amount'], mvt['currency'], datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.import_log.insert(tk.END, f"CAMT.053 importado: {len(movements)} movimientos\n")
            self.db.log_audit_event('camt_imported', self.user_id, f'{len(movements)} movimientos CAMT')
            self.refresh_metrics()
            
        except Exception as e:
            self.import_log.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"Error importando CAMT: {e}")
    
    def import_sifen(self):
        """Importa archivo SIFEN/DTE XML"""
        filename = filedialog.askopenfilename(filetypes=[('XML', '*.xml')])
        if not filename:
            return
        
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            ns = {'sifen': 'http://www.set.gov.py/dte/sifen'}
            
            sales = []
            for de in root.findall('.//sifen:DE', ns):
                ref_elem = de.find('sifen:dNrDocumento', ns)
                ref = ref_elem.text if ref_elem is not None else ''
                
                date_elem = de.find('sifen:dFEmi', ns)
                date = date_elem.text if date_elem is not None else ''
                
                customer_elem = de.find('sifen:dRazSoc', ns)
                customer = customer_elem.text if customer_elem is not None else ''
                
                amount_elem = de.find('sifen:dTotalGsPagar', ns)
                amount = float(amount_elem.text) if amount_elem is not None else 0
                
                sales.append({
                    'reference': ref,
                    'customer': customer,
                    'date': date,
                    'amount': amount,
                    'currency': 'PYG'
                })
            
            # Guardar en base de datos
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            for sale in sales:
                cursor.execute('''
                    INSERT INTO sales (reference, customer, date, amount, currency, imported_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (sale['reference'], sale['customer'], sale['date'], sale['amount'], sale['currency'], datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.import_log.insert(tk.END, f"SIFEN importado: {len(sales)} ventas\n")
            self.db.log_audit_event('sifen_imported', self.user_id, f'{len(sales)} ventas SIFEN')
            self.refresh_metrics()
            
        except Exception as e:
            self.import_log.insert(tk.END, f"Error: {e}\n")
            messagebox.showerror("Error", f"Error importando SIFEN: {e}")
    
    def get_reconciliation_rules(self) -> dict:
        """Obtiene reglas de conciliación"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reconciliation_rules LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'date_tolerance': row['date_tolerance_days'],
                'amount_tolerance': row['amount_tolerance'],
                'platform': row['blockchain_platform']
            }
        return {'date_tolerance': 3, 'amount_tolerance': 0.01, 'platform': 'hyperledger'}
    
    def run_reconciliation(self):
        """Ejecuta proceso de conciliación"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Obtener ventas y movimientos
            cursor.execute('SELECT * FROM sales')
            sales = cursor.fetchall()
            
            cursor.execute('SELECT * FROM bank_movements')
            movements = cursor.fetchall()
            
            if not sales or not movements:
                messagebox.showwarning("Advertencia", "No hay datos suficientes para conciliar")
                return
            
            rules = self.get_reconciliation_rules()
            date_tol = timedelta(days=rules['date_tolerance'])
            amount_tol = rules['amount_tolerance']
            
            results = []
            matched_bank_ids = set()
            
            for sale in sales:
                best_match = None
                best_score = 0
                
                for mvt in movements:
                    if mvt['id'] in matched_bank_ids:
                        continue
                    
                    score = 0
                    
                    # Comparar referencias
                    if sale['reference'] and mvt['reference'] and sale['reference'] in mvt['reference']:
                        score += 30
                    
                    # Comparar cliente/descripción
                    if sale['customer'] and mvt['description']:
                        if sale['customer'].lower() in mvt['description'].lower():
                            score += 20
                    
                    # Comparar fechas
                    try:
                        sale_date = datetime.fromisoformat(sale['date'])
                        mvt_date = datetime.fromisoformat(mvt['date'])
                        if abs((sale_date - mvt_date).days) <= date_tol.days:
                            score += 25
                    except:
                        pass
                    
                    # Comparar montos
                    amount_diff = abs(sale['amount'] - mvt['amount'])
                    if amount_diff <= amount_tol * max(sale['amount'], mvt['amount']):
                        score += 25
                    
                    if score > best_score:
                        best_score = score
                        best_match = mvt
                
                if best_match and best_score >= 50:
                    status = 'conciliada' if best_score >= 90 else 'discrepancia'
                    matched_bank_ids.add(best_match['id'])
                    
                    # Generar hash de transacción
                    tx_data = f"{sale['reference']}:{best_match['reference']}:{sale['amount']}:{best_match['amount']}:{status}"
                    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
                    
                    results.append({
                        'sale': sale,
                        'bank': best_match,
                        'status': status,
                        'tx_hash': tx_hash
                    })
                else:
                    results.append({
                        'sale': sale,
                        'bank': None,
                        'status': 'pendiente',
                        'tx_hash': ''
                    })
            
            # Guardar resultados temporalmente
            self.current_reconciliation_results = results
            self.display_reconciliation_results(results)
            
            conn.close()
            
            self.db.log_audit_event('reconciliation_executed', self.user_id, f'{len(results)} resultados generados')
            messagebox.showinfo("Éxito", f"Conciliación completada: {len(results)} registros procesados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en conciliación: {e}")
    
    def display_reconciliation_results(self, results):
        """Muestra resultados en treeview"""
        # Limpiar treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Agregar resultados
        for i, result in enumerate(results):
            sale = result['sale']
            bank = result['bank']
            
            self.results_tree.insert('', tk.END, values=(
                i + 1,
                sale['reference'],
                bank['reference'] if bank else '',
                sale['customer'],
                sale['date'],
                bank['date'] if bank else '',
                f"{sale['amount']:,.2f}",
                f"{bank['amount']:,.2f}" if bank else '',
                sale['currency'],
                result['status']
            ))
    
    def save_reconciliation(self):
        """Guarda resultados de conciliación"""
        if not hasattr(self, 'current_reconciliation_results') or not self.current_reconciliation_results:
            messagebox.showwarning("Advertencia", "No hay resultados para guardar")
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Generar código único
            run_code = f"CONC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            timestamp = datetime.now().isoformat()
            
            # Contar estados
            conciliadas = sum(1 for r in self.current_reconciliation_results if r['status'] == 'conciliada')
            discrepancias = sum(1 for r in self.current_reconciliation_results if r['status'] == 'discrepancia')
            pendientes = sum(1 for r in self.current_reconciliation_results if r['status'] == 'pendiente')
            
            # Guardar corrida
            cursor.execute('''
                INSERT INTO reconciliation_runs (run_code, timestamp, user_id, total_sales, total_bank_movements, 
                                                reconciled_count, discrepancy_count, pending_count, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (run_code, timestamp, self.user_id, len(self.current_reconciliation_results), 
                  len(self.current_reconciliation_results), conciliadas, discrepancias, pendientes, 'completed'))
            
            run_id = cursor.lastrowid
            
            # Guardar resultados individuales
            for result in self.current_reconciliation_results:
                sale = result['sale']
                bank = result['bank']
                
                cursor.execute('''
                    INSERT INTO reconciliation_results (run_id, sale_ref, bank_ref, customer, description, 
                                                       sale_date, bank_date, sale_amount, bank_amount, currency, status, tx_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (run_id, sale['reference'], bank['reference'] if bank else '', sale['customer'],
                      bank['description'] if bank else '', sale['date'], bank['date'] if bank else '',
                      sale['amount'], bank['amount'] if bank else 0, sale['currency'], result['status'], result['tx_hash']))
                
                # Agregar al ledger blockchain
                tx_data = f"{sale['reference']}:{bank['reference'] if bank else 'NONE'}:{result['status']}"
                self.db.add_to_ledger(
                    actor=self.username,
                    node='local-node-1',
                    platform='hyperledger',
                    tx_data=tx_data,
                    status=result['status']
                )
            
            conn.commit()
            conn.close()
            
            self.db.log_audit_event('reconciliation_saved', self.user_id, f'Corrida {run_code} guardada')
            self.refresh_metrics()
            self.refresh_history()
            
            messagebox.showinfo("Éxito", f"Conciliación guardada con código: {run_code}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando conciliación: {e}")
    
    def verify_ledger(self):
        """Verifica integridad del ledger"""
        success, message = self.db.verify_ledger_integrity()
        
        if success:
            messagebox.showinfo("Verificación", "✓ Ledger íntegro")
            self.db.log_audit_event('ledger_verified', self.user_id, 'Ledger verificado exitosamente')
        else:
            messagebox.showerror("Error", f"✗ {message}")
            self.db.log_audit_event('ledger_verification_failed', self.user_id, message)
    
    def export_json(self):
        """Exporta reporte JSON completo"""
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not filename:
            return
        
        try:
            report = {
                'app': APP_NAME,
                'version': VERSION,
                'timestamp': datetime.now().isoformat(),
                'user': self.username,
                'metrics': self.db.get_dashboard_metrics(),
                'rules': self.get_reconciliation_rules()
            }
            
            # Agregar últimos resultados
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reconciliation_runs ORDER BY id DESC LIMIT 1')
            last_run = cursor.fetchone()
            
            if last_run:
                cursor.execute('SELECT * FROM reconciliation_results WHERE run_id = ?', (last_run['id'],))
                results = [dict(row) for row in cursor.fetchall()]
                report['last_run'] = dict(last_run)
                report['results'] = results
            
            cursor.execute('SELECT * FROM blockchain_ledger ORDER BY id DESC LIMIT 10')
            report['recent_ledger'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.db.log_audit_event('export_json', self.user_id, f'Reporte exportado a {filename}')
            messagebox.showinfo("Éxito", "Reporte JSON exportado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando JSON: {e}")
    
    def export_csv(self):
        """Exporta resultados a CSV"""
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not filename:
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reconciliation_results ORDER BY id DESC LIMIT 100')
            results = cursor.fetchall()
            conn.close()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Referencia Venta', 'Ref Banco', 'Cliente', 'Fecha Venta', 'Fecha Banco', 
                               'Monto Venta', 'Monto Banco', 'Moneda', 'Estado', 'Tx Hash'])
                
                for row in results:
                    writer.writerow([
                        row['id'], row['sale_ref'], row['bank_ref'], row['customer'],
                        row['sale_date'], row['bank_date'], row['sale_amount'], row['bank_amount'],
                        row['currency'], row['status'], row['tx_hash']
                    ])
            
            self.db.log_audit_event('export_csv', self.user_id, f'Resultados exportados a {filename}')
            messagebox.showinfo("Éxito", "Reporte CSV exportado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando CSV: {e}")
    
    def export_fabric_payload(self):
        """Exporta payload para Hyperledger Fabric"""
        if not hasattr(self, 'current_reconciliation_results') or not self.current_reconciliation_results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not filename:
            return
        
        try:
            payload = {
                'chaincode': 'conciliapyme',
                'function': 'RegisterEvidence',
                'args': []
            }
            
            for result in self.current_reconciliation_results:
                evidence = {
                    'saleRef': result['sale']['reference'],
                    'bankRef': result['bank']['reference'] if result['bank'] else '',
                    'status': result['status'],
                    'timestamp': datetime.now().isoformat(),
                    'actor': self.username
                }
                payload['args'].append(json.dumps(evidence))
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            
            messagebox.showinfo("Éxito", "Payload Fabric exportado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando payload: {e}")
    
    def refresh_history(self):
        """Actualiza lista de historial"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reconciliation_runs ORDER BY id DESC')
        runs = cursor.fetchall()
        conn.close()
        
        for run in runs:
            self.history_tree.insert('', tk.END, values=(
                run['run_code'],
                run['timestamp'][:10],
                run['user_id'],
                run['total_sales'],
                run['total_bank_movements'],
                run['reconciled_count'],
                run['discrepancy_count'],
                run['pending_count'],
                run['status']
            ))
    
    def load_selected_run(self):
        """Carga corrida seleccionada"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una corrida")
            return
        
        item = self.history_tree.item(selection[0])
        run_code = item['values'][0]
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM reconciliation_runs WHERE run_code = ?', (run_code,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('SELECT * FROM reconciliation_results WHERE run_id = ?', (row[0],))
            results = cursor.fetchall()
            conn.close()
            
            formatted_results = []
            for r in results:
                formatted_results.append({
                    'sale': {'reference': r['sale_ref'], 'customer': r['customer'], 'date': r['sale_date'], 
                            'amount': r['sale_amount'], 'currency': r['currency']},
                    'bank': {'reference': r['bank_ref'], 'description': r['description'], 'date': r['bank_date'],
                            'amount': r['bank_amount']} if r['bank_ref'] else None,
                    'status': r['status'],
                    'tx_hash': r['tx_hash']
                })
            
            self.current_reconciliation_results = formatted_results
            self.display_reconciliation_results(formatted_results)
            self.notebook.select(2)
        else:
            conn.close()
    
    def load_historical_run(self, event):
        """Carga corrida al hacer doble click"""
        self.load_selected_run()
    
    def refresh_cotizacion(self):
        """Actualiza cotización USD/PYG"""
        # Limpiar frame anterior
        for widget in self.cotizacion_frame.winfo_children():
            if widget != self.cotizacion_frame:
                widget.destroy()
        
        # Re-crear estructura
        info_frame = ttk.LabelFrame(self.cotizacion_frame, text="Cotización USD/PYG", padding="15")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(info_frame, text="Actualizar Cotización", command=self.refresh_cotizacion).pack(pady=10)
        
        data = self.cotizacion_manager.fetch_cotizacion()
        
        if data:
            status_label = ttk.Label(info_frame, text=f"Última actualización: {data.get('updated', 'N/A')}", 
                                    font=('Arial', 9, 'italic'))
            status_label.pack()
            
            # Grid de fuentes
            sources_frame = ttk.Frame(info_frame)
            sources_frame.pack(fill=tk.X, pady=10)
            
            columns = 3
            for i, (source, values) in enumerate(data.get('sources', {}).items()):
                col = i % columns
                row = i // columns
                
                frame = ttk.LabelFrame(sources_frame, text=source, padding="10")
                frame.grid(row=row, column=col, padx=10, pady=5, sticky='nsew')
                
                ttk.Label(frame, text=f"Compra: ₲ {values['buy']:,.2f}").pack(anchor=tk.W)
                ttk.Label(frame, text=f"Venta: ₲ {values['sell']:,.2f}").pack(anchor=tk.W)
                ttk.Label(frame, text=f"Referencial: ₲ {values['reference']:,.2f}", 
                         font=('Arial', 10, 'bold'), foreground='#00d9ff').pack(anchor=tk.W)
            
            # Conversor
            converter_frame = ttk.LabelFrame(self.cotizacion_frame, text="Conversor USD a PYG", padding="10")
            converter_frame.pack(fill=tk.X, padx=10, pady=10)
            
            conv_inner = ttk.Frame(converter_frame)
            conv_inner.pack(fill=tk.X)
            
            ttk.Label(conv_inner, text="Monto USD:").grid(row=0, column=0, padx=5, pady=5)
            self.usd_entry = ttk.Entry(conv_inner, width=15)
            self.usd_entry.grid(row=0, column=1, padx=5, pady=5)
            self.usd_entry.insert(0, "100")
            
            ttk.Label(conv_inner, text="Fuente:").grid(row=0, column=2, padx=5, pady=5)
            self.source_var = tk.StringVar(value=list(data['sources'].keys())[0] if data['sources'] else 'BCP')
            source_combo = ttk.Combobox(conv_inner, textvariable=self.source_var, 
                                       values=list(data['sources'].keys()), width=15)
            source_combo.grid(row=0, column=3, padx=5, pady=5)
            
            ttk.Button(conv_inner, text="Convertir", command=self.convert_currency).grid(row=0, column=4, padx=10)
            
            self.conversion_result = ttk.Label(conv_inner, text="", font=('Arial', 12, 'bold'), foreground='#00d9ff')
            self.conversion_result.grid(row=1, column=0, columnspan=5, pady=10)
        else:
            ttk.Label(info_frame, text="No hay datos de cotización disponibles", foreground='red').pack()
    
    def convert_currency(self):
        """Convierte USD a PYG"""
        try:
            usd_amount = float(self.usd_entry.get())
            source = self.source_var.get()
            
            data = self.cotizacion_manager.fetch_cotizacion()
            if data and source in data.get('sources', {}):
                rate = data['sources'][source]['reference']
                pyg_amount = usd_amount * rate
                self.conversion_result.config(text=f"₲ {pyg_amount:,.2f}")
            else:
                self.conversion_result.config(text="Fuente no disponible")
        except ValueError:
            self.conversion_result.config(text="Monto inválido")
    
    def refresh_audit_log(self):
        """Actualiza log de auditoría"""
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM audit_log ORDER BY id DESC LIMIT 100')
        events = cursor.fetchall()
        conn.close()
        
        for event in events:
            self.audit_tree.insert('', tk.END, values=(
                event['id'],
                event['timestamp'][:19],
                event['event_type'],
                event['user_id'],
                event['description'][:50],
                event['prev_hash'][:16] + '...',
                event['event_hash'][:16] + '...'
            ))
    
    def verify_audit(self):
        """Verifica integridad de auditoría"""
        success, message = self.db.verify_audit_integrity()
        
        if success:
            messagebox.showinfo("Verificación", "✓ Auditoría íntegra")
        else:
            messagebox.showerror("Error", f"✗ {message}")
    
    def export_audit_log(self):
        """Exporta log de auditoría"""
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not filename:
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM audit_log ORDER BY id')
            events = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({'audit_log': events}, f, indent=2)
            
            messagebox.showinfo("Éxito", "Log de auditoría exportado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {e}")
    
    def create_backup(self):
        """Crea backup cifrado"""
        filename = filedialog.asksaveasfilename(defaultextension=".cplybak", 
                                               initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cplybak",
                                               filetypes=[("Backup", "*.cplybak")])
        if not filename:
            return
        
        # Pedir clave
        from tkinter import simpledialog
        password = simpledialog.askstring("Clave de Cifrado", "Ingrese clave para cifrar el backup:", show='•')
        
        if not password:
            return
        
        if self.db.create_backup(filename, password):
            messagebox.showinfo("Éxito", "Backup creado correctamente")
            self.db.log_audit_event('backup_created', self.user_id, f'Backup creado: {filename}')
        else:
            messagebox.showerror("Error", "Error creando backup")
    
    def restore_backup(self):
        """Restaura backup cifrado"""
        filename = filedialog.askopenfilename(filetypes=[("Backup", "*.cplybak")])
        if not filename:
            return
        
        from tkinter import simpledialog
        password = simpledialog.askstring("Clave de Descifrado", "Ingrese clave del backup:", show='•')
        
        if not password:
            return
        
        if self.db.restore_backup(filename, password):
            messagebox.showinfo("Éxito", "Backup restaurado correctamente. Reinicie la aplicación.")
            self.db.log_audit_event('backup_restored', self.user_id, f'Backup restaurado: {filename}')
        else:
            messagebox.showerror("Error", "Clave incorrecta o archivo corrupto")
    
    def open_users_window(self):
        """Abre ventana de gestión de usuarios"""
        UsersWindow(self.root, self.db, self.username)
    
    def open_company_config(self):
        """Abre configuración de empresa"""
        CompanyConfigWindow(self.root, self.db)
    
    def open_rules_window(self):
        """Abre configuración de reglas"""
        RulesWindow(self.root, self.db)
    
    def open_manual(self):
        """Abre manual de usuario"""
        manual_path = BASE_DIR / "docs" / "MANUAL_USUARIO.md"
        if manual_path.exists():
            import webbrowser
            webbrowser.open(f"file://{manual_path}")
        else:
            messagebox.showinfo("Manual", "El manual estará disponible en docs/MANUAL_USUARIO.md")
    
    def show_about(self):
        """Muestra información de la aplicación"""
        about_text = f"""{APP_NAME}
Versión {VERSION}

Basada en tesis:
"Sistema de Conciliación Financiera Automatizada para PYMES mediante Tecnología Blockchain Permissionada"

{COPYRIGHT}

Características:
- Conciliación automática de ventas y movimientos bancarios
- Evidencia criptográfica tipo blockchain
- Múltiples formatos de importación (CSV, MT940, CAMT.053, SIFEN)
- Integración futura con Hyperledger Fabric
- Auditoría con hash encadenado
- Cotización USD/PYG en tiempo real
- Backup cifrado
        """
        messagebox.showinfo("Acerca de", about_text)


class UsersWindow:
    """Ventana de gestión de usuarios"""
    
    def __init__(self, parent, db, current_username):
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Usuarios")
        self.window.geometry("600x500")
        self.db = db
        self.current_username = current_username
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interfaz"""
        # Lista de usuarios
        list_frame = ttk.LabelFrame(self.window, text="Usuarios", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Username', 'Rol', 'Activo', 'Creado')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        self.users_tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_users()
        
        # Botones
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Nuevo Usuario", command=self.new_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Activar/Desactivar", command=self.toggle_active).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=self.refresh_users).pack(side=tk.LEFT, padx=5)
    
    def refresh_users(self):
        """Actualiza lista de usuarios"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, role, active, created_at FROM users')
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            self.users_tree.insert('', tk.END, values=(
                user['username'],
                user['role'],
                'Sí' if user['active'] else 'No',
                user['created_at'][:10]
            ))
    
    def new_user(self):
        """Crea nuevo usuario"""
        NewUserDialog(self.window, self.db)
        self.refresh_users()
    
    def edit_user(self):
        """Edita usuario seleccionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        EditUserDialog(self.window, self.db, username)
        self.refresh_users()
    
    def toggle_active(self):
        """Activa/desactiva usuario"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.users_tree.item(selection[0])
        username = item['values'][0]
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT active FROM users WHERE username = ?', (username,))
        current = cursor.fetchone()[0]
        
        cursor.execute('UPDATE users SET active = ?, updated_at = ? WHERE username = ?', 
                      (0 if current else 1, datetime.now().isoformat(), username))
        conn.commit()
        conn.close()
        
        self.refresh_users()


class NewUserDialog:
    """Diálogo para crear usuario"""
    
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Usuario")
        self.dialog.geometry("400x350")
        self.db = db
        
        ttk.Label(self.dialog, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self.dialog)
        self.username_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Contraseña:").pack(pady=5)
        self.password_entry = ttk.Entry(self.dialog, show='•')
        self.password_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Confirmar Contraseña:").pack(pady=5)
        self.confirm_entry = ttk.Entry(self.dialog, show='•')
        self.confirm_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Rol:").pack(pady=5)
        self.role_var = tk.StringVar(value='contador')
        role_combo = ttk.Combobox(self.dialog, textvariable=self.role_var, 
                                 values=['admin', 'contador', 'gerente', 'auditor'])
        role_combo.pack(pady=5)
        
        ttk.Button(self.dialog, text="Crear", command=self.create).pack(pady=20)
    
    def create(self):
        """Crea usuario"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if not self.validate_password(password):
            messagebox.showerror("Error", 
                "Contraseña debe tener:\n- Mínimo 10 caracteres\n- Mayúscula\n- Minúscula\n- Número\n- Símbolo")
            return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            salt = secrets.token_hex(32)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, role, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, role, 1, now, now))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            self.dialog.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El usuario ya existe")
        finally:
            conn.close()
    
    def validate_password(self, password):
        """Valida política de contraseña fuerte"""
        if len(password) < 10:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True


class EditUserDialog:
    """Diálogo para editar usuario"""
    
    def __init__(self, parent, db, username):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Editar Usuario: {username}")
        self.dialog.geometry("400x300")
        self.db = db
        self.username = username
        
        ttk.Label(self.dialog, text="Nueva Contraseña (dejar vacío para no cambiar):").pack(pady=5)
        self.password_entry = ttk.Entry(self.dialog, show='•')
        self.password_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Rol:").pack(pady=5)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE username = ?', (username,))
        current_role = cursor.fetchone()[0]
        conn.close()
        
        self.role_var = tk.StringVar(value=current_role)
        role_combo = ttk.Combobox(self.dialog, textvariable=self.role_var, 
                                 values=['admin', 'contador', 'gerente', 'auditor'])
        role_combo.pack(pady=5)
        
        ttk.Button(self.dialog, text="Guardar", command=self.save).pack(pady=20)
    
    def save(self):
        """Guarda cambios"""
        password = self.password_entry.get()
        role = self.role_var.get()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if password:
            salt = secrets.token_hex(32)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ?, role = ?, updated_at = ?
                WHERE username = ?
            ''', (password_hash, salt, role, datetime.now().isoformat(), self.username))
        else:
            cursor.execute('''
                UPDATE users SET role = ?, updated_at = ? WHERE username = ?
            ''', (role, datetime.now().isoformat(), self.username))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Éxito", "Usuario actualizado")
        self.dialog.destroy()


class CompanyConfigWindow:
    """Ventana de configuración de empresa"""
    
    def __init__(self, parent, db):
        self.window = tk.Toplevel(parent)
        self.window.title("Configuración de Empresa")
        self.window.geometry("500x400")
        self.db = db
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Configura interfaz"""
        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ('Nombre Empresa:', 'name'),
            ('RUC:', 'ruc'),
            ('Sucursal:', 'branch'),
            ('Titular de Licencia:', 'holder')
        ]
        
        self.entries = {}
        for label, key in fields:
            ttk.Label(form_frame, text=label).pack(anchor=tk.W, pady=5)
            entry = ttk.Entry(form_frame)
            entry.pack(fill=tk.X, pady=5)
            self.entries[key] = entry
        
        ttk.Button(form_frame, text="Guardar", command=self.save).pack(pady=20)
        ttk.Button(form_frame, text="Generar Licencia Demo", command=self.generate_demo_license).pack()
    
    def load_config(self):
        """Carga configuración existente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM company_config LIMIT 1')
        config = cursor.fetchone()
        conn.close()
        
        if config:
            self.entries['name'].insert(0, config['name'] or '')
            self.entries['ruc'].insert(0, config['ruc'] or '')
            self.entries['branch'].insert(0, config['branch'] or '')
            self.entries['holder'].insert(0, config['license_holder'] or '')
    
    def save(self):
        """Guarda configuración"""
        name = self.entries['name'].get().strip()
        ruc = self.entries['ruc'].get().strip()
        branch = self.entries['branch'].get().strip()
        holder = self.entries['holder'].get().strip()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM company_config')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO company_config (name, ruc, branch, license_holder)
                VALUES (?, ?, ?, ?)
            ''', (name, ruc, branch, holder))
        else:
            cursor.execute('''
                UPDATE company_config SET name = ?, ruc = ?, branch = ?, license_holder = ?
            ''', (name, ruc, branch, holder))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Éxito", "Configuración guardada")
    
    def generate_demo_license(self):
        """Genera licencia demo"""
        holder = self.entries['holder'].get().strip() or "Demo User"
        ruc = self.entries['ruc'].get().strip() or "00000000-0"
        
        # Generar clave de licencia
        license_key = f"DEMO-{secrets.token_hex(8).upper()}"
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        
        # Firmar con HMAC
        secret = b"conciliapyme_demo_secret"
        signature = hmac.new(secret, f"{holder}:{ruc}:{expires}".encode(), hashlib.sha256).hexdigest()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM company_config')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO company_config (license_key, license_expires, license_signature)
                VALUES (?, ?, ?)
            ''', (license_key, expires, signature))
        else:
            cursor.execute('''
                UPDATE company_config SET license_key = ?, license_expires = ?, license_signature = ?
            ''', (license_key, expires, signature))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Licencia Demo", 
                           f"Licencia generada:\n{license_key}\nVence: {expires[:10]}")


class RulesWindow:
    """Ventana de configuración de reglas"""
    
    def __init__(self, parent, db):
        self.window = tk.Toplevel(parent)
        self.window.title("Reglas de Conciliación")
        self.window.geometry("400x300")
        self.db = db
        
        self.setup_ui()
        self.load_rules()
    
    def setup_ui(self):
        """Configura interfaz"""
        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Tolerancia de Fecha (días):").pack(anchor=tk.W, pady=5)
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_frame, text="Tolerancia de Monto (%):").pack(anchor=tk.W, pady=5)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(form_frame, text="Plataforma Blockchain:").pack(anchor=tk.W, pady=5)
        self.platform_var = tk.StringVar(value='hyperledger')
        platform_combo = ttk.Combobox(form_frame, textvariable=self.platform_var, 
                                     values=['hyperledger', 'ethereum', 'private'])
        platform_combo.pack(fill=tk.X, pady=5)
        
        ttk.Button(form_frame, text="Guardar", command=self.save).pack(pady=20)
    
    def load_rules(self):
        """Carga reglas existentes"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reconciliation_rules LIMIT 1')
        rules = cursor.fetchone()
        conn.close()
        
        if rules:
            self.date_entry.insert(0, str(rules['date_tolerance_days']))
            self.amount_entry.insert(0, str(rules['amount_tolerance']))
            self.platform_var.set(rules['blockchain_platform'])
    
    def save(self):
        """Guarda reglas"""
        try:
            date_tol = int(self.date_entry.get())
            amount_tol = float(self.amount_entry.get())
            platform = self.platform_var.get()
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reconciliation_rules 
                SET date_tolerance_days = ?, amount_tolerance = ?, blockchain_platform = ?
            ''', (date_tol, amount_tol, platform))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Reglas actualizadas")
        except ValueError:
            messagebox.showerror("Error", "Valores inválidos")


class ConciliaPymeApp:
    """Aplicación principal"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.db = DatabaseManager()
        self.show_login()
    
    def show_login(self):
        """Muestra ventana de login"""
        self.login_window = LoginWindow(self.root, self.db, self.on_login_success)
    
    def on_login_success(self, username):
        """Callback de login exitoso"""
        self.login_window.root.destroy()
        self.root = tk.Tk()
        self.dashboard = DashboardWindow(self.root, self.db, username)
    
    def run(self):
        """Ejecuta aplicación"""
        self.root.mainloop()


def main():
    """Función principal"""
    app = ConciliaPymeApp()
    app.run()


if __name__ == "__main__":
    main()
