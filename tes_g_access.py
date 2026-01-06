import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'ambient-tuner-447301-s1-934187a30682.json'  # update this if needed
SHEET_ID = '1JSlf6FOZMlSrb2wiAcb0LTk2BZYDPzvC98gNLfUDR-0'
TABS = ['Stations', 'Units', 'Earnings']

def test_all_tabs():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    for tab in TABS:
        try:
            sheet = client.open_by_key(SHEET_ID).worksheet(tab)
            records = sheet.get_all_records()
            print(f"✅ Tab '{tab}': {len(records)} records fetched successfully.")
        except gspread.exceptions.WorksheetNotFound:
            print(f"❌ Tab '{tab}' not found in the sheet.")
        except Exception as e:
            print(f"❌ Error accessing tab '{tab}': {e}")

if __name__ == "__main__":
    test_all_tabs()