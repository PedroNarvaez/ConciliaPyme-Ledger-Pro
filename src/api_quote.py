import urllib.request
import json
import sqlite3
from src.database import get_db_connection, DB_FILE

API_URL = "https://dolar.melizeche.com/api/1.0/"

def fetch_and_cache_quotes(db_path: str = DB_FILE) -> tuple[dict, str]:
    """
    Fetches exchange rates from Melizeche's API and updates the local cache.
    If the request fails, it reads from the cache database.
    Returns: (sources_dict, status_message)
    """
    try:
        # Request with a standard User-Agent to avoid getting blocked
        req = urllib.request.Request(
            API_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ConciliaPyme/2.3.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

        if 'dolarpy' in data:
            sources = data['dolarpy']
            updated_at = data.get('updated', datetime_now_str())

            # Save to SQLite cache
            conn = get_db_connection(db_path)
            cursor = conn.cursor()
            for source_name, rates in sources.items():
                compra = float(rates.get('compra', 0.0))
                venta = float(rates.get('venta', 0.0))
                cursor.execute("""
                    INSERT OR REPLACE INTO quote_cache (source, compra, venta, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (source_name, compra, venta, updated_at))
            conn.commit()
            conn.close()

            return sources, "Cotizaciones actualizadas en línea con éxito."
    except Exception as e:
        # Fall back to SQLite cache
        cached_sources = read_cached_quotes(db_path)
        if cached_sources:
            return cached_sources, f"Error al consultar API en línea ({str(e)}). Usando última cotización en caché."
        else:
            return {}, f"Error al consultar API y no hay cotización en caché: {str(e)}"

def datetime_now_str() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_cached_quotes(db_path: str = DB_FILE) -> dict:
    """Reads quotes cache from SQLite database."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quote_cache")
    rows = cursor.fetchall()
    conn.close()

    sources = {}
    for row in rows:
        sources[row['source']] = {
            'compra': row['compra'],
            'venta': row['venta'],
            'updated_at': row['updated_at']
        }
    return sources

def convert_usd_to_pyg(amount: float, source: str, db_path: str = DB_FILE) -> float:
    """Converts USD amount to PYG using selected source rate (venta)."""
    quotes = read_cached_quotes(db_path)
    if source in quotes:
        rate = quotes[source]['venta']
        if isinstance(rate, dict):
            # If the dict structure is nested
            rate = float(rate.get('venta', 0))
        return amount * float(rate)
    return 0.0

def convert_pyg_to_usd(amount: float, source: str, db_path: str = DB_FILE) -> float:
    """Converts PYG amount to USD using selected source rate (compra)."""
    quotes = read_cached_quotes(db_path)
    if source in quotes:
        rate = quotes[source]['compra']
        if isinstance(rate, dict):
            rate = float(rate.get('compra', 0))
        if float(rate) > 0:
            return amount / float(rate)
    return 0.0
