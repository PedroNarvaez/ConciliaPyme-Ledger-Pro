import hashlib
import json
from datetime import datetime
from src.database import get_db_connection, DB_FILE

def parse_date(date_str: str) -> datetime:
    """Tries parsing date string from common formats."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            pass
    try:
        # Fallback to date part only if ISO with T
        if 'T' in date_str:
            return datetime.strptime(date_str.split('T')[0], "%Y-%m-%d")
    except Exception:
        pass
    return datetime.now()

def compute_row_hash(sale: dict | None, bank: dict | None, status: str) -> str:
    """Computes SHA-256 of matched row attributes."""
    payload = f"{sale.get('referencia') if sale else ''}|{sale.get('monto') if sale else ''}|" \
              f"{bank.get('referencia') if bank else ''}|{bank.get('monto') if bank else ''}|{status}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def reconcile_lists(sales: list[dict], bank_txs: list[dict], tolerance_days: int = 3, tolerance_amount: float = 0.0) -> list[dict]:
    """
    Reconciles sales and bank transactions.
    Returns list of result dicts containing matching status and details.
    """
    results = []
    matched_bank_indices = set()

    # 1. First pass: Match by exact reference
    for sale in sales:
        sale_ref = sale['referencia'].strip()
        sale_date = parse_date(sale['fecha'])

        best_bank_idx = None
        best_status = "pendiente"
        diff_amount = 0.0

        # Look for matching bank transaction by reference first
        for idx, bank in enumerate(bank_txs):
            if idx in matched_bank_indices:
                continue

            bank_ref = bank['referencia'].strip()
            if sale_ref and bank_ref and sale_ref.lower() == bank_ref.lower():
                # Reference matches! Check date and amount tolerances
                bank_date = parse_date(bank['fecha'])
                days_diff = abs((sale_date - bank_date).days)
                val_diff = abs(sale['monto'] - bank['monto'])
                same_currency = (sale['moneda'].upper() == bank['moneda'].upper())

                if days_diff <= tolerance_days and val_diff <= tolerance_amount and same_currency:
                    best_status = "conciliada"
                else:
                    best_status = "discrepancia"

                best_bank_idx = idx
                diff_amount = sale['monto'] - bank['monto']
                break

        # 2. Second pass (fallback): Match by client name / description substring + tolerances if no reference match
        if best_status == "pendiente":
            for idx, bank in enumerate(bank_txs):
                if idx in matched_bank_indices:
                    continue

                # Check client name in bank desc or vice-versa
                s_client = sale['cliente'].lower() if sale['cliente'] else ""
                b_desc = bank['descripcion'].lower() if bank['descripcion'] else ""

                if s_client and b_desc and (s_client in b_desc or b_desc in s_client):
                    # Description match! Verify tolerances
                    bank_date = parse_date(bank['fecha'])
                    days_diff = abs((sale_date - bank_date).days)
                    val_diff = abs(sale['monto'] - bank['monto'])
                    same_currency = (sale['moneda'].upper() == bank['moneda'].upper())

                    if days_diff <= tolerance_days and val_diff <= tolerance_amount and same_currency:
                        best_status = "conciliada"
                        best_bank_idx = idx
                        diff_amount = sale['monto'] - bank['monto']
                        break

        # Record results
        if best_bank_idx is not None:
            matched_bank_indices.add(best_bank_idx)
            bank = bank_txs[best_bank_idx]
            row_hash = compute_row_hash(sale, bank, best_status)
            results.append({
                'sale_ref': sale['referencia'],
                'sale_client': sale['cliente'],
                'sale_date': sale['fecha'],
                'sale_amount': sale['monto'],
                'sale_currency': sale['moneda'],
                'bank_ref': bank['referencia'],
                'bank_desc': bank['descripcion'],
                'bank_date': bank['fecha'],
                'bank_amount': bank['monto'],
                'bank_currency': bank['moneda'],
                'status': best_status,
                'difference': diff_amount,
                'row_hash': row_hash
            })
        else:
            # Unmatched sale -> pendiente
            row_hash = compute_row_hash(sale, None, "pendiente")
            results.append({
                'sale_ref': sale['referencia'],
                'sale_client': sale['cliente'],
                'sale_date': sale['fecha'],
                'sale_amount': sale['monto'],
                'sale_currency': sale['moneda'],
                'bank_ref': '',
                'bank_desc': '',
                'bank_date': '',
                'bank_amount': 0.0,
                'bank_currency': '',
                'status': 'pendiente',
                'difference': sale['monto'],
                'row_hash': row_hash
            })

    # Add unmatched bank transactions
    for idx, bank in enumerate(bank_txs):
        if idx not in matched_bank_indices:
            row_hash = compute_row_hash(None, bank, "pendiente")
            results.append({
                'sale_ref': '',
                'sale_client': '',
                'sale_date': '',
                'sale_amount': 0.0,
                'sale_currency': '',
                'bank_ref': bank['referencia'],
                'bank_desc': bank['descripcion'],
                'bank_date': bank['fecha'],
                'bank_amount': bank['monto'],
                'bank_currency': bank['moneda'],
                'status': 'pendiente',
                'difference': -bank['monto'],
                'row_hash': row_hash
            })

    return results

def compute_tx_hash(results: list[dict]) -> str:
    """Computes SHA-256 over all transaction hashes in the run."""
    row_hashes = sorted([r['row_hash'] for r in results])
    payload = "|".join(row_hashes)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def create_ledger_block(actor: str, tx_hash: str, status: str, db_path: str = DB_FILE) -> tuple[int, str]:
    """Generates a ledger block linked to the previous block."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        # Get prev block hash
        cursor.execute("SELECT block_hash FROM ledger ORDER BY block_index DESC LIMIT 1")
        last_row = cursor.fetchone()
        prev_hash = last_row['block_hash'] if last_row else "GENESIS_BLOCK"

        timestamp = datetime.now().isoformat()
        node = "NODE-PY-01"
        platform = "Hyperledger Fabric (Permissioned)"

        # block_hash calculation
        block_payload = f"{prev_hash}|{tx_hash}|{timestamp}|{actor}|{node}|{platform}|{status}"
        block_hash = hashlib.sha256(block_payload.encode('utf-8')).hexdigest()

        cursor.execute("""
            INSERT INTO ledger (timestamp, actor, node, platform, prev_hash, tx_hash, status, block_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, actor, node, platform, prev_hash, tx_hash, status, block_hash))
        conn.commit()

        block_index = cursor.lastrowid or 0
        return block_index, block_hash
    finally:
        conn.close()

def verify_ledger_integrity(db_path: str = DB_FILE) -> tuple[bool, str]:
    """Verifies cryptographic linking of all ledger blocks."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM ledger ORDER BY block_index ASC")
        blocks = cursor.fetchall()
        if not blocks:
            return True, "El ledger local está vacío. Integridad intacta."

        expected_prev_hash = "GENESIS_BLOCK"
        for block in blocks:
            idx = block['block_index']
            timestamp = block['timestamp']
            actor = block['actor']
            node = block['node']
            platform = block['platform']
            prev_hash = block['prev_hash']
            tx_hash = block['tx_hash']
            status = block['status']
            block_hash = block['block_hash']

            # Check link to previous
            if prev_hash != expected_prev_hash:
                return False, f"Fallo de enlace de ledger en el bloque {idx}. Esperaba: {expected_prev_hash}, Obtuve: {prev_hash}"

            # Recalculate block hash
            block_payload = f"{prev_hash}|{tx_hash}|{timestamp}|{actor}|{node}|{platform}|{status}"
            recalculated = hashlib.sha256(block_payload.encode('utf-8')).hexdigest()
            if recalculated != block_hash:
                return False, f"Fallo de hash en el bloque {idx}. El contenido fue alterado."

            expected_prev_hash = block_hash

        return True, "Integridad del ledger local verificada con éxito. Todos los bloques están intactos."
    except Exception as e:
        return False, f"Error al verificar ledger: {str(e)}"
    finally:
        conn.close()

