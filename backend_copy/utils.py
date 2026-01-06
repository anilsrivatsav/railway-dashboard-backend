import logging
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from typing import Any, Dict, List, Optional

# ─── LOGGING ────────────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

logger = logging.getLogger("station_units_app")

# ─── GOOGLE SHEET CONFIG ────────────────────────────────────────────────
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'ambient-tuner-447301-s1-934187a30682.json'
SHEET_ID = '1JSlf6FOZMlSrb2wiAcb0LTk2BZYDPzvC98gNLfUDR-0'
TABS = ['Stations', 'Units', 'Earnings']

def get_google_sheet(sheet_id: str, tab_name: str) -> List[Dict[str, Any]]:
    """
    Fetch all records from the named tab in our canonical SHEET_ID.
    """
    if tab_name not in TABS:
        raise ValueError(f"Unknown tab '{tab_name}'. Valid tabs are: {TABS}")

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)

    try:
        ws = client.open_by_key(SHEET_ID).worksheet(tab_name)
        return ws.get_all_records()
    except gspread.exceptions.SpreadsheetNotFound:
        raise Exception(f"❌ Sheet ID '{SHEET_ID}' not found or not shared.")
    except gspread.exceptions.WorksheetNotFound:
        raise Exception(f"❌ Tab '{tab_name}' not found in sheet.")
    except Exception as e:
        raise Exception(f"❌ Failed to fetch tab '{tab_name}': {e}")

# ─── SAFETY CONVERSIONS ─────────────────────────────────────────────────
def safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def parse_bool(value) -> bool:
    s = str(value).strip().lower()
    return s in ('true', '1', 'yes')

def parse_date(value) -> Optional[date]:
    """
    Try a few common date formats; return a date or None.
    """
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            continue
    logger.warning(f"⚠ could not parse date '{value}'")
    return None