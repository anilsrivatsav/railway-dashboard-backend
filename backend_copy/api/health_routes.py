from fastapi import APIRouter
import gspread
from google.oauth2.service_account import Credentials

router = APIRouter(prefix="/health", tags=["Health"])

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'ambient-tuner-447301-s1-934187a30682.json'
SHEET_ID = '1JSlf6FOZMlSrb2wiAcb0LTk2BZYDPzvC98gNLfUDR-0'
TABS = ['Stations', 'Units', 'Earnings']

@router.get("/sheet")
def sheet_health_check():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    result = {}

    for tab in TABS:
        try:
            sheet = client.open_by_key(SHEET_ID).worksheet(tab)
            records = sheet.get_all_records()
            result[tab] = f"{len(records)} records fetched ✅"
        except gspread.exceptions.WorksheetNotFound:
            result[tab] = "Tab not found ❌"
        except Exception as e:
            result[tab] = f"Error: {e}"

    return {"sheet_id": SHEET_ID, "tabs": result}