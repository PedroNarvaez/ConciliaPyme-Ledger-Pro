import csv
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime

# Helper function to clean float values in Spanish/German/US formats
def clean_float(val: str) -> float:
    if not val:
        return 0.0
    val = val.strip()
    try:
        return float(val)
    except ValueError:
        pass

    # Check if we have both dots and commas (e.g. 1.250,50 or 1,250.50)
    if ',' in val and '.' in val:
        # Determine which is the decimal separator (the last one)
        if val.find('.') > val.find(','):
            # US style: 1,250.50 -> 1250.50
            val = val.replace(',', '')
        else:
            # European style: 1.250,50 -> 1250.50
            val = val.replace('.', '').replace(',', '.')
    elif ',' in val:
        # Check if comma is decimal (e.g. 150000,50 or 150000,0) or thousands separator (150,000)
        parts = val.split(',')
        if len(parts[-1]) <= 2:  # likely decimal (e.g. ,00 or ,5)
            val = val.replace(',', '.')
        else:  # thousands separator
            val = val.replace(',', '')

    try:
        return float(val)
    except ValueError:
        return 0.0

def parse_sales_csv(filepath: str) -> list[dict]:
    """
    Parses Sales CSV.
    Expected headers: referencia, cliente, fecha, monto, moneda
    """
    sales = []
    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}

            ref = clean_row.get('referencia') or clean_row.get('ref') or ""
            client = clean_row.get('cliente') or clean_row.get('client') or ""
            date_str = clean_row.get('fecha') or clean_row.get('date') or ""
            amount_str = clean_row.get('monto') or clean_row.get('amount') or "0"
            currency = clean_row.get('moneda') or clean_row.get('currency') or "PYG"

            amount = clean_float(amount_str)

            sales.append({
                'referencia': ref,
                'cliente': client,
                'fecha': date_str,
                'monto': amount,
                'moneda': currency.upper()
            })
    return sales

def parse_bank_csv(filepath: str, preset: str = "Generic") -> list[dict]:
    """
    Parses Bank CSV based on local bank presets:
    - Generic: referencia, descripcion, fecha, monto, moneda
    - Banco Familiar: Fecha,Referencia,Concepto,Monto,Moneda
    - Banco Continental: Fec. Valor,Nro. Doc.,Descripción,Importe,Moneda
    - Banco Itaú: Data,Documento,Histórico,Valor,Moeda
    - Banco Basa: Fecha,Nro. Referencia,Glosa,Monto,Moneda
    """
    bank_txs = []

    preset_headers = {
        "Banco Familiar": {
            "fecha": "Fecha", "referencia": "Referencia", "descripcion": "Concepto", "monto": "Monto", "moneda": "Moneda"
        },
        "Banco Continental": {
            "fecha": "Fec. Valor", "referencia": "Nro. Doc.", "descripcion": "Descripción", "monto": "Importe", "moneda": "Moneda"
        },
        "Banco Itaú": {
            "fecha": "Data", "referencia": "Documento", "descripcion": "Histórico", "monto": "Valor", "moneda": "Moeda"
        },
        "Banco Basa": {
            "fecha": "Fecha", "referencia": "Nro. Referencia", "descripcion": "Glosa", "monto": "Monto", "moneda": "Moneda"
        },
        "Generic": {
            "fecha": "fecha", "referencia": "referencia", "descripcion": "descripcion", "monto": "monto", "moneda": "moneda"
        }
    }

    mapping = preset_headers.get(preset, preset_headers["Generic"])

    with open(filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip(): v.strip() for k, v in row.items() if k}

            ref = clean_row.get(mapping["referencia"]) or ""
            desc = clean_row.get(mapping["descripcion"]) or ""
            date_str = clean_row.get(mapping["fecha"]) or ""
            amount_str = clean_row.get(mapping["monto"]) or "0"
            currency = clean_row.get(mapping["moneda"]) or "PYG"

            amount = clean_float(amount_str)

            bank_txs.append({
                'referencia': ref,
                'descripcion': desc,
                'fecha': date_str,
                'monto': amount,
                'moneda': currency.upper()
            })
    return bank_txs

