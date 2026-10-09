import os, time, hashlib, requests
from dotenv import load_dotenv

load_dotenv()
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "")
if not app.secret_key:
    raise RuntimeError("Missing FLASK_SECRET_KEY. Set it in Render Environment or local .env.")

# Keep Firebase ID/refresh tokens on the server, not inside the browser cookie.
app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR="/tmp/pu_nin_flask_sessions",
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(os.environ.get("RENDER", "").lower() == "true"),
    WTF_CSRF_TIME_LIMIT=3600,
)
Session(app)
CSRFProtect(app)
# Render sits behind a trusted proxy; this helps Flask understand HTTPS requests.
if os.environ.get("RENDER", "").lower() == "true":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
FIREBASE_URL = os.environ.get("FIREBASE_URL", "https://punin-mobile-unlock-default-rtdb.asia-southeast1.firebasedatabase.app").rstrip("/")
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def auth_token():
    return session.get("id_token", "")

def fb_url(path):
    path = path.strip("/")
    return f"{FIREBASE_URL}/{path}.json" if path else f"{FIREBASE_URL}/.json"

def fb_request(method, path, data=None):
    token = auth_token()
    params = {"auth": token} if token else {}
    r = requests.request(method, fb_url(path), params=params, json=data, timeout=15)
    if not r.ok:
        raise RuntimeError(f"Firebase {method} {path}: HTTP {r.status_code} — {r.text[:500]}")
    return r.json() if r.text else None

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("id_token") or not session.get("is_admin"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

def telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "disable_web_page_preview": True},
            timeout=10,
        )
        return r.ok
    except requests.RequestException:
        return False

