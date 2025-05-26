import gspread
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'dental-world-dde59-cb4421544a45.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1dGa6lmOLy5a7Kkw3DNDh2uw4aPjOCSP9oA6AmTIbAa8'  # اتركها كما هي لو تستخدم نفس شيت الأسئلة

def get_sheet(sheet_name):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(sheet_name)

# ------------------ Counters ------------------
def save_counter(email, count):
    print(f"[DEBUG] save_counter called for: {email} - {count}")
    ws = get_sheet('Counters')
    cell = ws.find(email)
    if cell:
        ws.update_cell(cell.row, 2, count)
    else:
        ws.append_row([email, count])

def get_counter(email):
    ws = get_sheet('Counters')
    try:
        cell = ws.find(email)
        if cell:
            return int(ws.cell(cell.row, 2).value)
    except Exception as e:
        print("[gsheet] Error in get_counter:", e)
    return 0

# ------------------ Sessions ------------------
def save_session(email, session_data):
    print(f"[DEBUG] save_session called for: {email} - {session_data}")
    ws = get_sheet('Sessions')
    cell = ws.find(email)
    if cell:
        ws.update_cell(cell.row, 2, session_data)
    else:
        ws.append_row([email, session_data])

def get_session(email):
    ws = get_sheet('Sessions')
    try:
        cell = ws.find(email)
        if cell:
            return ws.cell(cell.row, 2).value
    except Exception as e:
        print("[gsheet] Error in get_session:", e)
    return None

# ------------------ VIP ------------------
def save_vip(email, is_vip=True):
    print(f"[DEBUG] save_vip called for: {email} - {is_vip}")
    ws = get_sheet('VIP')
    cell = ws.find(email)
    if cell:
        ws.update_cell(cell.row, 2, str(is_vip))
    else:
        ws.append_row([email, str(is_vip)])

def check_vip(email):
    ws = get_sheet('VIP')
    try:
        cell = ws.find(email)
        if cell:
            return ws.cell(cell.row, 2).value == 'True'
    except Exception as e:
        print("[gsheet] Error in check_vip:", e)
    return False
