import os
import pytest
from src.database import init_db, get_db_connection
from src.reconciliation import (
    reconcile_lists,
    compute_tx_hash,
    create_ledger_block,
    verify_ledger_integrity,
    save_reconciliation_run,
    load_reconciliation_run,
    get_all_runs
)

TEST_DB_FILE = "test_reconciliation.db"

@pytest.fixture
def recon_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    init_db(TEST_DB_FILE)
    yield TEST_DB_FILE
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_reconciliation_logic():
    # Setup test input lists
    sales = [
        {"referencia": "FAC-001", "cliente": "Juan Perez", "fecha": "2026-03-01", "monto": 150000.0, "moneda": "PYG"},
        {"referencia": "FAC-002", "cliente": "Maria Gomez", "fecha": "2026-03-02", "monto": 320000.0, "moneda": "PYG"},
        {"referencia": "FAC-003", "cliente": "Carlos Lopez", "fecha": "2026-03-03", "monto": 450000.0, "moneda": "PYG"}
    ]

    bank_txs = [
        # Perfect match for FAC-001
        {"referencia": "FAC-001", "descripcion": "DEP JUAN PEREZ", "fecha": "2026-03-01", "monto": 150000.0, "moneda": "PYG"},
        # Discrepancy match for FAC-002 (amount difference exceeds default 0.0 tolerance)
        {"referencia": "FAC-002", "descripcion": "TRANS GOMEZ", "fecha": "2026-03-02", "monto": 319000.0, "moneda": "PYG"},
        # Substring/concept fallback match (FAC-003 isn't in ref, but 'Carlos Lopez' is in concept, amount and date matches)
        {"referencia": "", "descripcion": "DEPOSITO DE Carlos Lopez VALORADO", "fecha": "2026-03-03", "monto": 450000.0, "moneda": "PYG"},
        # Unmatched bank transaction (should become pending)
        {"referencia": "FAC-999", "descripcion": "DEP EXTRA", "fecha": "2026-03-05", "monto": 10000.0, "moneda": "PYG"}
    ]

    results = reconcile_lists(sales, bank_txs, tolerance_days=3, tolerance_amount=0.0)

    assert len(results) == 4  # 3 matched/unmatched sales, 1 unmatched bank tx

    # Check FAC-001 -> conciliada
    fac1 = next(r for r in results if r['sale_ref'] == 'FAC-001')
    assert fac1['status'] == 'conciliada'
    assert fac1['bank_ref'] == 'FAC-001'

    # Check FAC-002 -> discrepancia (amounts 320000 vs 319000)
    fac2 = next(r for r in results if r['sale_ref'] == 'FAC-002')
    assert fac2['status'] == 'discrepancia'

    # Check FAC-003 -> conciliada (fallback matching on client substring)
    fac3 = next(r for r in results if r['sale_ref'] == 'FAC-003')
    assert fac3['status'] == 'conciliada'
    assert fac3['bank_desc'] == "DEPOSITO DE Carlos Lopez VALORADO"

    # Check FAC-999 -> pending (unmatched bank transaction)
    unmatched_bank = next(r for r in results if r['bank_ref'] == 'FAC-999')
    assert unmatched_bank['status'] == 'pendiente'
    assert unmatched_bank['sale_ref'] == ''

def test_ledger_and_save_run(recon_db):
    sales = [
        {"referencia": "FAC-101", "cliente": "Juan Perez", "fecha": "2026-03-01", "monto": 100.0, "moneda": "USD"}
    ]
    bank = [
        {"referencia": "FAC-101", "descripcion": "PAGO PEREZ", "fecha": "2026-03-01", "monto": 100.0, "moneda": "USD"}
    ]

    results = reconcile_lists(sales, bank, tolerance_days=1, tolerance_amount=0.0)
    run_code = "CONC-20260301-120000"

    # Save the run (this also writes to ledger)
    success, msg = save_reconciliation_run(run_code, "admin", results, 1, 0.0, db_path=recon_db)
    assert success

    # Verify ledger integrity (should be valid)
    is_valid, l_msg = verify_ledger_integrity(db_path=recon_db)
    assert is_valid

    # Load run and verify
    run_dict, loaded_results = load_reconciliation_run(run_code, db_path=recon_db)
    assert run_dict is not None
    assert run_dict['sales_count'] == 1
    assert run_dict['conciliated_count'] == 1
    assert len(loaded_results) == 1
    assert loaded_results[0]['sale_ref'] == 'FAC-101'

    # Check get all runs
    all_runs = get_all_runs(db_path=recon_db)
    assert len(all_runs) == 1
    assert all_runs[0]['code'] == run_code

def test_ledger_tampering(recon_db):
    # Create multiple ledger blocks
    create_ledger_block("admin", "hashA", "COMMITTED", db_path=recon_db)
    create_ledger_block("contador", "hashB", "COMMITTED", db_path=recon_db)

    # Verify (intact)
    is_valid, msg = verify_ledger_integrity(db_path=recon_db)
    assert is_valid

    # Tamper with block index 1
    conn = get_db_connection(recon_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE ledger SET actor = 'HACKER' WHERE block_index = 1")
    conn.commit()
    conn.close()

    # Verify (tampered!)
    is_valid, msg = verify_ledger_integrity(db_path=recon_db)
    assert not is_valid
    assert "Fallo de hash" in msg or "Fallo de enlace" in msg
