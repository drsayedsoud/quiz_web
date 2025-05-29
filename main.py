from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json
import base64
import pandas as pd
import threading
import random
import datetime
import math
from gsheet_helper import save_counter, get_counter, save_session, get_session, save_vip, check_vip

EXCEL_FILE = 'quiz_shuffle.xlsx'
USER_COUNTER_FILE = "user_counters.json"
RATINGS_FILE = "ratings.json"
SERVICE_ACCOUNT_FILE = 'dental-world-dde59-cb4421544a45.json'
SESSIONS_FILE = "user_sessions.json"
VIP_USERS_FILE = "vip_users.json"

from functools import wraps

def load_vip_users():
    if os.path.exists(VIP_USERS_FILE):
        with open(VIP_USERS_FILE, "r") as f:
            return json.load(f)
    else:
        # قائمة افتراضية إذا الملف مش موجود
        return {
            "vip1@example.com": "VIPCODE123",
            "dentist@clinic.com": "FULLACCESS"
        }

def save_vip_users(data):
    # تم تعليق Google Sheet هنا
    # for email in data:
    #     save_vip(email, True)
    with open(VIP_USERS_FILE, "w") as f:
        json.dump(data, f)

full_access_users = load_vip_users()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def is_vip_user(email):
    # تم تعليق Google Sheet هنا
    # if check_vip(email):
    #     return True
    return email in full_access_users

def load_all_questions_from_excel():
    df = pd.read_excel(EXCEL_FILE)
    questions = []
    for _, row in df.iterrows():
        questions.append({
            'question': row[0],
            'choices': [row[1], row[2], row[3], row[4]],
            'correct': row[5],
            'explanation': row[6] if len(row) > 6 else '',
            'detailed': row[9] if len(row) > 9 else '',
            'metadata': row[10] if len(row) > 10 else ''
        })
    return questions

all_questions = load_all_questions_from_excel()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

ratings_lock = threading.Lock()

SPREADSHEET_ID = '1dGa6lmOLy5a7Kkw3DNDh2uw4aPjOCSP9oA6AmTIbAa8'
RANGE_NAME = 'Sheet1!A2:K'

subject_start_indexes = {
    "Endodontic": 2270,
    "Operative": 5013,
    "Oral Surgery": 2991,
    "Periodontic": 4112,
    "Fixed Prosthodontic": 4601,
    "Pedodontic": 3290,
    "Orthodontic": 3511,
    "Diagnosis": 4,
    "Radiology": 3880,
    "Removable Prosthodontic": 4804,
    "Pathology": 5223,
    "Anatomy": 4,
    "Oral Medicine": 4368
}

VIP_ADMIN_PASSWORD = "123456789"

def encode_email(email):
    return base64.b64encode(email.encode()).decode()

def decode_email(encoded):
    return base64.b64decode(encoded.encode()).decode()

def load_user_counter(email):
    # تم تعليق جلب Google Sheet هنا
    # gs_count = get_counter(email)
    # if gs_count > 0:
    #     return gs_count
    key = encode_email(email)
    if os.path.exists(USER_COUNTER_FILE):
        with open(USER_COUNTER_FILE, "r") as f:
            data = json.load(f)
            return data.get(key, 0)
    return 0

def save_user_counter(email, value):
    # تم تعليق حفظ Google Sheet هنا
    # save_counter(email, value)
    key = encode_email(email)
    if os.path.exists(USER_COUNTER_FILE):
        with open(USER_COUNTER_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[key] = value
    with open(USER_COUNTER_FILE, "w") as f:
        json.dump(data, f)

def load_ratings():
    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                "ratings": data.get("ratings", []),
                "comments": data.get("comments", []),
                "visible": data.get("visible", True)
            }
        except Exception as e:
            print(f"Error loading ratings: {e}")
            return {"ratings": [], "comments": [], "visible": True}
    else:
        return {"ratings": [], "comments": [], "visible": True}

