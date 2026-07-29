import http.server
import socketserver
import threading
import urllib.request
import json
from src.database import get_db_connection, DB_FILE

class SnapshotHTTPHandler(http.server.BaseHTTPRequestHandler):
    db_path = DB_FILE

    def log_message(self, format, *args):
        # Override to suppress standard HTTP logging to console
        pass

    def do_GET(self):
        if self.path == "/snapshot":
            # Fetch all database snapshots
            try:
                snapshot = get_database_snapshot(self.db_path)
                response_data = json.dumps(snapshot).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_data)))
                self.end_headers()
                self.wfile.write(response_data)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def get_database_snapshot(db_path: str) -> dict:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # 1. Fetch runs
        cursor.execute("SELECT * FROM runs")
        runs = [dict(row) for row in cursor.fetchall()]

        # 2. Fetch results
        cursor.execute("SELECT * FROM results")
        results = [dict(row) for row in cursor.fetchall()]

        # 3. Fetch ledger
        cursor.execute("SELECT * FROM ledger")
        ledger = [dict(row) for row in cursor.fetchall()]

        # 4. Fetch audit_log
        cursor.execute("SELECT * FROM audit_log")
        audit_log = [dict(row) for row in cursor.fetchall()]

        return {
            'runs': runs,
            'results': results,
            'ledger': ledger,
            'audit_log': audit_log
        }
    finally:
        conn.close()

class LANSyncServer:
    def __init__(self, port: int = 8080, db_path: str = DB_FILE):
        self.port = port
        self.db_path = db_path
        self.server = None
        self.thread = None

    def start(self):
        """Starts HTTP server in a background thread."""
        class CustomHandler(SnapshotHTTPHandler):
            db_path = self.db_path

        handler = CustomHandler
        # Allow port reuse to avoid 'address already in use' errors
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(("", self.port), handler)

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        """Stops the HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

def import_snapshot_from_url(url: str, db_path: str = DB_FILE) -> tuple[bool, str]:
    """
    Downloads snapshot from url, and inserts missing runs, results, ledger blocks, and audit entries.
    Only inserts if they do not already exist (matching code for runs, index for ledger, id for audits, hash for results).
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ConciliaPymeSync/2.3.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))

        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Keep track of imported summary count
        new_runs_count = 0

        try:
            # 1. Import runs
            for run in data.get('runs', []):
                cursor.execute("SELECT COUNT(*) FROM runs WHERE code = ?", (run['code'],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO runs (code, timestamp, actor, platform, rule_date_tolerance, rule_amount_tolerance,
                                         sales_count, bank_count, conciliated_count, discrepancy_count, pending_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (run['code'], run['timestamp'], run['actor'], run['platform'],
                          run['rule_date_tolerance'], run['rule_amount_tolerance'],
                          run['sales_count'], run['bank_count'], run['conciliated_count'],
                          run['discrepancy_count'], run['pending_count']))
                    new_runs_count += 1

            # 2. Import results (filter by imported run codes only)
            for res in data.get('results', []):
                # Verify if this results row is already there
                cursor.execute("""
                    SELECT COUNT(*) FROM results
                    WHERE run_code = ? AND row_hash = ?
                """, (res['run_code'], res['row_hash']))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO results (run_code, sale_ref, sale_client, sale_date, sale_amount, sale_currency,
                                             bank_ref, bank_desc, bank_date, bank_amount, bank_currency, status, difference, row_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (res['run_code'], res['sale_ref'], res['sale_client'], res['sale_date'], res['sale_amount'], res['sale_currency'],
                          res['bank_ref'], res['bank_desc'], res['bank_date'], res['bank_amount'], res['bank_currency'],
                          res['status'], res['difference'], res['row_hash']))

            # 3. Import ledger (blocks missing based on block_hash)
            for block in data.get('ledger', []):
                cursor.execute("SELECT COUNT(*) FROM ledger WHERE block_hash = ?", (block['block_hash'],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO ledger (timestamp, actor, node, platform, prev_hash, tx_hash, status, block_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (block['timestamp'], block['actor'], block['node'], block['platform'],
                          block['prev_hash'], block['tx_hash'], block['status'], block['block_hash']))

            # 4. Import audit logs (logs missing based on event_hash)
            for audit in data.get('audit_log', []):
                cursor.execute("SELECT COUNT(*) FROM audit_log WHERE event_hash = ?", (audit['event_hash'],))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO audit_log (timestamp, actor, event_type, description, prev_hash, event_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (audit['timestamp'], audit['actor'], audit['event_type'], audit['description'],
                          audit['prev_hash'], audit['event_hash']))

            conn.commit()
            return True, f"Sincronización finalizada. Se importaron {new_runs_count} corridas nuevas."
        except Exception as inner_e:
            conn.rollback()
            return False, f"Fallo al insertar snapshot en la base de datos: {str(inner_e)}"
        finally:
            conn.close()

    except Exception as e:
        return False, f"Error al descargar snapshot desde URL: {str(e)}"
