import os
import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from src.database import get_db_connection, DB_FILE
from src.auth import (
    authenticate_user, register_user, get_all_users, edit_user_role_and_status,
    change_user_password, reset_admin_password
)
from src.license_module import (
    get_active_license, save_license, generate_demo_license, validate_license
)
from src.audit import (
    log_audit_event, verify_audit_trail_integrity, get_all_audit_logs
)
from src.importers import (
    parse_sales_csv, parse_bank_csv, parse_mt940, parse_camt053, parse_sifen_xml,
    generate_all_demo_files
)
from src.reconciliation import (
    reconcile_lists, save_reconciliation_run, verify_ledger_integrity, get_all_runs, load_reconciliation_run
)
from src.api_quote import (
    fetch_and_cache_quotes, convert_usd_to_pyg, convert_pyg_to_usd, read_cached_quotes
)
from src.backup import (
    create_encrypted_backup, restore_encrypted_backup
)
from src.sync_server import (
    LANSyncServer, import_snapshot_from_url
)

class ConciliaPymeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ConciliaPyme Ledger Pro - v2.3.0")
        self.root.geometry("1150x780")
        self.root.minsize(1050, 700)

        # Logged-in user context
        self.current_user = None

        # Temp memory for reconciliation
        self.imported_sales = []
        self.imported_bank = []
        self.active_run_results = []

        # LAN Server reference
        self.sync_server = None

        # Load theme preference from DB
        self.theme_name = self.load_theme_preference()

        # Define color palettes
        self.dark_palette = {
            "bg": "#0A192F",
            "panel": "#172A45",
            "fg": "#FFFFFF",
            "accent": "#64FFDA",       # Cyan
            "success": "#52C41A",      # Green
            "warning": "#FAAD14",      # Gold/Orange
            "text_sec": "#8892B0",     # Slate Blue / Gray
            "border": "#233554"
        }

        self.light_palette = {
            "bg": "#F4F6F9",
            "panel": "#FFFFFF",
            "fg": "#1E293B",
            "accent": "#0F172A",       # Slate Blue Dark
            "success": "#2E7D32",      # Forest Green
            "warning": "#ED6C02",      # Orange
            "text_sec": "#64748B",     # Cool Gray
            "border": "#E2E8F0"
        }

        # Active colors based on theme
        self.colors = {}
        self.apply_colors()

        # Setup modern styles
        self.setup_ttk_styles()

        # Render initial screen (Login)
        self.show_login_screen()

    def load_theme_preference(self) -> str:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key='theme'")
            row = cursor.fetchone()
            conn.close()
            return row['value'] if row else 'Sistema'
        except Exception:
            return 'Sistema'

    def save_theme_preference(self, theme: str):
        self.theme_name = theme
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('theme', ?)", (theme,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving theme: {e}")
        self.apply_colors()
        self.setup_ttk_styles()
        self.refresh_ui()

    def get_windows_theme(self) -> str:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "Claro" if value == 1 else "Oscuro"
        except Exception:
            return "Claro"

    def apply_colors(self):
        t = self.theme_name
        if t == "Sistema":
            detected = self.get_windows_theme()
            p = self.light_palette if detected == "Claro" else self.dark_palette
        elif t == "Claro":
            p = self.light_palette
        else:
            p = self.dark_palette

        self.colors = p
        self.root.configure(bg=p["bg"])

    def setup_ttk_styles(self):
        style = ttk.Style()
        # Clean existing style definitions
        style.theme_use("clam")

        bg = self.colors["bg"]
        panel = self.colors["panel"]
        fg = self.colors["fg"]
        accent = self.colors["accent"]
        text_sec = self.colors["text_sec"]
        border = self.colors["border"]

        # Configure frames
        style.configure("TFrame", background=bg)
        style.configure("Panel.TFrame", background=panel, borderwidth=1, relief="solid")

        # Configure Labels
        style.configure("TLabel", background=bg, foreground=fg, font=("Helvetica", 10))
        style.configure("Title.TLabel", background=bg, foreground=fg, font=("Helvetica", 18, "bold"))
        style.configure("Header.TLabel", background=panel, foreground=fg, font=("Helvetica", 12, "bold"))
        style.configure("Panel.TLabel", background=panel, foreground=fg, font=("Helvetica", 10))
        style.configure("PanelSec.TLabel", background=panel, foreground=text_sec, font=("Helvetica", 9))

        # Notebook style (Tabs)
        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=panel, foreground=fg, padding=[10, 4], font=("Helvetica", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", accent), ("active", accent)], foreground=[("selected", bg), ("active", bg)])

        # Treeview (results tables)
        style.configure("Treeview", background=panel, foreground=fg, fieldbackground=panel, borderwidth=0, font=("Helvetica", 9))
        style.configure("Treeview.Heading", background=bg, foreground=fg, relief="flat", font=("Helvetica", 9, "bold"))
        style.map("Treeview", background=[("selected", accent)], foreground=[("selected", bg)])

        # Buttons style
        style.configure("TButton", background=panel, foreground=fg, borderwidth=1, font=("Helvetica", 9, "bold"), padding=[10, 5])
        style.map("TButton", background=[("active", accent)], foreground=[("active", bg)])

        style.configure("Accent.TButton", background=accent, foreground=bg, borderwidth=1, font=("Helvetica", 10, "bold"), padding=[12, 6])
        style.map("Accent.TButton", background=[("active", fg)], foreground=[("active", bg)])

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_root()
        self.apply_colors()

        # Outer login container
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.place(relx=0.5, rely=0.45, anchor="center")

        # Logo Card
        logo_frame = tk.Frame(container, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=30, pady=35)
        logo_frame.pack()

        # Title
        title_label = tk.Label(logo_frame, text="ConciliaPyme Ledger Pro", font=("Helvetica", 20, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        title_label.pack(pady=(0, 5))

        subtitle_label = tk.Label(logo_frame, text="Sistema de Conciliación Financiera Automatizada", font=("Helvetica", 9), fg=self.colors["text_sec"], bg=self.colors["panel"])
        subtitle_label.pack(pady=(0, 25))

        # Fields
        lbl_user = tk.Label(logo_frame, text="Usuario:", font=("Helvetica", 10, "bold"), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_user.pack(anchor="w")
        self.ent_user = tk.Entry(logo_frame, font=("Helvetica", 11), width=28, bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_user.pack(pady=(2, 12))
        self.ent_user.insert(0, "admin")

        lbl_pass = tk.Label(logo_frame, text="Contraseña:", font=("Helvetica", 10, "bold"), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_pass.pack(anchor="w")
        self.ent_pass = tk.Entry(logo_frame, font=("Helvetica", 11), show="*", width=28, bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_pass.pack(pady=(2, 20))
        self.ent_pass.bind("<Return>", lambda e: self.handle_login())

        # Buttons
        btn_login = tk.Button(logo_frame, text="INICIAR SESIÓN", font=("Helvetica", 11, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], activebackground=self.colors["fg"], activeforeground=self.colors["bg"], relief="flat", padx=15, pady=8, command=self.handle_login)
        btn_login.pack(fill="x", pady=(0, 10))

        # Copyright
        lbl_copy = tk.Label(container, text="2026 © Creado por Pedro Narváez y Ariel Torres.", font=("Helvetica", 8, "italic"), fg=self.colors["text_sec"], bg=self.colors["bg"])
        lbl_copy.pack(pady=(25, 0))

    def handle_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get()

        success, msg, u_dict = authenticate_user(user, pwd)
        if success:
            self.current_user = u_dict
            log_audit_event(user, "login", f"Inicio de sesión exitoso. Rol: {u_dict['role']}")
            self.show_main_app()
        else:
            log_audit_event(user or "desconocido", "login_failed", f"Intento fallido de login: {msg}")
            messagebox.showerror("Error de Inicio de Sesión", msg)

    def show_main_app(self):
        self.clear_root()
        self.apply_colors()

        # Main Topbar
        topbar = tk.Frame(self.root, bg=self.colors["panel"], height=55, highlightbackground=self.colors["border"], highlightthickness=1)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        title = tk.Label(topbar, text="ConciliaPyme Ledger Pro  [v2.3.0]", font=("Helvetica", 14, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        title.pack(side="left", padx=15)

        user_info = tk.Label(topbar, text=f"Usuario: {self.current_user['username']} ({self.current_user['role'].upper()})", font=("Helvetica", 9, "bold"), fg=self.colors["fg"], bg=self.colors["panel"])
        user_info.pack(side="right", padx=15)

        btn_logout = tk.Button(topbar, text="Cerrar Sesión", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", command=self.handle_logout)
        btn_logout.pack(side="right", padx=10)

        # Outer Tabs Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize Panels
        self.create_dashboard_tab()
        self.create_cotizacion_tab()
        self.create_history_tab()
        self.create_audit_tab()

        # Conditional Admin user tab
        if self.current_user['role'] == 'admin':
            self.create_users_tab()
            self.create_license_tab()
            self.create_sync_tab()
            self.create_backup_tab()

        self.create_themes_tab()

        # Restore imported and active results data across UI/theme redraws
        self.refresh_imported_tables()
        self.refresh_results_table()

    def refresh_results_table(self):
        for r in self.table_res.get_children():
            self.table_res.delete(r)
        for res in self.active_run_results:
            self.table_res.insert("", "end", values=(
                res['sale_ref'] or "PENDIENTE",
                res['bank_ref'] or "PENDIENTE",
                res['sale_date'] or res['bank_date'],
                f"{res['difference']:.2f}",
                res['status'].upper()
            ))

    def handle_logout(self):
        if self.sync_server:
            self.sync_server.stop()
        log_audit_event(self.current_user['username'], "login", "Cierre de sesión.")
        self.current_user = None
        self.show_login_screen()

    def refresh_ui(self):
        # Stores current active tab index
        current_tab_idx = self.notebook.index(self.notebook.select()) if hasattr(self, 'notebook') else 0
        self.show_main_app()
        try:
            self.notebook.select(current_tab_idx)
        except Exception:
            pass

    # ------------------ DASHBOARD TAB ------------------
    def create_dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Dashboard ")

        # Grid layout for Dashboard
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=3)
        tab.rowconfigure(0, weight=1)

        # LEFT COLUMN: Metrics & Configuration Panel
        left_panel = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=12, pady=12)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_conf_title = tk.Label(left_panel, text="Reglas & Configuración", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_conf_title.pack(anchor="w", pady=(0, 10))

        # Tolerance Date
        lbl_t_days = tk.Label(left_panel, text="Tolerancia de Fecha (Días):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_t_days.pack(anchor="w")
        self.ent_t_days = tk.Entry(left_panel, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_t_days.pack(fill="x", pady=(2, 10))
        self.ent_t_days.insert(0, self.get_config_value("tolerance_days", "3"))

        # Tolerance Amount
        lbl_t_amt = tk.Label(left_panel, text="Tolerancia de Monto:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_t_amt.pack(anchor="w")
        self.ent_t_amt = tk.Entry(left_panel, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_t_amt.pack(fill="x", pady=(2, 10))
        self.ent_t_amt.insert(0, self.get_config_value("tolerance_amount", "0.0"))

        # Blockchain platform label
        lbl_plat = tk.Label(left_panel, text="Plataforma Blockchain:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_plat.pack(anchor="w")
        lbl_plat_val = tk.Label(left_panel, text="Hyperledger Fabric (Permissioned)", font=("Helvetica", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_plat_val.pack(anchor="w", pady=(0, 15))

        # Metrics Panel
        lbl_metrics_title = tk.Label(left_panel, text="Métricas del Sistema", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_metrics_title.pack(anchor="w", pady=(10, 8))

        # Card style stats
        self.lbl_processed = tk.Label(left_panel, text="Procesados: 0", font=("Helvetica", 9, "bold"), fg=self.colors["fg"], bg=self.colors["panel"])
        self.lbl_processed.pack(anchor="w", pady=2)

        self.lbl_conciliated = tk.Label(left_panel, text="Conciliadas: 0", font=("Helvetica", 9, "bold"), fg=self.colors["success"], bg=self.colors["panel"])
        self.lbl_conciliated.pack(anchor="w", pady=2)

        self.lbl_discrepancy = tk.Label(left_panel, text="Discrepancias: 0", font=("Helvetica", 9, "bold"), fg=self.colors["warning"], bg=self.colors["panel"])
        self.lbl_discrepancy.pack(anchor="w", pady=2)

        self.lbl_pending = tk.Label(left_panel, text="Pendientes: 0", font=("Helvetica", 9, "bold"), fg=self.colors["text_sec"], bg=self.colors["panel"])
        self.lbl_pending.pack(anchor="w", pady=2)

        # Count blockchain blocks
        self.lbl_blocks = tk.Label(left_panel, text="Bloques Blockchain: 0", font=("Helvetica", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        self.lbl_blocks.pack(anchor="w", pady=(2, 15))

        self.update_dashboard_metrics()

        # Action Buttons
        btn_demo = tk.Button(left_panel, text="CARGAR ARCHIVOS DEMO", font=("Helvetica", 9, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", pady=6, command=self.load_demo_files_action)
        btn_demo.pack(fill="x", pady=4)

        btn_imp_sales = tk.Button(left_panel, text="Importar Ventas (CSV/SIFEN)", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", pady=4, command=self.import_sales_action)
        btn_imp_sales.pack(fill="x", pady=4)

        btn_imp_bank = tk.Button(left_panel, text="Importar Banco (CSV/MT/XML)", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", pady=4, command=self.import_bank_action)
        btn_imp_bank.pack(fill="x", pady=4)

        btn_reconcile = tk.Button(left_panel, text="CONCILIAR Y GUARDAR", font=("Helvetica", 10, "bold"), bg=self.colors["success"], fg="#FFFFFF", relief="flat", pady=6, command=self.run_reconciliation_action)
        btn_reconcile.pack(fill="x", pady=(15, 4))

        btn_verify_l = tk.Button(left_panel, text="Verificar Integridad Ledger", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", pady=4, command=self.verify_ledger_action)
        btn_verify_l.pack(fill="x", pady=4)

        # Export buttons
        btn_exp_json = tk.Button(left_panel, text="Exportar JSON Completo", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", pady=3, command=self.export_json_action)
        btn_exp_json.pack(fill="x", pady=2)

        btn_exp_csv = tk.Button(left_panel, text="Exportar CSV de Resultados", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", pady=3, command=self.export_csv_action)
        btn_exp_csv.pack(fill="x", pady=2)

        # Export payload for Chaincode Fabric JSON
        btn_exp_fabric = tk.Button(left_panel, text="Exportar Payload Chaincode Fabric JSON", font=("Helvetica", 8, "italic"), bg=self.colors["panel"], fg=self.colors["accent"], activebackground=self.colors["accent"], activeforeground=self.colors["panel"], relief="groove", pady=3, command=self.export_fabric_payload_action)
        btn_exp_fabric.pack(fill="x", pady=(10, 2))

        # RIGHT COLUMN: Results tables
        right_panel = tk.Frame(tab, bg=self.colors["bg"])
        right_panel.grid(row=0, column=1, sticky="nsew")

        # Upper table: imported sales summary
        lbl_s_info = tk.Label(right_panel, text="Ventas Importadas (Sin conciliar)", font=("Helvetica", 10, "bold"), fg=self.colors["fg"], bg=self.colors["bg"])
        lbl_s_info.pack(anchor="w", pady=(0, 2))

        frame_table_sales = tk.Frame(right_panel)
        frame_table_sales.pack(fill="both", expand=True, pady=(0, 10))

        self.table_sales = ttk.Treeview(frame_table_sales, columns=("ref", "client", "date", "amount", "currency"), show="headings", height=6)
        self.table_sales.heading("ref", text="Referencia")
        self.table_sales.heading("client", text="Cliente")
        self.table_sales.heading("date", text="Fecha")
        self.table_sales.heading("amount", text="Monto")
        self.table_sales.heading("currency", text="Moneda")
        self.table_sales.pack(fill="both", expand=True, side="left")

        sb_sales = ttk.Scrollbar(frame_table_sales, orient="vertical", command=self.table_sales.yview)
        sb_sales.pack(fill="y", side="right")
        self.table_sales.configure(yscrollcommand=sb_sales.set)

        # Middle table: imported bank statements summary
        lbl_b_info = tk.Label(right_panel, text="Movimientos Bancarios Importados (Sin conciliar)", font=("Helvetica", 10, "bold"), fg=self.colors["fg"], bg=self.colors["bg"])
        lbl_b_info.pack(anchor="w", pady=(0, 2))

        frame_table_bank = tk.Frame(right_panel)
        frame_table_bank.pack(fill="both", expand=True, pady=(0, 10))

        self.table_bank = ttk.Treeview(frame_table_bank, columns=("ref", "desc", "date", "amount", "currency"), show="headings", height=6)
        self.table_bank.heading("ref", text="Referencia")
        self.table_bank.heading("desc", text="Descripción")
        self.table_bank.heading("date", text="Fecha")
        self.table_bank.heading("amount", text="Monto")
        self.table_bank.heading("currency", text="Moneda")
        self.table_bank.pack(fill="both", expand=True, side="left")

        sb_bank = ttk.Scrollbar(frame_table_bank, orient="vertical", command=self.table_bank.yview)
        sb_bank.pack(fill="y", side="right")
        self.table_bank.configure(yscrollcommand=sb_bank.set)

        # Lower table: Reconciliation outcomes
        lbl_r_info = tk.Label(right_panel, text="Resultados de la Corrida Activa", font=("Helvetica", 10, "bold"), fg=self.colors["accent"], bg=self.colors["bg"])
        lbl_r_info.pack(anchor="w", pady=(0, 2))

        frame_table_res = tk.Frame(right_panel)
        frame_table_res.pack(fill="both", expand=True)

        self.table_res = ttk.Treeview(frame_table_res, columns=("s_ref", "b_ref", "date", "amount_diff", "status"), show="headings", height=8)
        self.table_res.heading("s_ref", text="Venta Ref")
        self.table_res.heading("b_ref", text="Banco Ref")
        self.table_res.heading("date", text="Fecha")
        self.table_res.heading("amount_diff", text="Dif. Monto")
        self.table_res.heading("status", text="Estado")
        self.table_res.pack(fill="both", expand=True, side="left")

        sb_res = ttk.Scrollbar(frame_table_res, orient="vertical", command=self.table_res.yview)
        sb_res.pack(fill="y", side="right")
        self.table_res.configure(yscrollcommand=sb_res.set)

    def get_config_value(self, key: str, default: str) -> str:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key=?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row['value'] if row else default
        except Exception:
            return default

    def update_dashboard_metrics(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Count runs totals
            cursor.execute("SELECT SUM(sales_count + bank_count), SUM(conciliated_count), SUM(discrepancy_count), SUM(pending_count) FROM runs")
            r = cursor.fetchone()
            processed = r[0] or 0
            conciliated = r[1] or 0
            discrepancy = r[2] or 0
            pending = r[3] or 0

            # Count ledger blocks
            cursor.execute("SELECT COUNT(*) FROM ledger")
            blocks = cursor.fetchone()[0] or 0

            conn.close()

            self.lbl_processed.config(text=f"Procesados: {processed}")
            self.lbl_conciliated.config(text=f"Conciliadas: {conciliated}")
            self.lbl_discrepancy.config(text=f"Discrepancias: {discrepancy}")
            self.lbl_pending.config(text=f"Pendientes: {pending}")
            self.lbl_blocks.config(text=f"Bloques Blockchain: {blocks}")
        except Exception as e:
            print(f"Error fetching dashboard metrics: {e}")

    def load_demo_files_action(self):
        """Generates mock files in 'demo_files/' directory and loads them."""
        demo_dir = "demo_files"
        generate_all_demo_files(demo_dir)

        # Load automatically
        self.imported_sales = parse_sales_csv(os.path.join(demo_dir, "demo_sales.csv"))
        self.imported_bank = parse_bank_csv(os.path.join(demo_dir, "demo_bank_generic.csv"))

        self.refresh_imported_tables()
        log_audit_event(self.current_user['username'], "import", "Archivos de prueba demo cargados con éxito.")
        messagebox.showinfo("Demo Cargado", f"Se han generado y cargado las ventas y movimientos bancarios de prueba desde '{demo_dir}/'.")

    def refresh_imported_tables(self):
        # Clear
        for r in self.table_sales.get_children():
            self.table_sales.delete(r)
        for r in self.table_bank.get_children():
            self.table_bank.delete(r)

        for sale in self.imported_sales:
            self.table_sales.insert("", "end", values=(sale['referencia'], sale['cliente'], sale['fecha'], f"{sale['monto']:.2f}", sale['moneda']))

        for bank in self.imported_bank:
            self.table_bank.insert("", "end", values=(bank['referencia'], bank['descripcion'], bank['fecha'], f"{bank['monto']:.2f}", bank['moneda']))

    def import_sales_action(self):
        filetypes = [("Archivos Soportados", "*.csv;*.xml"), ("CSV Ventas", "*.csv"), ("SIFEN XML Paraguay", "*.xml")]
        filepath = filedialog.askopenfilename(title="Seleccionar Ventas", filetypes=filetypes)
        if not filepath:
            return

        try:
            if filepath.endswith('.csv'):
                self.imported_sales = parse_sales_csv(filepath)
            elif filepath.endswith('.xml'):
                self.imported_sales = parse_sifen_xml(filepath)
            else:
                raise ValueError("Formato de archivo no soportado.")

            self.refresh_imported_tables()
            log_audit_event(self.current_user['username'], "import", f"Ventas importadas desde: {os.path.basename(filepath)}")
            messagebox.showinfo("Importación", f"Se importaron {len(self.imported_sales)} registros de ventas con éxito.")
        except Exception as e:
            messagebox.showerror("Error de Importación", f"No se pudo importar las ventas: {e}")

    def import_bank_action(self):
        # Allow choosing bank format preset
        preset_win = tk.Toplevel(self.root)
        preset_win.title("Seleccionar Banco y Formato")
        preset_win.geometry("380x250")
        preset_win.transient(self.root)
        preset_win.grab_set()
        preset_win.configure(bg=self.colors["panel"])

        lbl = tk.Label(preset_win, text="Seleccione el preset o formato bancario:", font=("Helvetica", 10, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl.pack(pady=15)

        preset_var = tk.StringVar(value="Generic")
        presets = ["Generic", "Banco Familiar", "Banco Continental", "Banco Itaú", "Banco Basa", "MT940 (.txt)", "CAMT.053 (.xml)"]
        cb = ttk.Combobox(preset_win, textvariable=preset_var, values=presets, state="readonly", width=25)
        cb.pack(pady=10)

        def select_file_and_import():
            preset = preset_var.get()
            preset_win.destroy()

            if preset == "MT940 (.txt)":
                filetypes = [("MT940 Text", "*.txt")]
            elif preset == "CAMT.053 (.xml)":
                filetypes = [("CAMT.053 XML", "*.xml")]
            else:
                filetypes = [("CSV Bank Statements", "*.csv")]

            filepath = filedialog.askopenfilename(title="Seleccionar Movimientos Bancarios", filetypes=filetypes)
            if not filepath:
                return

            try:
                if preset == "MT940 (.txt)":
                    self.imported_bank = parse_mt940(filepath)
                elif preset == "CAMT.053 (.xml)":
                    self.imported_bank = parse_camt053(filepath)
                else:
                    self.imported_bank = parse_bank_csv(filepath, preset=preset)

                self.refresh_imported_tables()
                log_audit_event(self.current_user['username'], "import", f"Movimientos bancarios importados ({preset}) desde: {os.path.basename(filepath)}")
                messagebox.showinfo("Importación Bancaria", f"Se importaron {len(self.imported_bank)} movimientos bancarios con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron importar los movimientos bancarios: {e}")

        btn = tk.Button(preset_win, text="SELECCIONAR ARCHIVO", font=("Helvetica", 9, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", padx=10, pady=5, command=select_file_and_import)
        btn.pack(pady=20)

    def run_reconciliation_action(self):
        """Runs matching engine, generates blockchain ledger evidence and saves metadata."""
        if not self.imported_sales and not self.imported_bank:
            messagebox.showwarning("Sin Datos", "Debe importar ventas o movimientos bancarios antes de conciliar.")
            return

        try:
            t_days = int(self.ent_t_days.get().strip())
            t_amt = float(self.ent_t_amt.get().strip())
        except ValueError:
            messagebox.showerror("Configuración Inválida", "Los valores de fecha y monto de tolerancia deben ser numéricos.")
            return

        # Save settings
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('tolerance_days', ?)", (str(t_days),))
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('tolerance_amount', ?)", (str(t_amt),))
            conn.commit()
            conn.close()
        except Exception:
            pass

        # Perform reconciliation
        self.active_run_results = reconcile_lists(self.imported_sales, self.imported_bank, tolerance_days=t_days, tolerance_amount=t_amt)

        # Format code CONC-YYYYMMDD-HHMMSS
        run_code = f"CONC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Save run in DB & Ledger
        actor = self.current_user['username']
        success, msg = save_reconciliation_run(run_code, actor, self.active_run_results, t_days, t_amt)

        if success:
            log_audit_event(actor, "reconciliation", f"Conciliación guardada {run_code}. Bloque blockchain generado.")
            self.update_dashboard_metrics()

            # Populate results table
            for r in self.table_res.get_children():
                self.table_res.delete(r)

            for res in self.active_run_results:
                self.table_res.insert("", "end", values=(
                    res['sale_ref'] or "PENDIENTE",
                    res['bank_ref'] or "PENDIENTE",
                    res['sale_date'] or res['bank_date'],
                    f"{res['difference']:.2f}",
                    res['status'].upper()
                ))

            # Pop visual success
            messagebox.showinfo("Conciliación Completada", f"Código de Corrida: {run_code}\n\n{msg}")

            # Clean imported memory
            self.imported_sales = []
            self.imported_bank = []
            self.refresh_imported_tables()
        else:
            messagebox.showerror("Error", msg)

    def verify_ledger_action(self):
        is_valid, msg = verify_ledger_integrity()
        log_audit_event(self.current_user['username'], "verification", f"Verificación de ledger: {msg}")
        if is_valid:
            messagebox.showinfo("Verificación Ledger", msg)
        else:
            messagebox.showerror("Error de Integridad", msg)

    def export_json_action(self):
        """Exports complete JSON with app metadata, licence, runs, results and ledger."""
        if not self.active_run_results:
            messagebox.showwarning("Sin Datos", "Debe correr una conciliación para poder exportar resultados activos.")
            return

        filepath = filedialog.asksaveasfilename(title="Guardar Reporte JSON", filetypes=[("JSON Files", "*.json")], defaultextension=".json")
        if not filepath:
            return

        try:
            lic = get_active_license() or {}

            report = {
                "app": "ConciliaPyme Ledger Pro",
                "version": "2.3.0",
                "export_timestamp": datetime.now().isoformat(),
                "exporter_user": self.current_user['username'],
                "empresa": {
                    "nombre": lic.get('company_name', 'No Configurada'),
                    "RUC": lic.get('ruc', 'N/A'),
                    "sucursal": lic.get('branch', 'N/A')
                },
                "reglas": {
                    "tolerance_days": self.ent_t_days.get().strip(),
                    "tolerance_amount": self.ent_t_amt.get().strip()
                },
                "resultados": self.active_run_results
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            log_audit_event(self.current_user['username'], "export", f"Reporte JSON exportado a: {os.path.basename(filepath)}")
            messagebox.showinfo("Exportación JSON", "Reporte completo exportado con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al exportar reporte JSON: {e}")

    def export_csv_action(self):
        if not self.active_run_results:
            messagebox.showwarning("Sin Datos", "Debe correr una conciliación para poder exportar resultados activos.")
            return

        filepath = filedialog.asksaveasfilename(title="Guardar Reporte CSV", filetypes=[("CSV Files", "*.csv")], defaultextension=".csv")
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Venta Ref", "Cliente", "Fecha Venta", "Monto Venta", "Moneda Venta", "Banco Ref", "Detalle Banco", "Fecha Banco", "Monto Banco", "Estado", "Diferencia"])
                for r in self.active_run_results:
                    writer.writerow([
                        r['sale_ref'], r['sale_client'], r['sale_date'], r['sale_amount'], r['sale_currency'],
                        r['bank_ref'], r['bank_desc'], r['bank_date'], r['bank_amount'], r['status'], r['difference']
                    ])
            log_audit_event(self.current_user['username'], "export", f"Reporte CSV exportado a: {os.path.basename(filepath)}")
            messagebox.showinfo("Exportación CSV", "Resultados de corrida exportados con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al exportar CSV: {e}")

    def export_fabric_payload_action(self):
        """Generates Hyperledger Fabric JSON payload matching Go chaincode format."""
        if not self.active_run_results:
            messagebox.showwarning("Sin Datos", "Debe correr una conciliación para generar el payload del chaincode.")
            return

        filepath = filedialog.asksaveasfilename(title="Guardar Payload Fabric JSON", filetypes=[("JSON Files", "*.json")], defaultextension=".json")
        if not filepath:
            return

        try:
            # Match Go chaincode structure: Index, Timestamp, Actor, Node, Platform, TxHash, PrevHash, BlockHash, Status
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ledger ORDER BY block_index DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()

            if not row:
                messagebox.showerror("Error", "No se encontraron bloques de ledger.")
                return

            payload = {
                "id": f"EVID-{row['block_index']}",
                "timestamp": row['timestamp'],
                "actor": row['actor'],
                "node": row['node'],
                "platform": row['platform'],
                "txHash": row['tx_hash'],
                "prevHash": row['prev_hash'],
                "blockHash": row['block_hash'],
                "status": row['status']
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)

            log_audit_event(self.current_user['username'], "export", f"Payload Fabric JSON exportado a: {os.path.basename(filepath)}")
            messagebox.showinfo("Exportación Fabric", "Payload de Hyperledger Fabric generado con éxito.\nListo para invocar chaincode.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el payload Fabric: {e}")


    # ------------------ COTIZACION TAB ------------------
    def create_cotizacion_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Cotización USD/PYG ")

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        # Left side: sources display
        left_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        left_f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_title = tk.Label(left_f, text="Cotizaciones de Plaza", font=("Helvetica", 12, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_title.pack(anchor="w", pady=(0, 10))

        self.table_rates = ttk.Treeview(left_f, columns=("source", "buy", "sell", "updated"), show="headings", height=8)
        self.table_rates.heading("source", text="Fuente")
        self.table_rates.heading("buy", text="Compra (PYG)")
        self.table_rates.heading("sell", text="Venta (PYG)")
        self.table_rates.heading("updated", text="Actualización")
        self.table_rates.pack(fill="both", expand=True, pady=(0, 10))

        # Populating rates from cache initially
        self.refresh_rates_table()

        btn_update_r = tk.Button(left_f, text="ACTUALIZAR COTIZACIONES ONLINE", font=("Helvetica", 9, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", command=self.update_online_rates_action)
        btn_update_r.pack(fill="x")

        # Right side: Conversor
        right_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        right_f.grid(row=0, column=1, sticky="nsew")

        lbl_c_title = tk.Label(right_f, text="Conversor Arbitraje", font=("Helvetica", 12, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_c_title.pack(anchor="w", pady=(0, 15))

        lbl_source = tk.Label(right_f, text="Fuente de Cambio:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_source.pack(anchor="w")
        self.source_var = tk.StringVar()
        self.cb_sources = ttk.Combobox(right_f, textvariable=self.source_var, state="readonly")
        self.cb_sources.pack(fill="x", pady=(2, 12))

        lbl_direction = tk.Label(right_f, text="Dirección de Conversión:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_direction.pack(anchor="w")
        self.dir_var = tk.StringVar(value="USD a PYG")
        cb_dir = ttk.Combobox(right_f, textvariable=self.dir_var, values=["USD a PYG", "PYG a USD"], state="readonly")
        cb_dir.pack(fill="x", pady=(2, 12))

        lbl_amt = tk.Label(right_f, text="Monto a Convertir:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_amt.pack(anchor="w")
        self.ent_conv_amt = tk.Entry(right_f, font=("Helvetica", 11), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_conv_amt.pack(fill="x", pady=(2, 15))

        self.lbl_conv_result = tk.Label(right_f, text="Resultado: -", font=("Helvetica", 14, "bold"), fg=self.colors["success"], bg=self.colors["panel"])
        self.lbl_conv_result.pack(pady=15)

        btn_conv = tk.Button(right_f, text="CONVERTIR MONEDA", font=("Helvetica", 10, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", pady=6, command=self.perform_conversion_action)
        btn_conv.pack(fill="x")

        self.populate_sources_combo()

    def refresh_rates_table(self):
        for r in self.table_rates.get_children():
            self.table_rates.delete(r)

        quotes = read_cached_quotes()
        for src, val in quotes.items():
            self.table_rates.insert("", "end", values=(src.upper(), f"{val['compra']:.1f}", f"{val['venta']:.1f}", val['updated_at']))

    def populate_sources_combo(self):
        quotes = read_cached_quotes()
        lst = list(quotes.keys())
        self.cb_sources['values'] = lst
        if lst:
            self.cb_sources.current(0)

    def update_online_rates_action(self):
        _, msg = fetch_and_cache_quotes()
        self.refresh_rates_table()
        self.populate_sources_combo()
        log_audit_event(self.current_user['username'], "sync", "Cotización de USD/PYG actualizada desde API.")
        messagebox.showinfo("Actualización Cotización", msg)

    def perform_conversion_action(self):
        try:
            amt = float(self.ent_conv_amt.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido.")
            return

        src = self.source_var.get()
        direction = self.dir_var.get()

        if direction == "USD a PYG":
            res = convert_usd_to_pyg(amt, src)
            self.lbl_conv_result.config(text=f"Resultado: {res:,.0f} PYG")
        else:
            res = convert_pyg_to_usd(amt, src)
            self.lbl_conv_result.config(text=f"Resultado: {res:,.2f} USD")


    # ------------------ HISTORY TAB ------------------
    def create_history_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Historial de Corridas ")

        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        h_frame = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        h_frame.grid(row=0, column=0, sticky="nsew")

        lbl_title = tk.Label(h_frame, text="Corridas de Conciliación Anteriores", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_title.pack(anchor="w", pady=(0, 10))

        # Table of history runs
        self.table_hist = ttk.Treeview(h_frame, columns=("code", "timestamp", "actor", "sales", "bank", "con", "disc", "pend"), show="headings", height=12)
        self.table_hist.heading("code", text="Código")
        self.table_hist.heading("timestamp", text="Fecha Ejecución")
        self.table_hist.heading("actor", text="Usuario")
        self.table_hist.heading("sales", text="Ventas")
        self.table_hist.heading("bank", text="Banco")
        self.table_hist.heading("con", text="Concil.")
        self.table_hist.heading("disc", text="Discrep.")
        self.table_hist.heading("pend", text="Pend.")
        self.table_hist.pack(fill="both", expand=True, pady=(0, 15))

        self.refresh_history_table()

        btn_load = tk.Button(h_frame, text="CARGAR CORRIDA SELECCIONADA EN DASHBOARD", font=("Helvetica", 9, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", pady=6, command=self.load_history_run_action)
        btn_load.pack(fill="x")

    def refresh_history_table(self):
        for r in self.table_hist.get_children():
            self.table_hist.delete(r)

        runs = get_all_runs()
        for run in runs:
            self.table_hist.insert("", "end", values=(
                run['code'], run['timestamp'], run['actor'], run['sales_count'], run['bank_count'],
                run['conciliated_count'], run['discrepancy_count'], run['pending_count']
            ))

    def load_history_run_action(self):
        selected = self.table_hist.selection()
        if not selected:
            messagebox.showwarning("Seleccionar", "Por favor seleccione una corrida del historial.")
            return

        item = self.table_hist.item(selected[0])
        run_code = item['values'][0]

        run_dict, results = load_reconciliation_run(run_code)
        if run_dict:
            # Load back to Dashboard active results
            self.active_run_results = results

            # Show in results table in Dashboard
            for r in self.table_res.get_children():
                self.table_res.delete(r)

            for res in results:
                self.table_res.insert("", "end", values=(
                    res['sale_ref'] or "PENDIENTE",
                    res['bank_ref'] or "PENDIENTE",
                    res['sale_date'] or res['bank_date'],
                    f"{res['difference']:.2f}",
                    res['status'].upper()
                ))

            # Update configuration widgets to reflect historic limits if any
            self.ent_t_days.delete(0, "end")
            self.ent_t_days.insert(0, str(run_dict['rule_date_tolerance']))
            self.ent_t_amt.delete(0, "end")
            self.ent_t_amt.insert(0, f"{run_dict['rule_amount_tolerance']:.2f}")

            log_audit_event(self.current_user['username'], "verification", f"Carga de corrida histórica: {run_code}")
            messagebox.showinfo("Carga Completada", f"Se ha cargado la corrida {run_code} en la vista del Dashboard.")

            # Navigate to Dashboard tab
            self.notebook.select(0)
        else:
            messagebox.showerror("Error", "No se pudo cargar la corrida.")


    # ------------------ AUDIT TAB ------------------
    def create_audit_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Auditoría ")

        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        a_frame = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        a_frame.grid(row=0, column=0, sticky="nsew")

        top_bar = tk.Frame(a_frame, bg=self.colors["panel"])
        top_bar.pack(fill="x", pady=(0, 10))

        lbl_title = tk.Label(top_bar, text="Bitácora de Eventos de Auditoría (Encadenada)", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_title.pack(side="left")

        btn_verify = tk.Button(top_bar, text="Verificar Integridad de Bitácora", font=("Helvetica", 9, "bold"), bg=self.colors["success"], fg="#FFFFFF", relief="flat", command=self.verify_audit_action)
        btn_verify.pack(side="right")

        # Table of audit logs
        self.table_audit = ttk.Treeview(a_frame, columns=("timestamp", "actor", "event", "desc"), show="headings", height=12)
        self.table_audit.heading("timestamp", text="Fecha y Hora")
        self.table_audit.heading("actor", text="Actor")
        self.table_audit.heading("event", text="Evento")
        self.table_audit.heading("desc", text="Descripción")
        self.table_audit.pack(fill="both", expand=True)

        self.refresh_audit_table()

    def refresh_audit_table(self):
        for r in self.table_audit.get_children():
            self.table_audit.delete(r)

        logs = get_all_audit_logs()
        for log in logs:
            self.table_audit.insert("", "end", values=(
                log['timestamp'], log['actor'], log['event_type'].upper(), log['description']
            ))

    def verify_audit_action(self):
        is_valid, msg, errors = verify_audit_trail_integrity()
        log_audit_event(self.current_user['username'], "verification", f"Verificación de integridad de auditoría: {msg}")
        self.refresh_audit_table()

        if is_valid:
            messagebox.showinfo("Verificación de Auditoría", msg)
        else:
            err_msg = "\n".join([f"ID: {e['id']} - {e['error']}" for e in errors[:5]])
            messagebox.showerror("Fallo de Integridad", f"{msg}\n\nErrores de eslabón detectados:\n{err_msg}")


    # ------------------ USERS TAB (ADMIN ONLY) ------------------
    def create_users_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Administrar Usuarios ")

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        # Left Panel: Create and Edit Users
        left_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        left_f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_create = tk.Label(left_f, text="Crear / Modificar Usuario", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_create.pack(anchor="w", pady=(0, 15))

        lbl_username = tk.Label(left_f, text="Usuario:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_username.pack(anchor="w")
        self.ent_user_edit = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_user_edit.pack(fill="x", pady=(2, 12))

        lbl_pass = tk.Label(left_f, text="Contraseña (Política Fuerte):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_pass.pack(anchor="w")
        self.ent_pass_edit = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_pass_edit.pack(fill="x", pady=(2, 12))

        lbl_role = tk.Label(left_f, text="Rol:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_role.pack(anchor="w")
        self.role_var = tk.StringVar(value="contador")
        cb_roles = ttk.Combobox(left_f, textvariable=self.role_var, values=["admin", "contador", "gerente", "auditor"], state="readonly")
        cb_roles.pack(fill="x", pady=(2, 12))

        lbl_active = tk.Label(left_f, text="Estado:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_active.pack(anchor="w")
        self.active_var = tk.IntVar(value=1)
        chk_active = tk.Checkbutton(left_f, text="Usuario Activo", variable=self.active_var, fg=self.colors["fg"], bg=self.colors["panel"], activebackground=self.colors["panel"], activeforeground=self.colors["fg"])
        chk_active.pack(anchor="w", pady=(2, 15))

        btn_register = tk.Button(left_f, text="REGISTRAR NUEVO USUARIO", font=("Helvetica", 9, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", command=self.create_user_action)
        btn_register.pack(fill="x", pady=4)

        btn_update = tk.Button(left_f, text="ACTUALIZAR ROL & ESTADO", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", command=self.update_user_action)
        btn_update.pack(fill="x", pady=4)

        btn_ch_pass = tk.Button(left_f, text="Cambiar Contraseña de Usuario", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", command=self.change_user_password_action)
        btn_ch_pass.pack(fill="x", pady=4)

        btn_reset_admin = tk.Button(left_f, text="Resetear Admin a Valor por Defecto", font=("Helvetica", 8, "italic"), bg=self.colors["panel"], fg=self.colors["warning"], relief="groove", command=self.reset_admin_action)
        btn_reset_admin.pack(fill="x", pady=(15, 0))

        # Right Panel: Users List
        right_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        right_f.grid(row=0, column=1, sticky="nsew")

        lbl_title_list = tk.Label(right_f, text="Lista de Usuarios", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_title_list.pack(anchor="w", pady=(0, 15))

        self.table_users = ttk.Treeview(right_f, columns=("username", "role", "active"), show="headings", height=10)
        self.table_users.heading("username", text="Usuario")
        self.table_users.heading("role", text="Rol")
        self.table_users.heading("active", text="Activo")
        self.table_users.pack(fill="both", expand=True)
        self.table_users.bind("<<TreeviewSelect>>", self.on_user_selected)

        self.refresh_users_table()

    def refresh_users_table(self):
        for r in self.table_users.get_children():
            self.table_users.delete(r)

        users = get_all_users()
        for u in users:
            self.table_users.insert("", "end", values=(u['username'], u['role'].upper(), "SÍ" if u['active'] else "NO"))

    def on_user_selected(self, event):
        selected = self.table_users.selection()
        if selected:
            item = self.table_users.item(selected[0])
            username = item['values'][0]
            role = item['values'][1].lower()
            active = 1 if item['values'][2] == "SÍ" else 0

            self.ent_user_edit.delete(0, "end")
            self.ent_user_edit.insert(0, username)
            self.role_var.set(role)
            self.active_var.set(active)

    def create_user_action(self):
        u = self.ent_user_edit.get().strip()
        p = self.ent_pass_edit.get()
        role = self.role_var.get()
        active = self.active_var.get()

        success, msg = register_user(u, p, role, active)
        if success:
            log_audit_event(self.current_user['username'], "user_change", f"Registró usuario {u} con rol {role}.")
            self.refresh_users_table()
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def update_user_action(self):
        u = self.ent_user_edit.get().strip()
        role = self.role_var.get()
        active = self.active_var.get()

        success, msg = edit_user_role_and_status(u, role, active)
        if success:
            log_audit_event(self.current_user['username'], "user_change", f"Actualizó usuario {u}: rol {role}, activo {active}.")
            self.refresh_users_table()
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def change_user_password_action(self):
        u = self.ent_user_edit.get().strip()
        p = self.ent_pass_edit.get()

        success, msg = change_user_password(u, p)
        if success:
            log_audit_event(self.current_user['username'], "user_change", f"Cambió contraseña de usuario {u}.")
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def reset_admin_action(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea restablecer el usuario admin a su estado por defecto?"):
            success, msg = reset_admin_password()
            if success:
                log_audit_event(self.current_user['username'], "user_change", "Reseteó contraseña de administrador.")
                self.refresh_users_table()
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)


    # ------------------ LICENSE TAB (ADMIN ONLY) ------------------
    def create_license_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Licencia & Empresa ")

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        # Left Panel: Activate License
        left_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        left_f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_title = tk.Label(left_f, text="Activar Licencia Comercial", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_title.pack(anchor="w", pady=(0, 15))

        lbl_cname = tk.Label(left_f, text="Nombre de Empresa / Titular:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_cname.pack(anchor="w")
        self.ent_lic_cname = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_lic_cname.pack(fill="x", pady=(2, 10))

        lbl_ruc = tk.Label(left_f, text="RUC de Empresa (Paraguay):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_ruc.pack(anchor="w")
        self.ent_lic_ruc = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_lic_ruc.pack(fill="x", pady=(2, 10))

        lbl_branch = tk.Label(left_f, text="Sucursal:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_branch.pack(anchor="w")
        self.ent_lic_branch = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_lic_branch.pack(fill="x", pady=(2, 10))
        self.ent_lic_branch.insert(0, "Casa Central")

        lbl_exp = tk.Label(left_f, text="Vencimiento (YYYY-MM-DD):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_exp.pack(anchor="w")
        self.ent_lic_exp = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_lic_exp.pack(fill="x", pady=(2, 10))
        self.ent_lic_exp.insert(0, "2027-12-31")

        lbl_type = tk.Label(left_f, text="Tipo de Licencia:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_type.pack(anchor="w")
        self.lic_type_var = tk.StringVar(value="full")
        cb_type = ttk.Combobox(left_f, textvariable=self.lic_type_var, values=["demo", "full"], state="readonly")
        cb_type.pack(fill="x", pady=(2, 12))

        lbl_key = tk.Label(left_f, text="Clave de Activación (Firma HMAC):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_key.pack(anchor="w")
        self.ent_lic_key = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_lic_key.pack(fill="x", pady=(2, 15))

        btn_save = tk.Button(left_f, text="ACTIVAR Y GUARDAR LICENCIA", font=("Helvetica", 9, "bold"), bg=self.colors["success"], fg="#FFFFFF", relief="flat", command=self.activate_license_action)
        btn_save.pack(fill="x", pady=4)

        btn_demo_lic = tk.Button(left_f, text="Generar y Auto-Activar Licencia Demo (30 Días)", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", command=self.generate_demo_license_action)
        btn_demo_lic.pack(fill="x", pady=4)

        # Right Panel: Active Status
        right_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        right_f.grid(row=0, column=1, sticky="nsew")

        lbl_title_status = tk.Label(right_f, text="Estado de Licencia Activa", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_title_status.pack(anchor="w", pady=(0, 20))

        self.lbl_active_ruc = tk.Label(right_f, text="RUC de Empresa: N/A", font=("Helvetica", 10, "bold"), fg=self.colors["fg"], bg=self.colors["panel"])
        self.lbl_active_ruc.pack(anchor="w", pady=5)

        self.lbl_active_cname = tk.Label(right_f, text="Empresa: Sin registrar", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"])
        self.lbl_active_cname.pack(anchor="w", pady=5)

        self.lbl_active_branch = tk.Label(right_f, text="Sucursal: Casa Central", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"])
        self.lbl_active_branch.pack(anchor="w", pady=5)

        self.lbl_active_expires = tk.Label(right_f, text="Vence el: N/A", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"])
        self.lbl_active_expires.pack(anchor="w", pady=5)

        self.lbl_active_type = tk.Label(right_f, text="Tipo: N/A", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"])
        self.lbl_active_type.pack(anchor="w", pady=5)

        self.lbl_active_status = tk.Label(right_f, text="Estado de Validación: SIN LICENCIA ACTIVA", font=("Helvetica", 11, "bold"), fg=self.colors["warning"], bg=self.colors["panel"])
        self.lbl_active_status.pack(anchor="w", pady=(20, 5))

        self.refresh_active_license_status()

    def refresh_active_license_status(self):
        lic = get_active_license()
        if lic:
            self.lbl_active_ruc.config(text=f"RUC de Empresa: {lic['ruc']}")
            self.lbl_active_cname.config(text=f"Empresa: {lic['company_name']}")
            self.lbl_active_branch.config(text=f"Sucursal: {lic['branch']}")
            self.lbl_active_expires.config(text=f"Vence el: {lic['expires_at']}")
            self.lbl_active_type.config(text=f"Tipo: {lic['license_type'].upper()}")

            if lic['is_valid']:
                self.lbl_active_status.config(text="Estado de Validación: LICENCIA ACTIVA Y VÁLIDA ✅", fg=self.colors["success"])
            else:
                self.lbl_active_status.config(text=f"Estado de Validación: {lic['validation_message'].upper()} ❌", fg="red")
        else:
            self.lbl_active_ruc.config(text="RUC de Empresa: N/A")
            self.lbl_active_cname.config(text="Empresa: Sin registrar")
            self.lbl_active_branch.config(text="Sucursal: Casa Central")
            self.lbl_active_expires.config(text="Vence el: N/A")
            self.lbl_active_type.config(text="Tipo: N/A")
            self.lbl_active_status.config(text="Estado de Validación: SIN LICENCIA ACTIVA ⚠️", fg=self.colors["warning"])

    def activate_license_action(self):
        cname = self.ent_lic_cname.get().strip()
        ruc = self.ent_lic_ruc.get().strip()
        branch = self.ent_lic_branch.get().strip()
        exp = self.ent_lic_exp.get().strip()
        lic_type = self.lic_type_var.get()
        key = self.ent_lic_key.get().strip()

        if not cname or not ruc or not exp or not key:
            messagebox.showwarning("Campos vacíos", "Todos los campos obligatorios deben completarse.")
            return

        success, msg = save_license(ruc, cname, branch, exp, lic_type, key)
        if success:
            log_audit_event(self.current_user['username'], "user_change", f"Licencia activada con éxito para RUC {ruc}.")
            self.refresh_active_license_status()
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def generate_demo_license_action(self):
        demo = generate_demo_license()
        success, msg = save_license(
            demo['ruc'], demo['company_name'], demo['branch'], demo['expires_at'], demo['license_type'], demo['license_key']
        )
        if success:
            log_audit_event(self.current_user['username'], "user_change", "Licencia demo auto-generada y activada con éxito.")
            self.refresh_active_license_status()
            messagebox.showinfo("Demo Activado", f"Licencia Demo de 30 Días activada para {demo['company_name']} RUC {demo['ruc']}.\nClave: {demo['license_key']}")
        else:
            messagebox.showerror("Error", msg)


    # ------------------ LAN SYNC TAB (ADMIN ONLY) ------------------
    def create_sync_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Sincronización LAN ")

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

        # Left Panel: Server Control
        left_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        left_f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        lbl_server = tk.Label(left_f, text="Servidor HTTP Local opcional (LAN)", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_server.pack(anchor="w", pady=(0, 15))

        lbl_port = tk.Label(left_f, text="Puerto del Servidor:", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_port.pack(anchor="w")
        self.ent_sync_port = tk.Entry(left_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_sync_port.pack(fill="x", pady=(2, 12))
        self.ent_sync_port.insert(0, "8080")

        self.lbl_server_status = tk.Label(left_f, text="Estado: DETENIDO ❌", font=("Helvetica", 10, "bold"), fg="red", bg=self.colors["panel"])
        self.lbl_server_status.pack(anchor="w", pady=15)

        btn_start = tk.Button(left_f, text="INICIAR SERVIDOR LAN", font=("Helvetica", 9, "bold"), bg=self.colors["success"], fg="#FFFFFF", relief="flat", command=self.start_sync_server_action)
        btn_start.pack(fill="x", pady=4)

        btn_stop = tk.Button(left_f, text="DETENER SERVIDOR", font=("Helvetica", 9), bg=self.colors["bg"], fg=self.colors["fg"], relief="groove", command=self.stop_sync_server_action)
        btn_stop.pack(fill="x", pady=4)

        # Right Panel: Client Sync Import
        right_f = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=15, pady=15)
        right_f.grid(row=0, column=1, sticky="nsew")

        lbl_client = tk.Label(right_f, text="Importar Snapshot Remoto", font=("Helvetica", 11, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_client.pack(anchor="w", pady=(0, 15))

        lbl_url = tk.Label(right_f, text="URL del Snapshot Remoto (/snapshot):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_url.pack(anchor="w")
        self.ent_sync_url = tk.Entry(right_f, font=("Helvetica", 10), bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_sync_url.pack(fill="x", pady=(2, 12))
        self.ent_sync_url.insert(0, "http://localhost:8080/snapshot")

        btn_sync = tk.Button(right_f, text="SINCRONIZAR E IMPORTAR DATOS", font=("Helvetica", 10, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", pady=6, command=self.import_sync_snapshot_action)
        btn_sync.pack(fill="x", pady=15)

        lbl_help = tk.Label(right_f, text="Nota: No reemplaza datos existentes. Inserta únicamente corridas nuevas por su código único de conciliación.", font=("Helvetica", 9, "italic"), fg=self.colors["text_sec"], bg=self.colors["panel"], wraplength=350, justify="left")
        lbl_help.pack(anchor="w")

    def start_sync_server_action(self):
        try:
            port = int(self.ent_sync_port.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El puerto debe ser numérico.")
            return

        if self.sync_server:
            self.sync_server.stop()

        self.sync_server = LANSyncServer(port=port)
        try:
            self.sync_server.start()
            self.lbl_server_status.config(text=f"Estado: ACTIVO en puerto {port} ✅", fg=self.colors["success"])
            log_audit_event(self.current_user['username'], "sync", f"Servidor LAN HTTP iniciado en puerto {port}.")
            messagebox.showinfo("Sincronización LAN", f"Servidor LAN activo en puerto {port}. Endpoint /snapshot disponible.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el servidor: {e}")

    def stop_sync_server_action(self):
        if self.sync_server:
            self.sync_server.stop()
            self.sync_server = None
            self.lbl_server_status.config(text="Estado: DETENIDO ❌", fg="red")
            log_audit_event(self.current_user['username'], "sync", "Servidor LAN HTTP detenido.")
            messagebox.showinfo("Servidor Detenido", "Servidor LAN detenido correctamente.")
        else:
            messagebox.showwarning("Servidor", "El servidor no está en ejecución.")

    def import_sync_snapshot_action(self):
        url = self.ent_sync_url.get().strip()
        if not url:
            messagebox.showwarning("Error", "Ingrese la URL remota.")
            return

        success, msg = import_snapshot_from_url(url)
        if success:
            log_audit_event(self.current_user['username'], "sync", f"Sincronización exitosa desde snapshot: {url}")
            self.update_dashboard_metrics()
            self.refresh_history_table()
            self.refresh_audit_table()
            messagebox.showinfo("Éxito de Sincronización", msg)
        else:
            messagebox.showerror("Error de Sincronización", msg)


    # ------------------ BACKUP TAB (ADMIN ONLY) ------------------
    def create_backup_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Backups Cifrados ")

        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        b_frame = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=20, pady=20)
        b_frame.grid(row=0, column=0, sticky="nsew")

        lbl_b_title = tk.Label(b_frame, text="Copia de Seguridad Cifrada de SQLite", font=("Helvetica", 12, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_b_title.pack(anchor="w", pady=(0, 20))

        lbl_pass = tk.Label(b_frame, text="Clave de Cifrado (Requerida para crear y restaurar):", font=("Helvetica", 9), fg=self.colors["fg"], bg=self.colors["panel"])
        lbl_pass.pack(anchor="w")
        self.ent_bk_pass = tk.Entry(b_frame, font=("Helvetica", 11), show="*", bg=self.colors["bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        self.ent_bk_pass.pack(fill="x", pady=(2, 20))

        btn_create_bk = tk.Button(b_frame, text="CREAR RESPALDO CIFRADO (.cplybak)", font=("Helvetica", 10, "bold"), bg=self.colors["accent"], fg=self.colors["bg"], relief="flat", pady=8, command=self.create_backup_action)
        btn_create_bk.pack(fill="x", pady=6)

        btn_restore_bk = tk.Button(b_frame, text="RESTAURAR DESDE RESPALDO CIFRADO", font=("Helvetica", 10, "bold"), bg=self.colors["warning"], fg="#FFFFFF", relief="flat", pady=8, command=self.restore_backup_action)
        btn_restore_bk.pack(fill="x", pady=6)

    def create_backup_action(self):
        pw = self.ent_bk_pass.get()
        if not pw:
            messagebox.showwarning("Error", "Debe ingresar una clave de cifrado para el respaldo.")
            return

        filepath = filedialog.asksaveasfilename(title="Guardar Respaldo Cifrado", filetypes=[("Respaldo ConciliaPyme", "*.cplybak")], defaultextension=".cplybak")
        if not filepath:
            return

        success, msg = create_encrypted_backup(DB_FILE, filepath, pw)
        if success:
            log_audit_event(self.current_user['username'], "backup", f"Copia de seguridad cifrada creada: {os.path.basename(filepath)}")
            messagebox.showinfo("Copia de Seguridad", msg)
        else:
            messagebox.showerror("Error", msg)

    def restore_backup_action(self):
        pw = self.ent_bk_pass.get()
        if not pw:
            messagebox.showwarning("Error", "Debe ingresar la clave de cifrado para restaurar.")
            return

        filepath = filedialog.askopenfilename(title="Seleccionar Respaldo Cifrado", filetypes=[("Respaldo ConciliaPyme", "*.cplybak")])
        if not filepath:
            return

        if messagebox.askyesno("Confirmar Restauración", "⚠️ ADVERTENCIA: Se sobrescribirá la base de datos local actual con el respaldo. ¿Desea continuar?"):
            success, msg = restore_encrypted_backup(filepath, DB_FILE, pw)
            if success:
                # Log audit event in newly restored database
                log_audit_event(self.current_user['username'], "backup", f"Base de datos restaurada desde: {os.path.basename(filepath)}")
                self.update_dashboard_metrics()
                self.refresh_history_table()
                self.refresh_audit_table()
                if self.current_user['role'] == 'admin':
                    self.refresh_users_table()
                    self.refresh_active_license_status()
                messagebox.showinfo("Copia de Seguridad", msg)
            else:
                messagebox.showerror("Error de Restauración", msg)


    # ------------------ THEMES TAB ------------------
    def create_themes_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Apariencia / Temas ")

        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        t_frame = tk.Frame(tab, bg=self.colors["panel"], highlightbackground=self.colors["border"], highlightthickness=1, padx=20, pady=20)
        t_frame.grid(row=0, column=0, sticky="nsew")

        lbl_t_title = tk.Label(t_frame, text="Selector de Tema Visual", font=("Helvetica", 12, "bold"), fg=self.colors["accent"], bg=self.colors["panel"])
        lbl_t_title.pack(anchor="w", pady=(0, 20))

        theme_var = tk.StringVar(value=self.theme_name)

        def on_theme_change():
            self.save_theme_preference(theme_var.get())

        r_sys = tk.Radiobutton(t_frame, text="Tema del Sistema (Windows Preference)", variable=theme_var, value="Sistema", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"], activebackground=self.colors["panel"], activeforeground=self.colors["fg"], selectcolor=self.colors["panel"], command=on_theme_change)
        r_sys.pack(anchor="w", pady=6)

        r_light = tk.Radiobutton(t_frame, text="Tema Claro Profesional", variable=theme_var, value="Claro", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"], activebackground=self.colors["panel"], activeforeground=self.colors["fg"], selectcolor=self.colors["panel"], command=on_theme_change)
        r_light.pack(anchor="w", pady=6)

        r_dark = tk.Radiobutton(t_frame, text="Tema Oscuro Futurista (Cyberpunk Blue)", variable=theme_var, value="Oscuro", font=("Helvetica", 10), fg=self.colors["fg"], bg=self.colors["panel"], activebackground=self.colors["panel"], activeforeground=self.colors["fg"], selectcolor=self.colors["panel"], command=on_theme_change)
        r_dark.pack(anchor="w", pady=6)