def save_ratings(data):
    with ratings_lock:
        with open(RATINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

def convert_drive_link_to_direct_url(url):
    if isinstance(url, str):
        if "drive.google.com" in url:
            if "id=" in url:
                file_id = url.split("id=")[-1]
                return f"https://drive.google.com/uc?export=view&id={file_id}"
            elif "/file/d/" in url:
                try:
                    file_id = url.split("/file/d/")[1].split("/")[0]
                    return f"https://drive.google.com/uc?export=view&id={file_id}"
                except:
                    return url
    return url

def get_questions():
    return all_questions

questions = get_questions()

def save_user_session(email, score, attempted, subject=None, current_index=None):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    session_data = {
        "email": email,
        "date": today,
        "score": score,
        "attempted": attempted,
        "subject": subject,
        "last_question_index": current_index
    }
    # تم تعليق حفظ Google Sheet هنا
    # save_session(email, json.dumps(session_data, ensure_ascii=False))

    data = []
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    data.append(session_data)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def get_user_sessions(email):
    # تم تعليق جلب Google Sheet هنا
    # raw = get_session(email)
    # if raw:
    #     sessions = []
    #     if isinstance(raw, list):
    #         for item in raw:
    #             try:
    #                 sessions.append(json.loads(item))
    #             except:
    #                 pass
    #     else:
    #         try:
    #             sessions.append(json.loads(raw))
    #         except:
    #             pass
    #     return sessions

    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
        return [d for d in data if d['email'] == email]
    return []

def get_last_question_index_for_subject(email, subject):
    sessions = get_user_sessions(email)
    for sess in reversed(sessions):
        if sess.get('subject') == subject:
            return sess.get('last_question_index', 1)
    return 1

@app.route('/')
def root_redirect():
    if 'email' in session:
        return redirect(url_for('start'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/set_email', methods=['POST'])
def set_email():
    session['email'] = request.json.get('email')
    return jsonify({'status': 'ok'})

@app.route('/start')
@login_required
def start():
    last_index = session.get('last_index', None)
    total_questions = len(questions)
    email = session.get('email')

    is_vip = False
    if email:
        # تم تعليق جلب Google Sheet هنا
        # is_vip = check_vip(email)
        if not is_vip:
            is_vip = email in full_access_users

        session['global_question_counter'] = load_user_counter(email)
    else:
        session['global_question_counter'] = 0

    return render_template('start.html',
                           last_index=last_index,
                           total_questions=total_questions,
                           is_vip=is_vip)

@app.route('/start_session', methods=['POST'])
@login_required
def start_session():
    email = session.get('email')
    current_count = load_user_counter(email) if email else 0

    if email and (not is_vip_user(email)) and current_count >= 100:
        return redirect(url_for('stop_page'))

    choice = request.form.get('start_choice')
    reset_subject_index = request.form.get('reset_subject_index') == 'true'

    if choice in subject_start_indexes:
        if reset_subject_index:
            session['current_index'] = subject_start_indexes[choice]
        else:
            last_q_index = get_last_question_index_for_subject(email, choice)
            if last_q_index >= subject_start_indexes[choice]:
                session['current_index'] = last_q_index
            else:
                session['current_index'] = subject_start_indexes[choice]
        session['score'] = 0
        session['attempted'] = 0
        session['subject'] = choice
        session.pop('shuffled_indexes', None)
        session.pop('current_pos', None)
    elif choice == 'new':
        total_questions = len(all_questions)
        selected_indexes = random.sample(range(total_questions), min(300, total_questions))
        session['shuffled_indexes'] = selected_indexes
        session['current_pos'] = 0
        session['score'] = 0
        session['attempted'] = 0
        session.pop('subject', None)
    elif choice == 'resume_exam':
        session['current_pos'] = session.get('last_pos', 0)
        session['score'] = 0
        session['attempted'] = 0
        session.pop('subject', None)
    else:
        session['current_index'] = 1
        session['score'] = 0
        session['attempted'] = 0
        session.pop('subject', None)
        session.pop('shuffled_indexes', None)
        session.pop('current_pos', None)

    if 'shuffled_indexes' in session:
        session['total'] = len(session['shuffled_indexes'])
    else:
        session['total'] = len(questions)

    return redirect(url_for('quiz'))

@app.route('/quiz')
@login_required
def quiz():
    if 'shuffled_indexes' in session:
        indexes = session['shuffled_indexes']
        pos = session.get('current_pos', 0)
        if pos >= len(indexes):
            return redirect(url_for('result'))
        real_index = indexes[pos]
        question = all_questions[real_index]
        index = pos + 1
        total = len(indexes)
        question_id = real_index + 1
    else:
        current_index = session.get('current_index', 1)
        if current_index > len(questions):
            return redirect(url_for('result'))
        question = questions[current_index - 1]
        index = current_index
        total = len(questions)
        question_id = current_index

    raw_metadata = question.get('metadata', '')
    if raw_metadata is None:
        metadata = ''
    else:
        metadata = str(raw_metadata)
        if metadata.lower() == 'nan' or metadata.strip() == '':
            metadata = ''

    score = session.get('score', 0)
    attempted = session.get('attempted', 0)
    percentage = (score / attempted * 100) if attempted > 0 else 0
    subject = session.get('subject')

    return render_template('quiz.html',
                           question=question,
                           index=index,
                           question_id=question_id,
                           score=score,
                           attempted=attempted,
                           percentage=percentage,
                           total=total,
                           subject=subject,
                           metadata=metadata)

def async_save_counter(email, new_count):
    save_user_counter(email, new_count)

@app.route('/check', methods=['POST'])
@login_required
def check():
    email = session.get('email')

    if email and email not in full_access_users:
        current_count = load_user_counter(email)
        if current_count >= 100:
            return jsonify({
                'result': 'limit_reached',
                'message': '🚫 لقد تجاوزت الحد الأقصى للأسئلة (100 سؤال).',
                'score': session.get('score', 0),
                'attempted': session.get('attempted', 0)
            }), 403
    else:
        current_count = load_user_counter(email) if email else 0

    data = request.json
    selected = data['selected']
    correct = data['correct']
    score = session.get('score', 0)
    attempted = session.get('attempted', 0)

    attempted += 1
    if selected == correct:
        score += 1

    session['score'] = score
    session['attempted'] = attempted

    if email:
        new_count = current_count + 1
        threading.Thread(target=async_save_counter, args=(email, new_count)).start()
        session['global_question_counter'] = new_count

    return jsonify({
        'result': 'correct' if selected == correct else 'incorrect',
        'correct': correct,
        'score': score,
        'attempted': attempted
    })

@app.route('/stop')
def stop_page():
    return render_template('stop.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/next')
@login_required
def next_question():
    if 'shuffled_indexes' in session:
        pos = session.get('current_pos', 0) + 1
        session['current_pos'] = pos
        if pos >= len(session['shuffled_indexes']):
            return redirect(url_for('result'))
    else:
        current_index = session.get('current_index', 1) + 1
        session['current_index'] = current_index
        if current_index > len(questions):
            return redirect(url_for('result'))

    return redirect(url_for('quiz'))

@app.route('/finish_session', methods=['POST'])
@login_required
def finish_session():
    if 'shuffled_indexes' in session:
        pos = session.get('current_pos', 0)
        session['last_pos'] = pos
    else:
        current_index = session.get('current_index', 1)
        session['last_index'] = current_index

    score = session.get('score', 0)
    attempted = session.get('attempted', 0)
    percentage = (score / attempted * 100) if attempted > 0 else 0

    email = session.get('email')
    subject = session.get('subject')
    current_index = session.get('current_index', 1)
    if email:
        save_user_session(email, score, attempted, subject, current_index)

    if 'subject' in session:
        subject_name = session['subject']
        if 'revision_indexes' not in session:
            session['revision_indexes'] = {}
        session['revision_indexes'][subject_name] = session.get('current_index', 1)

    user_sessions = get_user_sessions(email) if email else []

    return render_template('finish.html',
                           current_index=session.get('current_pos', session.get('current_index', 1)),
                           score=score,
                           attempted=attempted,
                           percentage=percentage,
                           user_sessions=user_sessions)

@app.route('/explanation/<int:index>')
def explanation(index):
    if 'shuffled_indexes' in session:
        indexes = session['shuffled_indexes']
        pos = session.get('current_pos', 0)
        if 0 <= pos < len(indexes):
            real_index = indexes[pos]
            q = all_questions[real_index]
            return jsonify({
                'explanation': q['explanation'],
                'detailed': q['detailed']
            })
        else:
            return jsonify({'explanation': '', 'detailed': ''})
    else:
        if 0 < index <= len(questions):
            q = questions[index - 1]
            return jsonify({
                'explanation': q['explanation'],
                'detailed': q['detailed']
            })
        return jsonify({'explanation': '', 'detailed': ''})

@app.route('/result')
@login_required
def result():
    score = session.get('score', 0)
    attempted = session.get('attempted', 0)
    percentage = (score / attempted * 100) if attempted > 0 else 0
    total = session.get('total', 0)
    session.pop('last_index', None)
    session.pop('last_pos', None)
    return render_template('result.html', score=score, attempted=attempted, percentage=percentage, total=total)

@app.route('/main')
@login_required
def main_page():
    return render_template('main.html')

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    data = load_ratings()
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '').strip()

    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400

    if rating:
        data['ratings'].append(rating)
    if comment:
        data['comments'].append(comment)

    save_ratings(data)
    return jsonify({"success": True})

@app.route('/get_ratings')
def get_ratings():
    data = load_ratings()
    return jsonify(data)

@app.route('/ratings')
def ratings_page():
    data = load_ratings()
    return render_template('ratings.html', ratings=data)

@app.route('/toggle_comments', methods=['POST'])
def toggle_comments():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    data = load_ratings()
    data['visible'] = not data.get('visible', True)
    save_ratings(data)
    return jsonify({"visible": data['visible']})

@app.route('/vip_login', methods=['GET', 'POST'])
def vip_login():
    error_message = ""
    if request.method == 'POST':
        if request.form.get('password') == VIP_ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('vip_manager'))
        else:
            error_message = "🚫 كلمة مرور خاطئة"
    return render_template('vip_login.html', error_message=error_message)

@app.route('/vip_manager')
def vip_manager():
    if not session.get('is_admin'):
        return redirect(url_for('vip_login'))

    user_counters = {}
    total_users = 0
    over_limit = 0
    active_today_count = 0  # عدد المستخدمين النشطين اليوم

    if os.path.exists(USER_COUNTER_FILE):
        with open(USER_COUNTER_FILE, "r") as f:
            raw_data = json.load(f)

        for encoded_email, count in raw_data.items():
            try:
                email = base64.b64decode(encoded_email.encode()).decode()
            except:
                email = encoded_email
            user_counters[email] = count

        total_users = len(user_counters)
        over_limit = sum(1 for count in user_counters.values() if count >= 200)

    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                sessions_data = json.load(f)
                active_emails_today = {session['email'] for session in sessions_data if session['date'] == today_str}
                active_today_count = len(active_emails_today)
            except:
                active_today_count = 0

    vip_emails = list(full_access_users.keys())

    return render_template(
        "vip_manager.html",
        user_counters=user_counters,
        total_users=total_users,
        over_limit=over_limit,
        full_access_users=full_access_users,
        vip_emails=vip_emails,
        active_today=active_today_count
    )

@app.route('/add_vip', methods=['POST'])
def add_vip():
    if not session.get('is_admin'):
        return redirect(url_for('vip_login'))
    global full_access_users
    email = request.form.get('email')
    full_access_users[email] = "FULL"
    save_vip_users(full_access_users)
    full_access_users = load_vip_users()
    return f"<h3 style='color:green; text-align:center;'>✅ تم إضافة {email} كمستخدم VIP</h3><br><a href='/vip_manager'>رجوع</a>"

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if not session.get('is_admin'):
        return redirect(url_for('vip_login'))

    email = request.form.get('email')
    key = encode_email(email)

    if os.path.exists(USER_COUNTER_FILE):
        with open(USER_COUNTER_FILE, "r") as f:
            data = json.load(f)

        if key in data:
            del data[key]

            with open(USER_COUNTER_FILE, "w") as f:
                json.dump(data, f)

    return redirect(url_for('vip_manager'))

# ---------- Route لجلب كل بيانات المستخدمين للجدول الجديد ----------
@app.route('/get_all_users_info')
def get_all_users_info():
    user_counters = {}
    if os.path.exists(USER_COUNTER_FILE):
        with open(USER_COUNTER_FILE, "r") as f:
            raw_data = json.load(f)
        for encoded_email, count in raw_data.items():
            try:
                email = base64.b64decode(encoded_email.encode()).decode()
            except:
                email = encoded_email
            user_counters[email] = count

    vip_emails = set(load_vip_users().keys())

    sessions_by_user = {}
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                sessions_data = json.load(f)
            except:
                sessions_data = []
        for sess in sessions_data:
            em = sess['email']
            if em not in sessions_by_user:
                sessions_by_user[em] = []
            sessions_by_user[em].append(sess)

    for em in sessions_by_user:
        sessions_by_user[em].sort(key=lambda s: s.get('date', ''), reverse=True)

    all_users = []
    for email in set(list(user_counters.keys()) + list(sessions_by_user.keys())):
        all_users.append({
            "email": email,
            "counter": user_counters.get(email, 0),
            "is_vip": email in vip_emails,
            "sessions": sessions_by_user.get(email, [])
        })

    all_users.sort(key=lambda u: u['sessions'][0]['date'] if u['sessions'] else '', reverse=True)
    return jsonify(all_users)

# ---------- Route مزامنة البيانات مع Google Sheets عند الضغط على الزر ----------
import time
from gsheet_helper import get_sheet

@app.route('/sync_user_data')
def sync_user_data():
    try:
        # --- Sync counters ---
        if os.path.exists(USER_COUNTER_FILE):
            with open(USER_COUNTER_FILE, "r") as f:
                data = json.load(f)
            for encoded_email, count in data.items():
                try:
                    email = base64.b64decode(encoded_email.encode()).decode()
                except:
                    email = encoded_email
                save_counter(email, count)
                time.sleep(0.1)

        # --- Sync VIP users ---
        if os.path.exists(VIP_USERS_FILE):
            with open(VIP_USERS_FILE, "r") as f:
                vips = json.load(f)
            for email in vips:
                save_vip(email, True)
                time.sleep(0.1)

        # --- Sync sessions (احترافي، لا يكرر القراءة) ---
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                sessions_data = json.load(f)

            ws = get_sheet('Sessions')
            all_rows = ws.get_all_values()    # اقرأ كل الجلسات الحالية مرة واحدة فقط!
            existing_pairs = set((row[0], row[1]) for row in all_rows if len(row) > 1)

            for sess in sessions_data:
                session_str = json.dumps(sess, ensure_ascii=False)
                pair = (sess['email'], session_str)
                if pair not in existing_pairs:
                    ws.append_row([sess['email'], session_str])
                    time.sleep(0.1)

        return jsonify({"success": True})

    except Exception as e:
        print("Sync error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False})

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/privacy')
def privacy_page():
    return render_template('privacy.html')

if __name__ == '__main__':
    from os import environ
    port = int(environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