@app.route("/")
def index():
    if not session.get("id_token"): return redirect(url_for("login"))
    if not session.get("is_admin"): return "Access denied: this Firebase UID is not an admin.", 403
    stats = {}
    errors = []
    for key, path in [("pending","pending_users"),("members","approved_users"),("malware","malware_database"),("threats","threat_intelligence/packages"),("notifications","notifications")]:
        try:
            value = fb_request("GET", path)
            stats[key] = len(value) if isinstance(value, dict) else 0
        except Exception as e:
            stats[key] = "—"; errors.append(str(e))
    return render_template("index.html", stats=stats, errors=errors, email=session.get("email",""))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        password = request.form.get("password","")
        api_key = FIREBASE_API_KEY
        if not api_key:
            flash("Server setup missing FIREBASE_API_KEY.", "error")
            return render_template("login.html")
        try:
            r = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
                json={"email": email, "password": password, "returnSecureToken": True}, timeout=15)
            data = r.json()
            if not r.ok: raise RuntimeError(data.get("error",{}).get("message","Firebase login failed"))
            token, uid = data["idToken"], data["localId"]
            check = requests.get(fb_url(f"admins/{uid}"), params={"auth":token}, timeout=15)
            if not check.ok or check.json() is not True:
                raise RuntimeError("This Firebase account is not listed as an admin.")
            session.clear()
            session.update({"id_token":token,"refresh_token":data.get("refreshToken",""),
                            "expires_at":int(time.time())+int(data.get("expiresIn","3600")),
                            "uid":uid,"email":email,"is_admin":True})
            telegram_alert(f"🔐 PU NIN Web Admin login\nAdmin: {email}\nUID: {uid}")
            return redirect(url_for("index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/pending")
@admin_required
def pending():
    data = fb_request("GET","pending_users") or {}
    return render_template("table.html", title="Pending Users", rows=[{"key":k, **(v if isinstance(v,dict) else {})} for k,v in data.items()], section="pending")

@app.route("/members")
@admin_required
def members():
    data = fb_request("GET","approved_users") or {}
    return render_template("table.html", title="Approved Members", rows=[{"key":k, **(v if isinstance(v,dict) else {})} for k,v in data.items()], section="members")

@app.route("/action/<section>/<path:key>/<action>", methods=["POST"])
@admin_required
def action(section,key,action):
    try:
        if section == "pending" and action == "delete":
            fb_request("DELETE",f"pending_users/{key}")
            telegram_alert(f"🗑️ PU NIN: Pending registration rejected\nUsername: {key}\nBy: {session.get('email')}")
            flash(f"Deleted pending request: {key}", "success")
        elif section == "members" and action == "delete":
            fb_request("DELETE",f"approved_users/{key}")
            telegram_alert(f"🗑️ PU NIN: Member deleted\nUsername: {key}\nBy: {session.get('email')}")
            flash(f"Deleted member: {key}", "success")
        else:
            raise RuntimeError("Unsupported action.")
    except Exception as e: flash(str(e),"error")
    return redirect(url_for(section))

@app.route("/approve/<path:username>", methods=["POST"])
@admin_required
def approve(username):
    try:
        pending_data = fb_request("GET",f"pending_users/{username}")
        if not isinstance(pending_data,dict): raise RuntimeError("Pending request not found.")
        duration = request.form.get("duration","3 Months")
        expiry = request.form.get("expiry_date","")
        if not expiry: raise RuntimeError("Expiry date is required.")
        payload = {"email":pending_data.get("email",""), "password":pending_data.get("password",""),
                   "license_key": "PUNIN-"+os.urandom(8).hex().upper(), "duration":duration,
                   "expiry_date":expiry, "status":"ACTIVE", "activated_at":time.strftime("%Y-%m-%d %H:%M:%S"),
                   "hwid":"", "last_login_time":""}
        fb_request("PUT",f"approved_users/{username}",payload)
        fb_request("DELETE",f"pending_users/{username}")
        telegram_alert(f"✅ PU NIN: Registration approved\nUsername: {username}\nPlan: {duration}\nExpiry: {expiry}\nBy: {session.get('email')}")
        flash(f"Approved {username}.","success")
    except Exception as e: flash(str(e),"error")
    return redirect(url_for("pending"))

@app.route("/update", methods=["GET","POST"])
@admin_required
def update():
    if request.method == "POST":
        payload = {"version":request.form.get("version","").strip(),
                   "min_supported_version":request.form.get("min_supported_version","").strip(),
                   "download_url":request.form.get("download_url","").strip(),
                   "sha256":request.form.get("sha256","").strip().lower(),
                   "updated_at":time.strftime("%Y-%m-%d %H:%M:%S"),
                   "notes":request.form.get("notes","").strip()}
        if not payload["version"] or not payload["download_url"].startswith("https://") or len(payload["sha256"]) != 64:
            flash("Version, HTTPS URL and 64-character SHA-256 are required.","error")
        else:
            try:
                fb_request("PUT","app_version",payload)
                telegram_alert(f"🚀 PU NIN: Client update published\nVersion: {payload['version']}\nMinimum: {payload['min_supported_version']}\nBy: {session.get('email')}")
                flash("Update manifest published.","success")
            except Exception as e: flash(str(e),"error")
    data = fb_request("GET","app_version") or {}
    return render_template("update.html", data=data)

@app.route("/notify", methods=["GET","POST"])
@admin_required
def notify():
    if request.method == "POST":
        title=request.form.get("title","").strip()
        message=request.form.get("message","").strip()
        if title and message:
            try:
                item={"title":title,"message":message,"created_at":time.strftime("%Y-%m-%d %H:%M:%S")}
                fb_request("POST","notifications",item)
                telegram_alert(f"📣 PU NIN Customer Notice\n{title}\n{message}")
                flash("Notification sent.","success")
            except Exception as e: flash(str(e),"error")
    data=fb_request("GET","notifications") or {}
    rows=[{"key":k,**(v if isinstance(v,dict) else {})} for k,v in data.items()]
    return render_template("notify.html",rows=rows)

@app.route("/health")
def health():
    return jsonify({"status":"ok","app":"PU NIN Web Admin"}),200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