def save_reconciliation_run(run_code: str, actor: str, results: list[dict], tolerance_days: int, tolerance_amount: float, db_path: str = DB_FILE) -> tuple[bool, str]:
    """Saves a reconciliation run (summary in runs, details in results) and commits a ledger block."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        sales_cnt = sum(1 for r in results if r['sale_ref'] or r['sale_client'])
        bank_cnt = sum(1 for r in results if r['bank_ref'] or r['bank_desc'])
        conciliated_cnt = sum(1 for r in results if r['status'] == 'conciliada')
        discrepancy_cnt = sum(1 for r in results if r['status'] == 'discrepancia')
        pending_cnt = sum(1 for r in results if r['status'] == 'pendiente')

        # Insert Run Summary
        timestamp = datetime.now().isoformat()
        platform = "Hyperledger Fabric (Permissioned)"
        cursor.execute("""
            INSERT INTO runs (code, timestamp, actor, platform, rule_date_tolerance, rule_amount_tolerance,
                             sales_count, bank_count, conciliated_count, discrepancy_count, pending_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (run_code, timestamp, actor, platform, tolerance_days, tolerance_amount,
              sales_cnt, bank_cnt, conciliated_cnt, discrepancy_cnt, pending_cnt))

        # Insert Results Detalle
        for r in results:
            cursor.execute("""
                INSERT INTO results (run_code, sale_ref, sale_client, sale_date, sale_amount, sale_currency,
                                     bank_ref, bank_desc, bank_date, bank_amount, bank_currency, status, difference, row_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (run_code, r['sale_ref'], r['sale_client'], r['sale_date'], r['sale_amount'], r['sale_currency'],
                  r['bank_ref'], r['bank_desc'], r['bank_date'], r['bank_amount'], r['bank_currency'],
                  r['status'], r['difference'], r['row_hash']))

        conn.commit()

        # Commit Ledger Block
        tx_hash = compute_tx_hash(results)
        create_ledger_block(actor, tx_hash, "COMMITTED", db_path=db_path)

        return True, "Corrida guardada y registrada en el ledger local."
    except Exception as e:
        return False, f"Error al guardar la corrida de conciliación: {str(e)}"
    finally:
        conn.close()

def load_reconciliation_run(run_code: str, db_path: str = DB_FILE) -> tuple[dict | None, list[dict]]:
    """Loads a previous run summary and its results."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM runs WHERE code = ?", (run_code,))
        run_row = cursor.fetchone()
        if not run_row:
            return None, []

        run_dict = dict(run_row)

        cursor.execute("SELECT * FROM results WHERE run_code = ?", (run_code,))
        results = [dict(row) for row in cursor.fetchall()]
        return run_dict, results
    finally:
        conn.close()

def get_all_runs(db_path: str = DB_FILE) -> list[dict]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    runs = [dict(row) for row in rows]
    conn.close()
    return runs
