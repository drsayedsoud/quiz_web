from gsheet_helper import save_counter

save_counter('test@example.com', 123)
from gsheet_helper import save_counter

save_counter('user2@example.com', 999)
from gsheet_helper import save_counter, save_session, save_vip

# إضافة في Counters
save_counter('user_counter_test@example.com', 7)

# إضافة في Sessions
import json
session_data = {
    "email": "user_session_test@example.com",
    "date": "2024-06-01",
    "score": 10,
    "attempted": 12
}
save_session('user_session_test@example.com', json.dumps(session_data, ensure_ascii=False))

# إضافة في VIP
save_vip('user_vip_test@example.com', True)

print("تمت إضافة صف في كل صفحة بنجاح! ✅")
