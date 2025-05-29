import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'dental-world-dde59-cb4421544a45.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1dGa6lmOLy5a7Kkw3DNDh2uw4aPjOCSP9oA6AmTIbAa8'

def get_sheet(sheet_name):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(sheet_name)

# ------------------ Counters ------------------
def save_counter(email, count):
    ws = get_sheet('Counters')
    try:
        cell = ws.find(email)
        ws.update_cell(cell.row, 2, count)
    except:
        ws.append_row([email, count])

def get_counter(email):
    ws = get_sheet('Counters')
    try:
        cell = ws.find(email)
        return int(ws.cell(cell.row, 2).value)
    except:
        return 0

# ------------------ Sessions ------------------
def save_session(email, session_data):
    ws = get_sheet('Sessions')
    # لا تكتب الجلسة إذا كانت مكررة (تفادي تكرار الصفوف)
    existing_sessions = get_session(email)
    if existing_sessions and session_data in existing_sessions:
        return
    ws.append_row([email, session_data])

def get_session(email):
    ws = get_sheet('Sessions')
    all_rows = ws.get_all_values()
    sessions = []
    for row in all_rows:
        # صفوف الجلسات: [email, json_session_data]
        if row and row[0] == email:
            if len(row) > 1:
                sessions.append(row[1])
    return sessions if sessions else None

# ------------------ VIP ------------------
def save_vip(email, is_vip=True):
    ws = get_sheet('VIP')
    try:
        cell = ws.find(email)
        ws.update_cell(cell.row, 2, str(is_vip))
    except:
        ws.append_row([email, str(is_vip)])

def check_vip(email):
    ws = get_sheet('VIP')
    try:
        cell = ws.find(email)
        return ws.cell(cell.row, 2).value == 'True'
    except:
        return False
