import os
import json
import logging
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from typing import Any, Dict, List, Optional

# ─── LOGGING ─────────────────────────────────────────────────────────────
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

logger = logging.getLogger("station_units_app")

# ─── GOOGLE SERVICE ACCOUNT ──────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SERVICE_ACCOUNT_INFO = json.loads(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
)

TABS = ["Stations", "Units", "Earnings"]

# ─── GOOGLE SHEET READER ─────────────────────────────────────────────────
def get_google_sheet(sheet_id: str, tab_name: str) -> List[Dict[str, Any]]:
    """
    Fetch all rows from a Google Sheet tab safely.
    Handles duplicate headers automatically.
    """
    if tab_name not in TABS:
        raise ValueError(f"Unknown tab '{tab_name}'. Valid tabs are: {TABS}")

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES
    )
    client = gspread.authorize(creds)

    try:
        ws = client.open_by_key(sheet_id).worksheet(tab_name)

        # Get header row
        headers = ws.row_values(1)

        # Remove duplicate headers safely
        clean_headers = []
        seen = {}
        for h in headers:
            h = h.strip()
            if h in seen:
                seen[h] += 1
                clean_headers.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 1
                clean_headers.append(h)

        records = ws.get_all_records(expected_headers=clean_headers)

        logger.info(f"📄 Fetched {len(records)} rows from '{tab_name}'")
        return records

    except Exception as e:
        logger.exception("Google Sheet fetch failed")
        raise Exception(f"❌ Failed to fetch tab '{tab_name}': {e}")

# ─── NUMBER NORMALIZATION (₹, commas, + etc) ──────────────────────────────
def normalize_number(value):
    """
    Converts:
      ₹1,305,999  → 1305999
      3,50,000+   → 350000
      1,23,456    → 123456
      #N/A        → None
    """
    if value is None:
        return None

    s = str(value).strip()

    if s.lower() in ("", "n/a", "#n/a", "na", "none"):
        return None

    # Remove currency, commas, plus, spaces
    s = re.sub(r"[₹,+\s]", "", s)

    # Keep digits and dot only
    s = re.sub(r"[^\d.]", "", s)

    if s == "":
        return None

    return s


def safe_int(value, default=0) -> int:
    try:
        n = normalize_number(value)
        if n is None:
            return default
        return int(float(n))
    except:
        return default


def safe_float(value, default=0.0) -> float:
    try:
        n = normalize_number(value)
        if n is None:
            return default
        return float(n)
    except:
        return default

# ─── BOOLEAN PARSER ──────────────────────────────────────────────────────
def parse_bool(value) -> bool:
    s = str(value).strip().lower()
    return s in ("true", "1", "yes", "y", "available", "operational")

# ─── DATE PARSER ─────────────────────────────────────────────────────────
def parse_date(value) -> Optional[date]:
    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except:
            continue

    logger.warning(f"⚠ Could not parse date '{value}'")
    return None
