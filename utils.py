import os
import json
import logging
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from typing import Any, Dict, List, Optional

# ─── LOGGING ─────────────────────────────────────────────
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
    if tab_name not in TABS:
        raise ValueError(f"Unknown tab '{tab_name}'. Valid tabs are: {TABS}")

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES
    )
    client = gspread.authorize(creds)

    ws = client.open_by_key(sheet_id).worksheet(tab_name)

    headers = ws.row_values(1)

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


# ─── NUMBER NORMALIZER (INDIAN RAILWAYS SAFE) ─────────────────────────────
def normalize_number(value):
    """
    Handles:
      73451 → 73451
      1,23,456 → 123456
      ₹5,40,000 → 540000
      3,50,000+ → 350000
      05to50Lakhs → 50
      upto01Lakhs → 1
      #N/A → None
    """

    if value is None:
        return None

    # If Google sends number type
    if isinstance(value, (int, float)):
        return str(value)

    s = str(value).strip()

    if s.lower() in ("", "n/a", "#n/a", "na", "none"):
        return None

    # Handle ranges like "05to50Lakhs" → take last number
    if "to" in s.lower():
        nums = re.findall(r"\d+", s)
        if nums:
            return nums[-1]

    # Handle "upto01Lakhs"
    if "upto" in s.lower():
        nums = re.findall(r"\d+", s)
        if nums:
            return nums[-1]

    # Remove currency symbols and commas
    s = re.sub(r"[₹,+\s]", "", s)

    # Remove everything except digits and dot
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


# ─── BOOLEAN PARSER ─────────────────────────────────────────────
def parse_bool(value) -> bool:
    if value is None:
        return False
    s = str(value).strip().lower()
    return s in ("true", "1", "yes", "y", "available", "operational")


# ─── DATE PARSER ─────────────────────────────────────────────
def parse_date(value) -> Optional[date]:
    if value is None:
        return None

    s = str(value).strip()
    if s.lower() in ("", "n/a", "#n/a", "na"):
        return None

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except:
            pass

    logger.warning(f"⚠ Could not parse date '{value}'")
    return None
