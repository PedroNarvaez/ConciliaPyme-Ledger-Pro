import os
import pytest
from src.importers import (
    parse_sales_csv,
    parse_bank_csv,
    parse_mt940,
    parse_camt053,
    parse_sifen_xml,
    generate_all_demo_files
)

DEMO_DIR = "test_demo_files"

@pytest.fixture(scope="module")
def setup_demo_files():
    if os.path.exists(DEMO_DIR):
        for f in os.listdir(DEMO_DIR):
            os.remove(os.path.join(DEMO_DIR, f))
        os.rmdir(DEMO_DIR)

    generate_all_demo_files(DEMO_DIR)
    yield DEMO_DIR

    if os.path.exists(DEMO_DIR):
        for f in os.listdir(DEMO_DIR):
            os.remove(os.path.join(DEMO_DIR, f))
        os.rmdir(DEMO_DIR)

def test_sales_csv_parser(setup_demo_files):
    path = os.path.join(setup_demo_files, "demo_sales.csv")
    sales = parse_sales_csv(path)
    assert len(sales) == 5
    assert sales[0]['referencia'] == 'FAC-001-002-000456'
    assert sales[0]['cliente'] == 'Juan Perez'
    assert sales[0]['monto'] == 150000.0
    assert sales[0]['moneda'] == 'PYG'

def test_bank_csv_presets(setup_demo_files):
    # Familiar
    path_fam = os.path.join(setup_demo_files, "demo_bank_familiar.csv")
    txs_fam = parse_bank_csv(path_fam, preset="Banco Familiar")
    assert len(txs_fam) == 3
    assert txs_fam[0]['referencia'] == 'FAC-001-002-000456'
    assert txs_fam[0]['descripcion'] == 'DEPOSITO JUAN PEREZ'
    assert txs_fam[0]['monto'] == 150000.0
    assert txs_fam[0]['moneda'] == 'PYG'

    # Continental
    path_cont = os.path.join(setup_demo_files, "demo_bank_continental.csv")
    txs_cont = parse_bank_csv(path_cont, preset="Banco Continental")
    assert len(txs_cont) == 3
    assert txs_cont[1]['referencia'] == 'FAC-001-002-000457'

    # Itaú
    path_itau = os.path.join(setup_demo_files, "demo_bank_itau.csv")
    txs_itau = parse_bank_csv(path_itau, preset="Banco Itaú")
    assert len(txs_itau) == 2
    assert txs_itau[0]['referencia'] == 'FAC-001-002-000456'

    # Basa
    path_basa = os.path.join(setup_demo_files, "demo_bank_basa.csv")
    txs_basa = parse_bank_csv(path_basa, preset="Banco Basa")
    assert len(txs_basa) == 2
    assert txs_basa[1]['monto'] == 100.0
    assert txs_basa[1]['moneda'] == 'USD'

def test_mt940_parser(setup_demo_files):
    path = os.path.join(setup_demo_files, "demo_bank_mt940.txt")
    txs = parse_mt940(path)
    assert len(txs) == 2
    assert txs[0]['referencia'] == 'FAC-001-002-000456'
    assert txs[0]['monto'] == 150000.0
    assert txs[0]['fecha'] == '2026-03-01'
    assert txs[0]['descripcion'] == 'PAGO FACTURA JUAN PEREZ'

def test_camt053_parser(setup_demo_files):
    path = os.path.join(setup_demo_files, "demo_bank_camt053.xml")
    txs = parse_camt053(path)
    assert len(txs) == 2
    assert txs[0]['referencia'] == 'FAC-001-002-000456'
    assert txs[0]['monto'] == 150000.0
    assert txs[0]['fecha'] == '2026-03-01'

def test_sifen_parser(setup_demo_files):
    path = os.path.join(setup_demo_files, "demo_sifen.xml")
    sales = parse_sifen_xml(path)
    assert len(sales) == 1
    assert sales[0]['referencia'] == 'FAC-001-002-000457'
    assert sales[0]['monto'] == 320000.0
    assert sales[0]['cliente'] == 'Maria Gomez SIFEN DEMO'
    assert sales[0]['fecha'] == '2026-03-02'
