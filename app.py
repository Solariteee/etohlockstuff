from flask import Flask, render_template, abort
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import markdown
import os
import time
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.context_processor
def inject_css_version():
    css_path = os.path.join(app.static_folder, 'css', 'styles.css')
    try:
        version = int(os.path.getmtime(css_path))
    except OSError:
        version = 1
    return {'css_version': version}

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_CREDENTIALS"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

_cache = {}
CACHE_TTL = 300

def get_data():
    now = time.time()
    if 'data' in _cache and now - _cache['data']['time'] < CACHE_TTL:
        return _cache['data']['value']

    result = sheet.values().get(
        spreadsheetId="1fQ7znFTWrQBqkLbKfsQpBKhujcnXbh2XoESjXZmzlis",
        range="List!A:D",
        valueRenderOption="FORMATTED_VALUE"
    ).execute()
    rows = result.get("values", [])[1:]

    grouped = {}
    for row in rows:
        if len(row) < 3:
            continue
        
        uid = row[0].strip()
        name = row[1].strip() if len(row) > 1 else "Unknown"
        
        try:
            lock_level = int(row[2].strip())
        except:
            continue
        
        desc = row[3].strip() if len(row) > 3 else ""
        image_url = f"/static/assets/users/{name}.webp"

        if not uid.isdigit():
            continue

        key = name.lower()
        if key not in grouped:
            grouped[key] = {
                "name": name,
                "lock_level": lock_level,
                "description": desc,
                "image_url": image_url,
                "accounts": [uid],
            }
        else:
            grouped[key]["accounts"].append(uid)
            if lock_level > grouped[key]["lock_level"]:
                grouped[key]["lock_level"] = lock_level
            if not grouped[key]["description"] and desc:
                grouped[key]["description"] = desc

    data = sorted(grouped.values(), key=lambda x: x["lock_level"], reverse=True)
    _cache['data'] = {'value': data, 'time': now}
    return data

CREDITS = [
    {
        "name": "TheHaloDeveloper",
        "role": "Owner, Staff, Evidence Curator",
        "bio": "Halo built and maintains the RoLock bot and website. He also develops TowerStats.com, sclp.pro, and occasionally contributes to Caleb's Soul Crushing Domain.",
        "image": "/static/assets/users/credits/thehalodeveloper.webp"
    },
    {
        "name": "Solariteee",
        "role": "Staff, Evidence Curator",
        "bio": "Solar advocates for community safety and is a former staff member across multiple fangames, including community manager for EToH 3XS. She now contributes to other communities like TM and works as an experienced QA tester.",
        "image": "/static/assets/users/credits/solariteee.webp"
    },
    {
        "name": "Manager_Magolor",
        "role": "Staff, Evidence Curator",
        "bio": "Lor hunts down exploiters across EToH games and helps keep Caleb's Soul Crushing Domain clean. He also maintains an osu! private server and occasionally works on projects outside of Roblox.",
        "image": "/static/assets/users/credits/manager_magolor.webp"
    },
    {
        "name": "imkostasbtw",
        "role": "Evidence Curator, Former Staff",
        "bio": "Kostas was a former staff member for RoLock and is now an evidence curator. [UPDATE DESC]",
        "image": "/static/assets/users/credits/imkostasbtw.webp"
    },
    {
        "name": "k_tten0",
        "role": "Staff, Evidence Curator",
        "bio": "Lyriffs is a staff member for RoLock and is also an evidence curator. [UPDATE DESC]",
        "image": "/static/assets/users/credits/k_tten0.webp"
    },
    {
        "name": "xXTheR3DGamerXx",
        "role": "Former Staff",
        "bio": "Red was a former staff member for RoLock. [UPDATE DESC]",
        "image": "/static/assets/users/credits/xxther3dgamerxx.webp"
    },
    {
        "name": "LoveliestJacob",
        "role": "Former Staff",
        "bio": "LoveliestJacob was a former staff member for RoLock. [UPDATE DESC]",
        "image": "/static/assets/users/credits/loveliestjacob.webp"
    },
    {
        "name": "obbylordd",
        "role": "Former Staff",
        "bio": "obbylordd was a former staff member for RoLock. [UPDATE DESC]",
        "image": "/static/assets/users/credits/obbylordd.webp"
    }
]

@app.route('/')
def home():
    data = get_data()
    return render_template('home.html',
        player_count=len(data),
        total_accounts=sum(len(u['accounts']) for u in data),
        ll3=sum(1 for u in data if u['lock_level'] == 3),
        ll2=sum(1 for u in data if u['lock_level'] == 2),
        ll1=sum(1 for u in data if u['lock_level'] == 1),
        staff_count=len(CREDITS),
    )

@app.route('/banlist')
def index():
    data = get_data()
    total = sum(len(p["accounts"]) for p in data)
    for user in data:
        user['has_evidence'] = os.path.exists(os.path.join("static", "evidence", f"{user['name']}.md"))
    return render_template('index.html', users=data, total=total)

@app.route('/user/<string:name>')
def user_detail(name):
    data = get_data()
    user = next((u for u in data if u["name"].lower() == name.lower()), None)
    if not user:
        abort(404)

    evidence_html = None
    evidence_path = os.path.join("static", "evidence", f"{user['name']}.md")
    if os.path.exists(evidence_path):
        with open(evidence_path, "r") as f:
            evidence_html = markdown.markdown(f.read(), extensions=["tables", "fenced_code"])

    return render_template('user.html', user=user, evidence_html=evidence_html)

@app.route('/credits')
def credits():
    return render_template('credits.html', credits=CREDITS)

if __name__ == '__main__':
    app.run(debug=True)