def parse_mt940(filepath: str) -> list[dict]:
    """
    Parses an MT940 text file.
    Extracts transaction lines (:61:) and details (:86:).
    """
    transactions = []
    current_tx = None

    with open(filepath, mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith(':61:'):
                content = line[4:]

                # Extract 6-digit date
                date_match = re.match(r'^(\d{6})', content)
                if not date_match:
                    continue
                date_val = date_match.group(1)
                try:
                    dt = datetime.strptime(date_val, "%y%m%d")
                    formatted_date = dt.strftime("%Y-%m-%d")
                except ValueError:
                    formatted_date = date_val

                # Find C or D mark (Credit or Debit)
                mark_match = re.search(r'([CD])', content[6:])
                if not mark_match:
                    continue
                mark = mark_match.group(1)
                mark_idx = content.index(mark, 6)

                # Amount part (after mark, up to a letter or forward slash)
                amt_part = content[mark_idx + 1:]
                amt_match = re.match(r'^([0-9,\.]+)', amt_part)
                if not amt_match:
                    continue
                amount_str = amt_match.group(1)

                amount = clean_float(amount_str)
                if mark == 'D':
                    amount = -amount

                # Extract reference (usually after // or near the end)
                ref = ""
                if '//' in content:
                    ref = content.split('//')[-1].strip()
                else:
                    # Try finding a typical reference pattern
                    ref_match = re.search(r'(FAC-\d+-\d+-\d+|FAC-\d+|REF-\d+)', content)
                    if ref_match:
                        ref = ref_match.group(1)

                current_tx = {
                    'referencia': ref,
                    'descripcion': '',
                    'fecha': formatted_date,
                    'monto': amount,
                    'moneda': 'PYG'
                }
                transactions.append(current_tx)

            elif line.startswith(':86:') and current_tx is not None:
                current_tx['descripcion'] = line[4:].strip()
                if not current_tx['referencia']:
                    ref_match = re.search(r'(FAC-\d+-\d+-\d+|FAC-\d+|REF-\d+)', line)
                    if ref_match:
                        current_tx['referencia'] = ref_match.group(1)

    return transactions

def parse_camt053(filepath: str) -> list[dict]:
    """
    Parses a CAMT.053 XML file (ISO 20022).
    Extracts entries with amounts, dates, and references.
    """
    txs = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        entries = root.findall('.//{*}Ntry')
        for ntry in entries:
            # Amount
            amt_elem = ntry.find('.//{*}Amt')
            amount = 0.0
            currency = 'PYG'
            if amt_elem is not None:
                amount = clean_float(amt_elem.text or "0.0")
                currency = amt_elem.attrib.get('Ccy', 'PYG')

            # Credit/Debit Indicator (CRDT/DBIT)
            cdt_dbt_elem = ntry.find('.//{*}CdtDbtInd')
            if cdt_dbt_elem is not None and cdt_dbt_elem.text == 'DBIT':
                amount = -amount

            # Date
            date_elem = ntry.find('.//{*}BookgDt/{*}Dt')
            if date_elem is None:
                date_elem = ntry.find('.//{*}ValDt/{*}Dt')
            date_str = date_elem.text if date_elem is not None else ""

            # Reference
            ref_elem = ntry.find('.//{*}Refs/{*}EndToEndId')
            if ref_elem is None:
                ref_elem = ntry.find('.//{*}Refs/{*}AcctSvcrRef')
            ref = ref_elem.text if ref_elem is not None else ""

            # Description
            desc_elem = ntry.find('.//{*}AddtlNtryInf')
            desc = desc_elem.text if desc_elem is not None else ""

            txs.append({
                'referencia': ref,
                'descripcion': desc,
                'fecha': date_str,
                'monto': amount,
                'moneda': currency.upper()
            })
    except Exception as e:
        print(f"Error parsing CAMT.053: {e}")
    return txs

def parse_sifen_xml(filepath: str) -> list[dict]:
    """
    Parses Paraguay's SIFEN (Documento Tributario Electrónico / DTE) XML.
    Extracts electronic invoice sales: reference (dNumDoc), customer (dNomRec), date (dFeEmiDE), and total amount (dTotOpe).
    """
    sales = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        num_doc_elem = root.find('.//{*}dNumDoc')
        invoice_ref = num_doc_elem.text if num_doc_elem is not None else ""

        cust_elem = root.find('.//{*}dNomRec')
        customer = cust_elem.text if cust_elem is not None else "Cliente SIFEN"

        date_elem = root.find('.//{*}dFeEmiDE')
        date_str = date_elem.text if date_elem is not None else ""
        if date_str:
            date_str = date_str.split('T')[0]

        tot_elem = root.find('.//{*}dTotOpe')
        amount = clean_float(tot_elem.text) if tot_elem is not None else 0.0

        cur_elem = root.find('.//{*}cMoneOpe')
        currency = cur_elem.text if cur_elem is not None else "PYG"
        if currency == "1" or currency == "PYG":
            currency = "PYG"
        elif currency == "2" or currency == "USD":
            currency = "USD"

        sales.append({
            'referencia': invoice_ref,
            'cliente': customer,
            'fecha': date_str,
            'monto': amount,
            'moneda': currency
        })
    except Exception as e:
        print(f"Error parsing SIFEN XML: {e}")
    return sales


# Demo File Generators

def generate_demo_sales_csv(filepath: str):
    data = [
        ["referencia", "cliente", "fecha", "monto", "moneda"],
        ["FAC-001-002-000456", "Juan Perez", "2026-03-01", "150000.0", "PYG"],
        ["FAC-001-002-000457", "Maria Gomez", "2026-03-02", "320000.0", "PYG"],
        ["FAC-001-002-000458", "Carlos Lopez", "2026-03-03", "450000.0", "PYG"],
        ["FAC-001-002-000459", "Tech Import S.A.", "2026-03-04", "100.0", "USD"],
        ["FAC-001-002-000460", "Distribuidora PY", "2026-03-05", "850000.0", "PYG"]
    ]
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def generate_demo_bank_csv(filepath: str, preset: str = "Generic"):
    if preset == "Banco Familiar":
        headers = ["Fecha", "Referencia", "Concepto", "Monto", "Moneda"]
        rows = [
            ["2026-03-01", "FAC-001-002-000456", "DEPOSITO JUAN PEREZ", "150000.0", "PYG"],
            ["2026-03-02", "FAC-001-002-000457", "TRANSFERENCIA GOMEZ", "320000.0", "PYG"],
            ["2026-03-05", "FAC-001-002-000460", "PAGO DISTRIBUIDORA", "840000.0", "PYG"]
        ]
    elif preset == "Banco Continental":
        headers = ["Fec. Valor", "Nro. Doc.", "Descripción", "Importe", "Moneda"]
        rows = [
            ["2026-03-01", "FAC-001-002-000456", "DEP J PEREZ", "150000.0", "PYG"],
            ["2026-03-02", "FAC-001-002-000457", "TRANSFERENCIA MARIA GOMEZ", "320000.0", "PYG"],
            ["2026-03-03", "FAC-001-002-000458", "PAGO CARLOS LOPEZ", "450000.0", "PYG"]
        ]
    elif preset == "Banco Itaú":
        headers = ["Data", "Documento", "Histórico", "Valor", "Moeda"]
        rows = [
            ["2026-03-01", "FAC-001-002-000456", "TED DEPOSITO PEREZ", "150000.0", "PYG"],
            ["2026-03-03", "FAC-001-002-000458", "COBRO LOPEZ", "450000.0", "PYG"]
        ]
    elif preset == "Banco Basa":
        headers = ["Fecha", "Nro. Referencia", "Glosa", "Monto", "Moneda"]
        rows = [
            ["2026-03-02", "FAC-001-002-000457", "DEP GOMEZ", "320000.0", "PYG"],
            ["2026-03-04", "FAC-001-002-000459", "PAGO TECH IMPORT", "100.0", "USD"]
        ]
    else: # Generic
        headers = ["referencia", "descripcion", "fecha", "monto", "moneda"]
        rows = [
            ["FAC-001-002-000456", "PAGO CLIENTE PEREZ", "2026-03-01", "150000.0", "PYG"],
            ["FAC-001-002-000457", "TRANSFERENCIA GOMEZ", "2026-03-02", "320000.0", "PYG"],
            ["FAC-001-002-000458", "CARLOS LOPEZ COBRO", "2026-03-03", "450000.0", "PYG"]
        ]

    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def generate_demo_mt940(filepath: str):
    content = """:20:CONCILIAPYMEDEMO
:25:123456789PYG
:28C:00001
:60F:C260301PYG1000000,
:61:2603010301C150000,FNDNREFFAC-001-002-000456//FAC-001-002-000456
:86:PAGO FACTURA JUAN PEREZ
:61:2603020302C320000,FNDNREFFAC-001-002-000457//FAC-001-002-000457
:86:TRANSFERENCIA GOMEZ DEPOSITO
:62F:C260305PYG1470000,
"""
    with open(filepath, mode='w', encoding='utf-8') as f:
        f.write(content)

def generate_demo_camt053(filepath: str):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt>
    <Stmt>
      <Id>001</Id>
      <Ntry>
        <Amt Ccy="PYG">150000.0</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <BookgDt>
          <Dt>2026-03-01</Dt>
        </BookgDt>
        <Refs>
          <EndToEndId>FAC-001-002-000456</EndToEndId>
        </Refs>
        <AddtlNtryInf>PAGO JUAN PEREZ</AddtlNtryInf>
      </Ntry>
      <Ntry>
        <Amt Ccy="PYG">450000.0</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <BookgDt>
          <Dt>2026-03-03</Dt>
        </BookgDt>
        <Refs>
          <EndToEndId>FAC-001-002-000458</EndToEndId>
        </Refs>
        <AddtlNtryInf>DEP CARLOS LOPEZ</AddtlNtryInf>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>
"""
    with open(filepath, mode='w', encoding='utf-8') as f:
        f.write(content)

def generate_demo_sifen_xml(filepath: str):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<rDE xmlns="http://sifen.set.gov.py/schema/de/v150">
  <gDatGralOpe>
    <gOpeNum>
      <dNumDoc>FAC-001-002-000457</dNumDoc>
    </gOpeNum>
    <gOpeCom>
      <dFeEmiDE>2026-03-02T10:30:00</dFeEmiDE>
      <cMoneOpe>PYG</cMoneOpe>
    </gOpeCom>
    <gResta>
      <dNomRec>Maria Gomez SIFEN DEMO</dNomRec>
    </gResta>
  </gDatGralOpe>
  <gTotSub>
    <dTotOpe>320000.0</dTotOpe>
  </gTotSub>
</rDE>
"""
    with open(filepath, mode='w', encoding='utf-8') as f:
        f.write(content)

def generate_all_demo_files(directory: str):
    os.makedirs(directory, exist_ok=True)
    generate_demo_sales_csv(os.path.join(directory, "demo_sales.csv"))
    generate_demo_bank_csv(os.path.join(directory, "demo_bank_generic.csv"), "Generic")
    generate_demo_bank_csv(os.path.join(directory, "demo_bank_familiar.csv"), "Banco Familiar")
    generate_demo_bank_csv(os.path.join(directory, "demo_bank_continental.csv"), "Banco Continental")
    generate_demo_bank_csv(os.path.join(directory, "demo_bank_itau.csv"), "Banco Itaú")
    generate_demo_bank_csv(os.path.join(directory, "demo_bank_basa.csv"), "Banco Basa")
    generate_demo_mt940(os.path.join(directory, "demo_bank_mt940.txt"))
    generate_demo_camt053(os.path.join(directory, "demo_bank_camt053.xml"))
    generate_demo_sifen_xml(os.path.join(directory, "demo_sifen.xml"))
