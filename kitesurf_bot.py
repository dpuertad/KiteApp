#!/usr/bin/env python3
"""
Automated Kitesurf Morning Briefing Assistant - Multi-User Cloud Edition
- Multi-User Isolated Profiles: Every friend has their own private quiver, weight, spot & briefings.
- Instant Onboarding via QR Code or Link (https://t.me/KiteForecast_bot).
- Spot-Aware Local Time: Calculates real solar/civil time of the spot.
- 1-Tap Phone GPS Linking via Telegram native button.
- Real-time /report & /now commands with current wind, gusts, tides & instant kite recommendation.
- Strictly recommends ONLY from the kites you have with you ("you have what you have").
- Dead-simple slot-based setup: /kite 1 (brand)Duotone (model)RebelSLS (size)11 or /kite 1 Duotone Rebel SLS 11
- Multi-provider resilient weather: Open-Meteo + Met.no fallback + Marine Tides.
"""

import os
import sys
import re
import json
import time
import math
import ssl
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from kite_catalog import lookup_kite_specs, KITE_CATALOG

def load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass

load_env_file()



if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forecast_cache.json")
USERS_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users_web_db.json")
PUBLIC_SPOTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_spots_db.json")

def load_public_spots() -> list:
    if os.path.exists(PUBLIC_SPOTS_FILE):
        try:
            with open(PUBLIC_SPOTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_public_spots(spots: list):
    try:
        with open(PUBLIC_SPOTS_FILE, "w", encoding="utf-8") as f:
            json.dump(spots, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving public_spots_db: {e}")

GUST_WARNING_THRESHOLD_KTS = 30
SSL_CTX = ssl._create_unverified_context()

APPROVED_BETA_FILE = "approved_beta_riders.json"
DEFAULT_BETA_EMAILS = ["d_puerta@hotmail.com", "admin.holygust@gmail.com", "d.puertadiaz@gmail.com"]

def load_approved_beta_emails() -> set:
    emails = set(DEFAULT_BETA_EMAILS)
    if os.path.exists(APPROVED_BETA_FILE):
        try:
            with open(APPROVED_BETA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    emails.update(data)
        except Exception:
            pass
    return emails

def save_approved_beta_email(email: str):
    emails = load_approved_beta_emails()
    emails.add(email.strip().lower())
    try:
        with open(APPROVED_BETA_FILE, "w", encoding="utf-8") as f:
            json.dump(list(emails), f, indent=2)
    except Exception as e:
        print(f"Error saving approved beta email: {e}")

def load_users_db() -> dict:
    db = {"users": {}, "feedback": []}
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            pass
    
    # Auto-reconcile any riders seen in spot telemetry so no registered rider is ever lost across restarts/deploys
    try:
        telemetry_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spot_telemetry_db.json")
        if os.path.exists(telemetry_file):
            with open(telemetry_file, "r", encoding="utf-8") as f:
                t_data = json.load(f)
            changed = False
            for v in t_data.get("spot_views", []):
                em = (v.get("email") or "").strip().lower()
                if em and "@" in em and em != "anonymous":
                    if em not in db.get("users", {}):
                        db.setdefault("users", {})[em] = {
                            "email": em,
                            "name": v.get("rider_name") or em.split("@")[0].title(),
                            "nationality": v.get("nationality") if v.get("nationality") != "Undefined" else "",
                            "registered_at": v.get("timestamp"),
                            "last_login": v.get("timestamp"),
                            "gear": [],
                            "boards": [],
                            "weight_kg": 75.0,
                            "level": "intermediate",
                            "board": "Twintip",
                            "spot": {"name": v.get("spot_name"), "lat": v.get("lat"), "lon": v.get("lon")}
                        }
                        changed = True
            if changed:
                save_users_db(db)
    except Exception as e:
        print(f"Error reconciling users from telemetry: {e}")

    # Auto-apply approved beta emails unless user opted out
    approved_set = load_approved_beta_emails()
    for em, u in db.get("users", {}).items():
        if u.get("beta_status") == "left":
            u["is_beta_rider"] = False
            continue
        if em in approved_set:
            u["is_beta_rider"] = True
            u["beta_status"] = "approved"
    return db

def save_users_db(db: dict):
    try:
        with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving users_web_db: {e}")

def hash_password(password: str, salt: str = None) -> tuple:
    import hashlib, secrets
    if not salt:
        salt = secrets.token_hex(8)
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return h, salt

def send_admin_telegram(text: str, reply_markup: dict = None) -> bool:
    try:
        config = load_config()
        token = config.get("telegram_token") or os.getenv("TELEGRAM_BOT_TOKEN")
        admin_id = str(config.get("admin_id", os.getenv("CHAT_ID", "7424865438")))
        if not token or not admin_id:
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": admin_id,
            "text": text
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"send_admin_telegram error: {e}")
        return False

def get_beta_decision_token(email: str) -> str:
    import hashlib
    salt = "holygust_beta_secret_2026"
    return hashlib.sha256(f"{email.lower().strip()}_{salt}".encode("utf-8")).hexdigest()[:16]

def approve_beta_rider(email: str):
    db = load_users_db()
    from datetime import datetime, timezone
    email_clean = email.strip().lower()
    if email_clean not in db.get("users", {}):
        db.setdefault("users", {})[email_clean] = {
            "email": email_clean,
            "name": email_clean.split("@")[0].title(),
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "gear": [],
            "boards": [],
            "weight_kg": 74.0,
            "favorite_spots": []
        }
    user = db["users"][email_clean]
    user["is_beta_rider"] = True
    user["beta_status"] = "approved"
    user["beta_approved_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    save_approved_beta_email(email_clean)
    save_users_db(db)
    rider_name = user.get("name") or email_clean.split("@")[0].title()
    
    # Send welcome email via Resend
    html_welcome = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin: 0; padding: 24px 0; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <div style="max-width: 520px; margin: 0 auto; background: #0f172a; border-radius: 20px; overflow: hidden; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
    <div style="padding: 26px 20px; text-align: center; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
      <div style="font-size: 32px; margin-bottom: 6px;">⚡</div>
      <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Welcome to the Beta Crew!</h1>
      <p style="margin: 4px 0 0; color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 600;">HolyGust Secret Dev Lab</p>
    </div>
    <div style="padding: 30px 24px; color: #f8fafc;">
      <h2 style="margin: 0 0 12px; font-size: 18px; color: #ffffff; font-weight: 700;">Aloha {rider_name},</h2>
      <p style="margin: 0 0 16px; font-size: 14px; line-height: 1.6; color: #94a3b8;">
        Your application to become a HolyGust Beta Rider has been <strong>approved</strong> by the HolyGust team!
      </p>
      <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 16px; margin: 20px 0; text-align: center;">
        <span style="display: inline-block; background: #f59e0b; color: #0f172a; font-weight: 800; font-size: 12px; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.5px; text-transform: uppercase;">
          ⚡ Beta Rider Badge Activated
        </span>
        <p style="margin: 10px 0 0; font-size: 13px; color: #fde68a;">
          You now have exclusive early access to experimental wind models, prototype gear physics, and upcoming features before anyone else.
        </p>
      </div>
      <div style="text-align: center; margin: 28px 0;">
        <a href="https://beta.holygust.com" style="display: inline-block; background: #f59e0b; color: #0f172a; font-weight: 800; font-size: 14px; padding: 13px 32px; border-radius: 12px; text-decoration: none; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4);">
          Launch Beta Lab (beta.holygust.com)
        </a>
      </div>
      <p style="margin: 20px 0 0; font-size: 12px; line-height: 1.5; color: #64748b; text-align: center;">
        Use your registered email (<strong>{email_clean}</strong>) to log in. Got feedback or spot suggestions? Reach out to our team directly via the feedback button in the app!
      </p>
    </div>
  </div>
</body>
</html>"""
    try:
        send_email_via_resend(email_clean, "⚡ You're in! Welcome to HolyGust Beta Crew", html_welcome)
    except Exception as e:
        print(f"Error sending beta welcome email: {e}")
    return True, rider_name

def decline_beta_rider(email: str):
    db = load_users_db()
    email_clean = email.strip().lower()
    if email_clean in db.get("users", {}):
        db["users"][email_clean]["is_beta_rider"] = False
        db["users"][email_clean]["beta_status"] = "declined"
        save_users_db(db)
    return True

def remove_approved_beta_email(email: str):
    email_clean = email.strip().lower()
    emails = load_approved_beta_emails()
    if email_clean in emails:
        emails.remove(email_clean)
        try:
            with open(APPROVED_BETA_FILE, "w", encoding="utf-8") as f:
                json.dump(list(emails), f, indent=2)
        except Exception as e:
            print(f"Error removing approved beta email: {e}")

def leave_beta_program(email: str) -> tuple:
    db = load_users_db()
    email_clean = email.strip().lower()
    user = db.get("users", {}).get(email_clean)
    rider_name = (user.get("name") if user else None) or email_clean.split("@")[0].title()
    
    if user:
        user["is_beta_rider"] = False
        user["beta_status"] = "left"
        save_users_db(db)
    
    remove_approved_beta_email(email_clean)
    
    # Notify Daniel via Telegram
    tele_text = (
        f"ℹ️ BETA PROGRAM UPDATE\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Rider: {rider_name}\n"
        f"📧 Email: {email_clean}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Rider has opted out of the Beta program and returned to the production version."
    )
    send_admin_telegram(tele_text)
    
    return True, rider_name

def handle_telegram_callback(cb: dict, token: str, config: dict):
    try:
        cb_id = cb.get("id")
        cb_data = cb.get("data", "")
        from_user = cb.get("from", {})
        msg = cb.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        msg_id = msg.get("message_id")
        
        if cb_data.startswith("approve_beta:"):
            email = cb_data.split("approve_beta:", 1)[1].strip().lower()
            _, rider_name = approve_beta_rider(email)
            
            # Answer callback toast
            ans_payload = {"callback_query_id": cb_id, "text": f"✅ {rider_name} approved as ⚡ Beta Rider!", "show_alert": True}
            try:
                req = urllib.request.Request(f"https://api.telegram.org/bot{token}/answerCallbackQuery", data=json.dumps(ans_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, context=SSL_CTX, timeout=8)
            except Exception as e:
                print(f"answerCallbackQuery error: {e}")
            
            # Edit original message
            if chat_id and msg_id:
                orig_text = msg.get("text", "")
                edit_payload = {
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "text": f"""{orig_text}\n\n✅ APPROVED by HolyGust Team! ⚡ Beta Rider badge active & welcome email sent.""",
                    "reply_markup": {"inline_keyboard": []}
                }
                try:
                    req_edit = urllib.request.Request(f"https://api.telegram.org/bot{token}/editMessageText", data=json.dumps(edit_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(req_edit, context=SSL_CTX, timeout=8)
                except Exception as e:
                    print(f"editMessageText error: {e}")
                    
        elif cb_data.startswith("decline_beta:"):
            email = cb_data.split("decline_beta:", 1)[1].strip().lower()
            decline_beta_rider(email)
            
            ans_payload = {"callback_query_id": cb_id, "text": f"❌ Declined beta request for {email}", "show_alert": False}
            try:
                req = urllib.request.Request(f"https://api.telegram.org/bot{token}/answerCallbackQuery", data=json.dumps(ans_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, context=SSL_CTX, timeout=8)
            except Exception as e:
                print(f"answerCallbackQuery error: {e}")
                
            if chat_id and msg_id:
                orig_text = msg.get("text", "")
                edit_payload = {
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "text": f"""{orig_text}\n\n❌ DECLINED by HolyGust Team.""",
                    "reply_markup": {"inline_keyboard": []}
                }
                try:
                    req_edit = urllib.request.Request(f"https://api.telegram.org/bot{token}/editMessageText", data=json.dumps(edit_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(req_edit, context=SSL_CTX, timeout=8)
                except Exception as e:
                    print(f"editMessageText error: {e}")
    except Exception as e:
        print(f"handle_telegram_callback error: {e}")

def notify_admin_telegram(text: str):
    send_admin_telegram(text)

def send_email_via_resend(to_email: str, subject: str, html_body: str) -> bool:
    try:
        config = load_config()
        api_key = os.getenv("RESEND_API_KEY") or config.get("resend_api_key") or os.getenv("RESEND_API_KEY")
        from_email = os.getenv("RESEND_FROM_EMAIL") or config.get("resend_from_email") or "HolyGust <noreply@holygust.com>"
        payload = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "HolyGust/1.0"
            }
        )
        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=12) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                print(f"[Resend] Email sent to {to_email}: {res_data}")
                return True
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8")
            print(f"[Resend] HTTP {he.code}: {err_body}")
            if he.code == 403 and "not verified" in err_body:
                # If custom domain pending verification, fallback to onboarding@resend.dev sandbox
                print("[Resend] Domain holygust.com pending verification; falling back to onboarding@resend.dev...")
                payload["from"] = "HolyGust <onboarding@resend.dev>"
                data2 = json.dumps(payload).encode("utf-8")
                req2 = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=data2,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "HolyGust/1.0"
                    }
                )
                with urllib.request.urlopen(req2, context=SSL_CTX, timeout=12) as resp2:
                    res_data2 = json.loads(resp2.read().decode("utf-8"))
                    print(f"[Resend] Sandbox fallback sent: {res_data2}")
                    return True
            return False
    except Exception as e:
        print(f"[Resend] Error sending email: {e}")
        return False

REPLY_KEYBOARD = {
    "keyboard": [
        [{"text": "📍 Send Current Location & Report", "request_location": True}],
        [{"text": "/report"}, {"text": "/report tomorrow"}, {"text": "/kites"}],
        [{"text": "📱 Open Interactive Web App"}]
    ],
    "resize_keyboard": True,
    "persistent": True
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            # Migration check: if old single-user config format, convert to multi-user
            if "users" not in cfg:
                old_chat_id = str(cfg.get("chat_id", "7424865438"))
                cfg = {
                    "telegram_token": cfg.get("telegram_token", "9295432294:AAFK0ZZz_Gww6ewx7D-YpbYTvfbHdU9ogyc"),
                    "admin_id": old_chat_id,
                    "users": {
                        old_chat_id: {
                            "user_id": int(old_chat_id),
                            "rider_name": cfg.get("rider_name", "Daniel"),
                            "rider_weight_kg": cfg.get("rider_weight_kg", 75.0),
                            "board_type": cfg.get("board_type", "Twintip"),
                            "spot": cfg.get("spot", {
                                "name": "Cumbuco, Brazil",
                                "lat": -3.6247,
                                "lon": -38.7297,
                                "timezone": "America/Fortaleza"
                            }),
                            "inventory": cfg.get("inventory", []),
                            "morning_briefing": True
                        }
                    }
                }
                save_config(cfg)
            return cfg

    # Default bootstrap
    default_cfg = {
        "telegram_token": os.getenv("TELEGRAM_TOKEN", "9295432294:AAFK0ZZz_Gww6ewx7D-YpbYTvfbHdU9ogyc"),
        "admin_id": os.getenv("CHAT_ID", "7424865438"),
        "users": {
            "7424865438": {
                "user_id": 7424865438,
                "rider_name": "Daniel",
                "rider_weight_kg": 75.0,
                "board_type": "Twintip",
                "spot": {
                    "name": "Cumbuco, Brazil",
                    "lat": -3.6247,
                    "lon": -38.7297,
                    "timezone": "America/Fortaleza"
                },
                "inventory": [],
                "morning_briefing": True
            }
        }
    }
    save_config(default_cfg)
    return default_cfg


def save_config(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_or_create_user(config: dict, user_id: int, first_name: str = "Kiter") -> tuple[dict, bool]:
    """Retrieves existing user profile or initializes a new one for friends."""
    uid = str(user_id)
    users = config.setdefault("users", {})
    if uid in users:
        return users[uid], False

    # Initialize new profile for friend - start with completely empty quiver
    new_user = {
        "user_id": user_id,
        "rider_name": first_name or "Kiter",
        "rider_weight_kg": 75.0,
        "board_type": "Twintip",
        "spot": {
            "name": "Cumbuco, Brazil",
            "lat": -3.6247,
            "lon": -38.7297,
            "timezone": "America/Fortaleza"
        },
        "inventory": [],
        "morning_briefing": True
    }
    users[uid] = new_user
    save_config(config)
    return new_user, True


def get_spot_local_now(spot: dict, utc_offset_seconds: int = None) -> datetime:
    if utc_offset_seconds is not None:
        return datetime.now(timezone(timedelta(seconds=utc_offset_seconds)))
    tz_name = spot.get("timezone", "auto")
    if tz_name and tz_name != "auto":
        try:
            return datetime.now(ZoneInfo(tz_name))
        except Exception:
            pass
    lon = spot.get("lon", -38.7297)
    approx_hours = round(lon / 15.0)
    return datetime.now(timezone(timedelta(hours=approx_hours)))


def round_knots(kts) -> int:
    """Rounds wind knots to a plain integer.
    Rounds down if decimal <= .4, rounds up if decimal >= .6 (or .5).
    Example: 15.1 -> 15, 15.4 -> 15, 15.6 -> 16, 16.1 -> 16.
    """
    try:
        val = float(kts)
        return int(math.floor(val + 0.5))
    except (ValueError, TypeError):
        return 0


def degrees_to_cardinal(deg: float) -> str:
    dirs = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    idx = int((deg + 11.25) / 22.5) % 16
    return dirs[idx]


# ---------------------------------------------------------
# SHORELINE SAFETY, WIND STABILITY, WETSUIT & CONSENSUS
# ---------------------------------------------------------
DEFAULT_BEACH_ORIENTATIONS = {
    "cumbuco": 40.0,        # NE
    "taiba": 35.0,          # NNE
    "paracuru": 45.0,       # NE
    "ilha do guajiru": 45.0,# NE
    "jericoacoara": 330.0,  # NNW
    "tarifa": 220.0,        # SW (Los Lances / Valdevaqueros)
    "dakhla": 270.0,        # W (Lagoon)
    "leucate": 110.0,       # ESE (La Franqui)
    "pozo": 90.0,           # E
    "bonaire": 260.0,       # W (Atlantis)
    "el gouna": 90.0,       # E
    "cape town": 250.0,     # WSW (Bloubergstrand)
    "cabarete": 30.0,       # NNE (Kite Beach)
    "maui": 350.0,          # N (Kanaha)
}

CARDINAL_DEGREES = {
    "N": 0.0, "NNE": 22.5, "NE": 45.0, "ENE": 67.5,
    "E": 90.0, "ESE": 112.5, "SE": 135.0, "SSE": 157.5,
    "S": 180.0, "SSW": 202.5, "SW": 225.0, "WSW": 247.5,
    "W": 270.0, "WNW": 292.5, "NW": 315.0, "NNW": 337.5
}



def resolve_spot_model_and_angle(lat: float, lon: float, country_code: str = "", name: str = ""):
    cc = (country_code or "").upper()
    n_lower = (name or "").lower()
    
    # 1. Model resolution
    if cc in ["IT", "DE", "CH", "AT"] or "garda" in n_lower or "como" in n_lower or "silvaplana" in n_lower or (44.0 <= lat <= 55.0 and 5.0 <= lon <= 17.0):
        preferred_model = "icon_seamless"
        model_label = "DWD ICON-D2 (2km) & ICON-EU"
    elif cc == "FR" or "leucate" in n_lower or "hyeres" in n_lower or (42.0 <= lat <= 51.5 and -5.0 <= lon <= 8.5):
        preferred_model = "best_match"
        model_label = "Météo-France AROME (1.3km) & ECMWF"
    elif cc in ["ES", "PT", "GR", "TR", "HR"] or "tarifa" in n_lower or "pozo" in n_lower:
        preferred_model = "icon_seamless"
        model_label = "DWD ICON-EU (7km) & ECMWF (9km)"
    elif cc in ["US", "CA"] or "hood river" in n_lower or "maui" in n_lower or "hatteras" in n_lower:
        preferred_model = "best_match"
        model_label = "NOAA HRRR (3km) & GFS (13km)"
    elif cc == "BR" or "cumbuco" in n_lower or "taiba" in n_lower or "prea" in n_lower:
        preferred_model = "best_match"
        model_label = "ECMWF IFS (9km) + Thermal Venturi"
    else:
        preferred_model = "best_match"
        model_label = "ECMWF IFS (9km) High-Resolution"

    # 2. Beach Angle resolution
    b_angle = resolve_beach_angle(name)
    if "dongo" in n_lower or "como" in n_lower:
        b_angle = 100.0  # Lake Como western shore facing ESE
    elif "garda" in n_lower or "torbole" in n_lower:
        b_angle = 200.0  # Lake Garda northern shore facing SSW

    return preferred_model, model_label, b_angle

def resolve_beach_angle(spot_name: str, custom_angle=None) -> float:
    if custom_angle is not None:
        if isinstance(custom_angle, (int, float)):
            return float(custom_angle)
        if isinstance(custom_angle, str) and custom_angle.upper() in CARDINAL_DEGREES:
            return CARDINAL_DEGREES[custom_angle.upper()]
        try:
            return float(custom_angle)
        except (ValueError, TypeError):
            pass
    clean_name = (spot_name or "").lower()
    for key, angle in DEFAULT_BEACH_ORIENTATIONS.items():
        if key in clean_name:
            return float(angle)
    try:
        from kite_spots import GLOBAL_KITE_SPOTS
        for s in GLOBAL_KITE_SPOTS:
            if s["id"] in clean_name or s["name"].lower() in clean_name or any(a in clean_name for a in s.get("aliases", [])):
                return float(s.get("beach_angle", 45.0))
    except Exception:
        pass
    return 45.0  # default generic NE coast


def calculate_shoreline_status(wind_deg: float, beach_deg: float) -> dict:
    """Calculates wind angle relative to beach coastline."""
    diff = abs((wind_deg - beach_deg + 180.0) % 360.0 - 180.0)
    if diff <= 30.0:
        return {
            "type": "Onshore",
            "tag": "🟡 Onshore",
            "pill": "Onshore",
            "badge_color": "amber",
            "description": "Direct onshore: choppy shorebreak, harder waterstarts",
            "is_safe": True,
            "warning": False,
            "danger": False,
            "relative_angle": round(diff)
        }
    elif diff <= 75.0:
        return {
            "type": "Side-Onshore",
            "tag": "🟢 Side-Onshore",
            "pill": "Side-Onshore",
            "badge_color": "emerald",
            "description": "Ideal & safe: prime riding angle, pushes back to shore",
            "is_safe": True,
            "warning": False,
            "danger": False,
            "relative_angle": round(diff)
        }
    elif diff <= 105.0:
        return {
            "type": "Sideshore",
            "tag": "🟢 Sideshore",
            "pill": "Sideshore",
            "badge_color": "emerald",
            "description": "Safe & clean: parallel to beach, smooth speed runs",
            "is_safe": True,
            "warning": False,
            "danger": False,
            "relative_angle": round(diff)
        }
    elif diff <= 150.0:
        return {
            "type": "Side-Offshore",
            "tag": "🟠 Side-Offshore",
            "pill": "Side-Offshore",
            "badge_color": "orange",
            "description": "Caution: blowing away from beach, safety cover advised",
            "is_safe": False,
            "warning": True,
            "danger": False,
            "relative_angle": round(diff)
        }
    else:
        return {
            "type": "Offshore",
            "tag": "🚨 Offshore Hazard",
            "pill": "Offshore Hazard",
            "badge_color": "rose",
            "description": "DANGER: blowing out to open sea! Rescue boat mandatory",
            "is_safe": False,
            "warning": True,
            "danger": True,
            "relative_angle": round(diff)
        }


def calculate_stability_score(wind_kts: float, gust_kts: float) -> dict:
    """Calculates 1-10 wind punchiness / stability score comparing gusts to sustained wind."""
    if wind_kts <= 4:
        return {
            "score": 10,
            "rating": "10/10",
            "label": "Calm / Light",
            "pill": "10/10 Calm",
            "badge_color": "sky",
            "description": "Sub-planing breeze, ultra calm"
        }
    ratio = gust_kts / max(wind_kts, 1.0)
    if ratio <= 1.15:
        return {
            "score": 10,
            "rating": "10/10",
            "label": "Butter Smooth",
            "pill": "10/10 Smooth",
            "badge_color": "emerald",
            "description": "Ultra smooth laminar flow (trade winds), steady pull"
        }
    elif ratio <= 1.25:
        return {
            "score": 9,
            "rating": "9/10",
            "label": "Steady & Clean",
            "pill": "9/10 Steady",
            "badge_color": "emerald",
            "description": "Consistent steady wind with minimal gust variation"
        }
    elif ratio <= 1.35:
        return {
            "score": 8,
            "rating": "8/10",
            "label": "Clean Breezes",
            "pill": "8/10 Clean",
            "badge_color": "teal",
            "description": "Comfortable steady wind, gentle predictable pulses"
        }
    elif ratio <= 1.45:
        return {
            "score": 6,
            "rating": "6/10",
            "label": "Moderate Gusts",
            "pill": "6/10 Moderate",
            "badge_color": "amber",
            "description": "Noticeable gusts, standard bar sheeting adjustments"
        }
    elif ratio <= 1.60:
        return {
            "score": 5,
            "rating": "5/10",
            "label": "Punchy / Gusty",
            "pill": "5/10 Punchy",
            "badge_color": "amber",
            "description": "Punchy gusts: ride conservatively and keep depowered"
        }
    elif ratio <= 1.80:
        return {
            "score": 3,
            "rating": "3/10",
            "label": "Turbulent & Shifty",
            "pill": "3/10 Turbulent",
            "badge_color": "orange",
            "description": "Heavy turbulence and gust spikes, hold edge firmly"
        }
    else:
        return {
            "score": 2,
            "rating": "2/10",
            "label": "Squally & Volatile",
            "pill": "2/10 Squally",
            "badge_color": "rose",
            "description": "Violent gust differentials, advanced storm riding only"
        }


def calculate_wetsuit_guide(water_temp, air_temp, wind_kts=15.0, apparent_temp=None) -> dict:
    """
    Thermal comfort and wetsuit recommendation based on:
    1. Water temperature (conductive heat loss during immersion)
    2. Air temperature & wind speed (convective wind chill)
    3. Latent heat of evaporation on wet neoprene/skin
    """
    w_temp = float(water_temp) if water_temp is not None else (float(air_temp) - 1.5 if air_temp is not None else 26.0)
    a_temp = float(air_temp) if air_temp is not None else w_temp
    w_speed = max(0.0, float(wind_kts or 14.0))

    v_kmh = w_speed * 1.852
    if apparent_temp is not None:
        dry_apparent = float(apparent_temp)
    elif v_kmh > 5.0 and a_temp < 28.0:
        dry_apparent = 13.12 + 0.6215 * a_temp - 11.37 * (v_kmh ** 0.16) + 0.3965 * a_temp * (v_kmh ** 0.16)
    else:
        dry_apparent = a_temp

    # Evaporative cooling penalty on wet skin/neoprene:
    if w_speed > 8.0 and a_temp < 28.0:
        evap_penalty = min(4.5, (w_speed / 25.0) * 2.8)
    else:
        evap_penalty = 0.0

    feels_like_wet = round(dry_apparent - evap_penalty, 1)

    # Limiting factor: cold wind chill freezes exposed skin/extremities,
    # while cold water drains core heat during immersion.
    limiting_cold = min(w_temp, feels_like_wet)
    milder = max(w_temp, feels_like_wet)
    
    # 65% weight on primary heat sink (colder medium) + 35% on milder
    rider_index = round((limiting_cold * 0.65) + (milder * 0.35), 1)

    w_display = round(w_temp, 1)
    chill_display = round(feels_like_wet, 1)
    a_display = round(a_temp, 1)

    # Thresholds:
    if rider_index >= 24.5 and feels_like_wet >= 22.0 and w_temp >= 23.5:
        return {
            "wetsuit": "Boardshorts & Lycra",
            "gear": "Boardshorts / Bikini & UV Lycra",
            "icon": "🩳",
            "tag": "🩳 Boardshorts & Lycra",
            "pill": "Boardshorts & Lycra",
            "badge_color": "emerald",
            "water_temp": w_display,
            "air_temp": a_display,
            "wind_chill": chill_display,
            "rider_index": rider_index,
            "limiting_factor": "warm",
            "advice": f"Tropical warm water ({w_display}°C) & air ({a_display}°C) — No neoprene needed, wear rashguard & sunscreen"
        }
    elif rider_index >= 20.5 and feels_like_wet >= 19.0:
        return {
            "wetsuit": "2mm Shorty",
            "gear": "2mm Shorty / Neoprene Top",
            "icon": "🏄",
            "tag": "🏄 2mm Shorty / Top",
            "pill": "2mm Shorty",
            "badge_color": "teal",
            "water_temp": w_display,
            "air_temp": a_display,
            "wind_chill": chill_display,
            "rider_index": rider_index,
            "limiting_factor": "mild",
            "advice": f"Pleasant water ({w_display}°C) & mild air ({a_display}°C) — 2mm shorty or top protects from mild breeze"
        }
    elif w_temp > 15.5 and rider_index >= 15.5:
        # e.g. Tarifa in Nov: water 19.8C, chill 14.8C -> 3/2mm full steamer protects from wind chill
        return {
            "wetsuit": "3/2mm Fullsuit",
            "gear": "3/2mm Full Wetsuit (Steamer)",
            "icon": "🧥",
            "tag": "🏄 3/2mm Fullsuit",
            "pill": "3/2mm Fullsuit",
            "badge_color": "sky",
            "water_temp": w_display,
            "air_temp": a_display,
            "wind_chill": chill_display,
            "rider_index": rider_index,
            "limiting_factor": "wind_chill" if feels_like_wet < w_temp else "water",
            "advice": f"Cool wind chill (feels {chill_display}°C) & {w_display}°C sea — 3/2mm full steamer required to prevent evaporative wind cooling"
        }
    elif rider_index >= 11.5 or w_temp >= 13.5:
        # e.g. Cape Town: water 15C
        return {
            "wetsuit": "4/3mm Steamer",
            "gear": "4/3mm Sealed Steamer",
            "icon": "❄️",
            "tag": "❄️ 4/3mm Steamer",
            "pill": "4/3mm Steamer",
            "badge_color": "indigo",
            "water_temp": w_display,
            "air_temp": a_display,
            "wind_chill": chill_display,
            "rider_index": rider_index,
            "limiting_factor": "cold_water" if w_temp < feels_like_wet else "cold_wind",
            "advice": f"Cold session (water {w_display}°C, chill {chill_display}°C) — 4/3mm sealed wetsuit recommended"
        }
    else:
        return {
            "wetsuit": "5/4mm + Booties",
            "gear": "5/4mm Wetsuit + Booties & Hood",
            "icon": "🧊",
            "tag": "🧊 5/4mm + Booties",
            "pill": "5/4mm + Booties",
            "badge_color": "purple",
            "water_temp": w_display,
            "air_temp": a_display,
            "wind_chill": chill_display,
            "rider_index": rider_index,
            "limiting_factor": "frigid",
            "advice": f"Frigid conditions (water {w_display}°C, chill {chill_display}°C) — 5/4mm hooded suit and booties mandatory"
        }


def calculate_model_consensus(ecmwf_val, gfs_val, icon_val) -> dict:
    """Calculates forecast consensus and confidence percentage across ECMWF, GFS, and ICON."""
    models = [ecmwf_val, gfs_val, icon_val]
    valid = [float(m) for m in models if m is not None]
    if len(valid) < 2:
        return {
            "confidence_pct": 85,
            "rating": "85%",
            "label": "Good Agreement",
            "tag": "🎯 85% Confidence",
            "pill": "85% Confidence",
            "badge_color": "emerald",
            "spread_kts": 1.0,
            "models": {
                "ecmwf": round_knots(ecmwf_val) if ecmwf_val is not None else None,
                "gfs": round_knots(gfs_val) if gfs_val is not None else None,
                "icon": round_knots(icon_val) if icon_val is not None else None
            },
            "description": "Standard forecast agreement"
        }
    mean = sum(valid) / len(valid)
    variance = sum((x - mean) ** 2 for x in valid) / len(valid)
    spread = math.sqrt(variance)

    if spread <= 1.5:
        pct = 95
        label = "High Consensus"
        desc = "All global models agree (ECMWF, GFS, ICON)"
        color = "emerald"
    elif spread <= 2.8:
        pct = 85
        label = "Good Agreement"
        desc = "Strong consensus across major models"
        color = "teal"
    elif spread <= 4.5:
        pct = 70
        label = "Moderate Spread"
        desc = "Minor model variance — slight timing shifts possible"
        color = "amber"
    else:
        pct = 55
        label = "Volatile Divergence"
        desc = "High model divergence — track station updates"
        color = "rose"

    return {
        "confidence_pct": pct,
        "rating": f"{pct}%",
        "label": label,
        "tag": f"🎯 {pct}% {label}",
        "pill": f"{pct}% Confidence",
        "badge_color": color,
        "spread_kts": round(spread, 1),
        "models": {
            "ecmwf": round_knots(ecmwf_val) if ecmwf_val is not None else None,
            "gfs": round_knots(gfs_val) if gfs_val is not None else None,
            "icon": round_knots(icon_val) if icon_val is not None else None
        },
        "description": desc
    }


def fetch_tides(lat: float, lon: float, timezone_str: str = "auto") -> list:
    today_tides, _, _, _ = fetch_tides_both_days(lat, lon, timezone_str)
    return today_tides


def fetch_tides_both_days(lat: float, lon: float, timezone_str: str = "auto") -> tuple:
    url = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={lat}&longitude={lon}&hourly=sea_level_height_msl,sea_surface_temperature&timezone={timezone_str}&forecast_days=2"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        levels = hourly.get("sea_level_height_msl", [])
        sst_list = hourly.get("sea_surface_temperature", [])

        # Extract representative sea surface temperature for today (midday hr 12) & tomorrow (hr 36)
        today_sst = None
        tmrw_sst = None
        if sst_list:
            valid_today = [x for x in sst_list[:24] if x is not None]
            if valid_today:
                today_sst = round(sum(valid_today) / len(valid_today), 1)
            valid_tmrw = [x for x in sst_list[24:48] if x is not None]
            if valid_tmrw:
                tmrw_sst = round(sum(valid_tmrw) / len(valid_tmrw), 1)

        if not times or not levels:
            return [], [], today_sst, tmrw_sst

        today_tides = []
        tomorrow_tides = []
        for i in range(1, len(levels) - 1):
            prev_l, curr_l, next_l = levels[i-1], levels[i], levels[i+1]
            if curr_l is not None and prev_l is not None and next_l is not None:
                time_str = times[i][-5:]
                tide_item = None
                if curr_l > prev_l and curr_l >= next_l:
                    tide_item = {"type": "High", "time": time_str, "height": curr_l}
                elif curr_l < prev_l and curr_l <= next_l:
                    tide_item = {"type": "Low", "time": time_str, "height": curr_l}
                
                if tide_item:
                    if i < 24:
                        today_tides.append(tide_item)
                    else:
                        tomorrow_tides.append(tide_item)

        return today_tides, tomorrow_tides, today_sst, tmrw_sst
    except Exception as e:
        print(f"Error fetching tides & SST: {e}")
        return [], [], None, None


GLOBAL_THERMAL_SPOTS = {
    # Brazil (Ceará, Piauí, Maranhão) - World-renowned trade + sand dune thermal venturi
    "cumbuco": {"name": "Cumbuco", "boost_pct": 0.16, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Sand-dune thermal venturi"},
    "caucaia": {"name": "Caucaia/Cumbuco", "boost_pct": 0.16, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Sand-dune thermal venturi"},
    "taiba": {"name": "Taíba", "boost_pct": 0.18, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Lagoon & point thermal boost"},
    "paracuru": {"name": "Paracuru", "boost_pct": 0.18, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Quebra Mar coastal thermal boost"},
    "lagoinha": {"name": "Lagoinha", "boost_pct": 0.16, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Dune thermal acceleration"},
    "flecheiras": {"name": "Flecheiras", "boost_pct": 0.15, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Coastal reef thermal draw"},
    "guajiru": {"name": "Ilha do Guajirú", "boost_pct": 0.20, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Flatwater lagoon thermal chimney"},
    "itapipoca": {"name": "Ilha do Guajirú", "boost_pct": 0.20, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Flatwater lagoon thermal chimney"},
    "prea": {"name": "Preá", "boost_pct": 0.20, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Trade & dune venturi"},
    "jericoacoara": {"name": "Jericoacoara", "boost_pct": 0.22, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "National park dune thermal chimney"},
    "jeri": {"name": "Jericoacoara", "boost_pct": 0.22, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "National park dune thermal chimney"},
    "macapa": {"name": "Macapá", "boost_pct": 0.18, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Parnaíba delta thermal boost"},
    "barra grande": {"name": "Barra Grande", "boost_pct": 0.18, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Piauí flatwater thermal boost"},
    "atins": {"name": "Atins", "boost_pct": 0.18, "peak_start": 11, "peak_end": 16, "months": [7,8,9,10,11,12,1], "desc": "Lençóis Maranhenses dune heating"},
    # Europe
    "tarifa": {"name": "Tarifa", "boost_pct": 0.20, "peak_start": 13, "peak_end": 18, "months": [4,5,6,7,8,9,10], "desc": "Strait of Gibraltar venturi + thermal Poniente"},
    "lances": {"name": "Tarifa Los Lances", "boost_pct": 0.20, "peak_start": 13, "peak_end": 18, "months": [4,5,6,7,8,9,10], "desc": "Poniente thermal boost"},
    "valdevaqueros": {"name": "Valdevaqueros", "boost_pct": 0.22, "peak_start": 13, "peak_end": 18, "months": [4,5,6,7,8,9,10], "desc": "Dune thermal acceleration + venturi"},
    "garda": {"name": "Lake Garda", "boost_pct": 0.25, "peak_start": 12, "peak_end": 17, "months": [4,5,6,7,8,9,10], "desc": "Ora afternoon alpine thermal wind"},
    "silvaplana": {"name": "Lake Silvaplana", "boost_pct": 0.30, "peak_start": 12, "peak_end": 16, "months": [5,6,7,8,9], "desc": "Maloja alpine thermal wind"},
    "prasonisi": {"name": "Prasonisi", "boost_pct": 0.20, "peak_start": 11, "peak_end": 17, "months": [5,6,7,8,9,10], "desc": "Meltemi thermal channel acceleration"},
    "leucate": {"name": "Leucate", "boost_pct": 0.15, "peak_start": 12, "peak_end": 17, "months": [4,5,6,7,8,9,10], "desc": "Marine thermal boost"},
    # Americas
    "la ventana": {"name": "La Ventana", "boost_pct": 0.25, "peak_start": 12, "peak_end": 17, "months": [11,12,1,2,3,4], "desc": "Sea of Cortez thermal + valley venturi"},
    "barriles": {"name": "Los Barriles", "boost_pct": 0.22, "peak_start": 12, "peak_end": 17, "months": [11,12,1,2,3,4], "desc": "Baja thermal + El Norte trade boost"},
    "hood river": {"name": "Hood River", "boost_pct": 0.30, "peak_start": 12, "peak_end": 18, "months": [5,6,7,8,9], "desc": "Columbia Gorge thermal pressure draw"},
    "sherman": {"name": "Sherman Island", "boost_pct": 0.25, "peak_start": 13, "peak_end": 18, "months": [5,6,7,8,9], "desc": "SF Bay / Central Valley thermal chimney"},
    "cabarete": {"name": "Cabarete", "boost_pct": 0.18, "peak_start": 12, "peak_end": 17, "months": [1,2,3,4,5,6,7,8,9,10,11,12], "desc": "Afternoon Atlantic sea breeze trade boost"},
    # Africa / Middle East
    "dakhla": {"name": "Dakhla", "boost_pct": 0.20, "peak_start": 12, "peak_end": 17, "months": [3,4,5,6,7,8,9,10], "desc": "Sahara desert thermal boundary draw"},
    "el gouna": {"name": "El Gouna", "boost_pct": 0.18, "peak_start": 10, "peak_end": 16, "months": [4,5,6,7,8,9,10], "desc": "Red Sea desert thermal channel"},
    "cape town": {"name": "Cape Town", "boost_pct": 0.22, "peak_start": 13, "peak_end": 18, "months": [10,11,12,1,2,3], "desc": "Cape Doctor thermal + Table Mountain ridge venturi"},
    "blouberg": {"name": "Bloubergstrand", "boost_pct": 0.22, "peak_start": 13, "peak_end": 18, "months": [10,11,12,1,2,3], "desc": "Cape Doctor thermal + ridge venturi"}
}


def get_spot_thermal_profile(spot_name: str) -> dict:
    clean = (spot_name or "").lower()
    for key, profile in GLOBAL_THERMAL_SPOTS.items():
        if key in clean:
            return profile
    return None


def calculate_thermal_calibration(
    hour: int,
    base_wind: float,
    base_gust: float,
    land_temp: float,
    sea_temp: float,
    spot_name: str,
    shore_diff: float = 45.0,
    month: int = None
) -> dict:
    profile = get_spot_thermal_profile(spot_name)
    if month is None:
        month = datetime.now().month

    boost_pct = 0.0
    reason = "None"
    is_active = False

    if profile:
        # Known thermal spot
        in_season = month in profile.get("months", list(range(1, 13)))
        start_hr = profile.get("peak_start", 11)
        end_hr = profile.get("peak_end", 16)
        
        if in_season and (start_hr - 1) <= hour <= (end_hr + 1):
            max_boost = profile.get("boost_pct", 0.15)
            # Smooth bell curve centered between start and end
            mid_hr = (start_hr + end_hr) / 2.0
            span = max(1.0, (end_hr - start_hr + 2) / 2.0)
            dist = abs(hour - mid_hr)
            curve = max(0.0, 1.0 - (dist / span) ** 1.5)
            boost_pct = max_boost * curve
            reason = profile.get("desc", "Local thermal boost")
            is_active = boost_pct >= 0.03
    else:
        # Universal thermodynamic check for any beach/spot
        if sea_temp is not None and land_temp is not None:
            delta_t = land_temp - sea_temp
            # Solar peak hours and warm land
            if 11 <= hour <= 16 and delta_t >= 2.5 and shore_diff <= 90.0:
                boost_pct = min(0.20, max(0.05, 0.035 * (delta_t - 1.5)))
                reason = f"Thermodynamic sea breeze (ΔT = +{round(delta_t, 1)}°C)"
                is_active = True

    boosted_wind = round_knots(base_wind * (1.0 + boost_pct))
    boosted_gust = round_knots(max(base_gust, boosted_wind * 1.18))
    boost_kts = round(boosted_wind - base_wind, 1)

    return {
        "boosted_wind": boosted_wind,
        "boosted_gust": boosted_gust,
        "boost_pct": round(boost_pct * 100),
        "boost_kts": boost_kts,
        "is_active": is_active,
        "reason": reason
    }


def find_peak_session_window(hourly_slots: list) -> dict:
    """Finds the best 2-4 hour riding window between 10:00 and 17:00."""
    day_slots = [s for s in hourly_slots if 10 <= s["hour"] <= 17]
    if not day_slots:
        return {"tag": "⚡ Peak Session: 12:00 – 15:30", "range": "15–17 kts", "best_hour": 13, "wind_range": "15–17 kts"}
    
    best_slot = max(day_slots, key=lambda s: s["wind_kts"])
    b_hr = best_slot["hour"]
    start_hr = max(11, b_hr - 1)
    end_hr = min(16, b_hr + 2)
    window_slots = [s for s in day_slots if start_hr <= s["hour"] <= end_hr]
    min_w = min(s["wind_kts"] for s in window_slots)
    max_w = max(s["wind_kts"] for s in window_slots)
    
    return {
        "start_time": f"{start_hr:02d}:00",
        "end_time": f"{end_hr:02d}:30",
        "wind_range": f"{round_knots(min_w)}–{round_knots(max_w)} kts",
        "best_hour": b_hr,
        "best_wind": round_knots(best_slot["wind_kts"]),
        "best_gust": round_knots(best_slot["gust_kts"]),
        "tag": f"⚡ Peak Session: {start_hr:02d}:00 – {end_hr:02d}:30 ({round_knots(min_w)}–{round_knots(max_w)} kts)"
    }


def fetch_weather_openmeteo(spot: dict, today_sst: float = None, tomorrow_sst: float = None) -> dict:
    params = {
        "latitude": spot["lat"],
        "longitude": spot["lon"],
        "current": "temperature_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,wind_gusts_10m,weather_code",
        "hourly": "temperature_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,wind_gusts_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant",
        "models": "best_match,ecmwf_ifs025,gfs_seamless,icon_seamless",
        "wind_speed_unit": "kn",
        "timezone": spot.get("timezone", "auto"),
        "forecast_days": 7
    }
    url = f"https://api.open-meteo.com/v1/forecast?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    utc_offset = data.get("utc_offset_seconds")
    spot_tz = data.get("timezone", spot.get("timezone", "auto"))

    current = data.get("current", {})
    hourly = data.get("hourly", {})
    speeds = hourly.get("wind_speed_10m_best_match") or hourly.get("wind_speed_10m", [])
    gusts = hourly.get("wind_gusts_10m_best_match") or hourly.get("wind_gusts_10m", [])
    directions = hourly.get("wind_direction_10m_best_match") or hourly.get("wind_direction_10m", [])
    temps = hourly.get("temperature_2m_best_match") or hourly.get("temperature_2m", [])

    ecmwf_speeds = hourly.get("wind_speed_10m_ecmwf_ifs025", [])
    gfs_speeds = hourly.get("wind_speed_10m_gfs_seamless", [])
    icon_speeds = hourly.get("wind_speed_10m_icon_seamless", [])

    beach_angle = resolve_beach_angle(spot.get("name", ""), spot.get("beach_angle"))
    cur_month = datetime.now().month

    # 1. 2-Hour Key Daylight Slots (07:00 to 19:00)
    target_2h_slots = {
        "07:00 Early Dawn": 7,
        "09:00 Morning Breeze": 9,
        "11:00 Thermal Building": 11,
        "13:00 Midday Peak": 13,
        "15:00 Afternoon Session": 15,
        "17:00 Sunset Session": 17,
        "19:00 Evening Wind-down": 19
    }

    # 2. 1-Hour Full Daylight Slots (07:00 to 19:00)
    daylight_hours = list(range(7, 20))

    def build_slot_data(hr_index, solar_hr, sst_val):
        raw_w = speeds[hr_index] if hr_index < len(speeds) else 15.0
        raw_g = gusts[hr_index] if hr_index < len(gusts) else raw_w * 1.25
        d_val = round(directions[hr_index]) if hr_index < len(directions) else 90
        t_val = round(temps[hr_index], 1) if hr_index < len(temps) else 28.0

        shore = calculate_shoreline_status(d_val, beach_angle)
        calib = calculate_thermal_calibration(
            solar_hr, raw_w, raw_g, t_val, sst_val,
            spot.get("name", ""), shore_diff=shore.get("relative_angle", 45.0), month=cur_month
        )
        w_calib = calib["boosted_wind"]
        g_calib = calib["boosted_gust"]

        # Coastal Calibration for coarse 28km ECMWF Open Data
        raw_e = ecmwf_speeds[hr_index] if hr_index < len(ecmwf_speeds) else raw_w
        e_calib = min(w_calib + 2, max(w_calib - 3, round_knots(raw_e * 1.30)))
        gf_val = gfs_speeds[hr_index] if hr_index < len(gfs_speeds) else raw_w
        ic_val = icon_speeds[hr_index] if hr_index < len(icon_speeds) else raw_w

        return {
            "hour": solar_hr,
            "wind_kts": w_calib,
            "gust_kts": g_calib,
            "direction": degrees_to_cardinal(d_val),
            "degrees": d_val,
            "temp": t_val,
            "stability": calculate_stability_score(w_calib, g_calib),
            "shoreline": shore,
            "consensus": calculate_model_consensus(e_calib, gf_val, ic_val),
            "thermal": calib
        }

    # Today schedules
    schedule = {}
    for label, hr in target_2h_slots.items():
        if hr < len(speeds):
            schedule[label] = build_slot_data(hr, hr, today_sst)

    schedule_hourly = {}
    for hr in daylight_hours:
        if hr < len(speeds):
            schedule_hourly[f"{hr:02d}:00"] = build_slot_data(hr, hr, today_sst)

    # Tomorrow schedules (offset +24)
    schedule_tomorrow = {}
    for label, hr in target_2h_slots.items():
        tmrw_hr = hr + 24
        if tmrw_hr < len(speeds):
            schedule_tomorrow[label] = build_slot_data(tmrw_hr, hr, tomorrow_sst)

    schedule_tomorrow_hourly = {}
    for hr in daylight_hours:
        tmrw_hr = hr + 24
        if tmrw_hr < len(speeds):
            schedule_tomorrow_hourly[f"{hr:02d}:00"] = build_slot_data(tmrw_hr, hr, tomorrow_sst)

    # Peak Session Windows
    peak_session = find_peak_session_window(list(schedule_hourly.values()))
    tomorrow_peak_session = find_peak_session_window(list(schedule_tomorrow_hourly.values()))

    # Current conditions with instant thermal calibration if in thermal window
    cur_time_str = current.get("time")
    cur_hr = 12
    if cur_time_str and "T" in cur_time_str:
        try:
            cur_hr = int(cur_time_str.split("T")[1].split(":")[0])
        except Exception:
            cur_hr = 12

    raw_cur_wind = round_knots(current.get("wind_speed_10m", speeds[cur_hr] if len(speeds) > cur_hr else 16.0))
    raw_cur_gust = round_knots(current.get("wind_gusts_10m", gusts[cur_hr] if len(gusts) > cur_hr else raw_cur_wind))
    cur_dir_deg = round(current.get("wind_direction_10m", directions[cur_hr] if len(directions) > cur_hr else 90))
    cur_dir = degrees_to_cardinal(cur_dir_deg)
    cur_temp = round(current.get("temperature_2m", 28.5), 1)
    cur_apparent = round(current.get("apparent_temperature", cur_temp), 1)

    cur_shore = calculate_shoreline_status(cur_dir_deg, beach_angle)
    cur_calib = calculate_thermal_calibration(
        cur_hr, raw_cur_wind, raw_cur_gust, cur_temp, today_sst,
        spot.get("name", ""), shore_diff=cur_shore.get("relative_angle", 45.0), month=cur_month
    )
    cur_wind = cur_calib["boosted_wind"]
    cur_gust = cur_calib["boosted_gust"]

    # Calibrate Consensus Barometer
    raw_ecmwf = ecmwf_speeds[cur_hr] if len(ecmwf_speeds) > cur_hr else cur_wind
    calib_ecmwf = min(cur_wind + 2, max(cur_wind - 3, round_knots(raw_ecmwf * 1.30)))
    calib_gfs = gfs_speeds[cur_hr] if len(gfs_speeds) > cur_hr else cur_wind
    calib_icon = icon_speeds[cur_hr] if len(icon_speeds) > cur_hr else cur_wind

    cur_stability = calculate_stability_score(cur_wind, cur_gust)
    cur_consensus = calculate_model_consensus(calib_ecmwf, calib_gfs, calib_icon)

    today_temps = temps[:24] if len(temps) >= 24 else temps
    today_gusts = gusts[:24] if len(gusts) >= 24 else gusts
    tmrw_temps = temps[24:48] if len(temps) >= 48 else temps
    tmrw_gusts = gusts[24:48] if len(gusts) >= 48 else gusts

    thermal_meta = {
        "is_active": cur_calib["is_active"],
        "boost_pct": cur_calib["boost_pct"],
        "boost_kts": cur_calib["boost_kts"],
        "reason": cur_calib["reason"],
        "spot_profile": get_spot_thermal_profile(spot.get("name", ""))
    }

    # 7-Day Forecast Construction
    weekly_forecast = []
    daily_data = data.get("daily", {})
    daily_times = daily_data.get("time", [])

    spot_name_l = (spot.get("name") or "").lower()
    s_lat = float(spot.get("lat", 0))
    s_lon = float(spot.get("lon", 0))

    if "italy" in spot_name_l or "garda" in spot_name_l or "como" in spot_name_l or "silvaplana" in spot_name_l or "germany" in spot_name_l or "switzerland" in spot_name_l or "austria" in spot_name_l or (44.0 <= s_lat <= 55.0 and 5.0 <= s_lon <= 17.0):
        short_model = "DWD ICON-D2 (2km) & ICON-EU"
    elif "france" in spot_name_l or "leucate" in spot_name_l or "hyeres" in spot_name_l:
        short_model = "Météo-France AROME (1.3km)"
    elif "united states" in spot_name_l or "usa" in spot_name_l or "hood river" in spot_name_l or "maui" in spot_name_l:
        short_model = "NOAA HRRR (3km) High-Res"
    elif "spain" in spot_name_l or "tarifa" in spot_name_l or "pozo" in spot_name_l or "portugal" in spot_name_l or "greece" in spot_name_l:
        short_model = "DWD ICON-EU (7km)"
    elif "brazil" in spot_name_l or "cumbuco" in spot_name_l or "taiba" in spot_name_l or "prea" in spot_name_l:
        short_model = "ECMWF IFS (9km) + Thermal Venturi"
    else:
        short_model = spot.get("model_label") or "ECMWF IFS (9km) High-Res"

    def decode_wmo(code):
        if code == 0: return "Clear Sky", "☀️"
        if code in [1, 2]: return "Partly Cloudy", "⛅"
        if code == 3: return "Overcast", "☁️"
        if code in [45, 48]: return "Fog", "🌫️"
        if code in [51, 53, 55]: return "Drizzle", "🌦️"
        if code in [61, 63, 65]: return "Rain", "🌧️"
        if code in [71, 73, 75]: return "Snow", "🌨️"
        if code in [80, 81, 82]: return "Rain Showers", "🌦️"
        if code in [95, 96, 99]: return "Thunderstorm", "⛈️"
        return "Breezy", "💨"

    num_days = min(7, len(daily_times)) if daily_times else 7
    for d in range(num_days):
        dt_str = daily_times[d] if d < len(daily_times) else ""
        try:
            d_obj = datetime.strptime(dt_str, "%Y-%m-%d")
            day_name = "Today" if d == 0 else ("Tomorrow" if d == 1 else d_obj.strftime("%A"))
            date_display = d_obj.strftime("%a, %b %d")
        except Exception:
            day_name = "Today" if d == 0 else ("Tomorrow" if d == 1 else f"Day +{d}")
            date_display = dt_str

        h_start = d * 24 + 8
        h_end = d * 24 + 19
        d_speeds = [speeds[h] for h in range(h_start, min(h_end, len(speeds)))]
        d_gusts = [gusts[h] for h in range(h_start, min(h_end, len(gusts)))]
        d_dirs = [directions[h] for h in range(h_start, min(h_end, len(directions)))]
        d_temps = [temps[h] for h in range(h_start, min(h_end, len(temps)))]

        peak_w = round_knots(max(d_speeds) if d_speeds else 15.0)
        min_w = round_knots(min(d_speeds) if d_speeds else 10.0)
        avg_w = round(sum(d_speeds)/len(d_speeds), 1) if d_speeds else 12.0
        peak_g = round_knots(max(d_gusts) if d_gusts else peak_w * 1.25)
        dom_deg = round(d_dirs[len(d_dirs)//2]) if d_dirs else 90
        dom_card = degrees_to_cardinal(dom_deg)

        w_code = 0
        w_codes_list = daily_data.get("weather_code_best_match") or daily_data.get("weather_code")
        if w_codes_list and d < len(w_codes_list):
            w_code = w_codes_list[d]
        w_desc, w_icon = decode_wmo(w_code)

        shore = calculate_shoreline_status(dom_deg, beach_angle)
        stab = calculate_stability_score(avg_w, peak_g)

        best_hr_idx = 13
        if d_speeds:
            max_idx = d_speeds.index(max(d_speeds))
            best_hr_idx = 8 + max_idx
        start_w = max(8, best_hr_idx - 2)
        end_w = min(19, best_hr_idx + 2)
        best_window = f"{start_w:02d}:00 – {end_w:02d}:00"

        day_model = short_model if d < 2 else "ECMWF IFS (9km) Synoptic Ensemble"

        day_hourly = []
        for h_sub in range(7, 20):
            full_h = d * 24 + h_sub
            if full_h < len(speeds):
                h_w = round_knots(speeds[full_h])
                h_g = round_knots(gusts[full_h]) if full_h < len(gusts) else h_w
                h_d = round(directions[full_h]) if full_h < len(directions) else 90
                day_hourly.append({
                    "hour": f"{h_sub:02d}:00",
                    "wind_kts": h_w,
                    "gust_kts": h_g,
                    "direction": degrees_to_cardinal(h_d),
                    "degrees": h_d,
                    "shoreline": calculate_shoreline_status(h_d, beach_angle)
                })

        weekly_forecast.append({
            "day_index": d,
            "day_name": day_name,
            "date": dt_str,
            "date_display": date_display,
            "weather_code": w_code,
            "weather_desc": w_desc,
            "weather_icon": w_icon,
            "wind_min_kts": min_w,
            "wind_peak_kts": peak_w,
            "wind_avg_kts": avg_w,
            "gust_peak_kts": peak_g,
            "direction": dom_card,
            "degrees": dom_deg,
            "shoreline": shore,
            "stability": stab,
            "best_window": best_window,
            "best_hour": best_hr_idx,
            "model_used": day_model,
            "hourly": day_hourly
        })

    return {
        "spot": spot["name"],
        "beach_angle": beach_angle,
        "timezone": spot_tz,
        "utc_offset_seconds": utc_offset,
        "temp_min": round(min(today_temps), 1) if today_temps else 25,
        "temp_max": round(max(today_temps), 1) if today_temps else 31,
        "max_gust": round_knots(max(today_gusts) if today_gusts else cur_gust),
        "tomorrow_temp_min": round(min(tmrw_temps), 1) if tmrw_temps else 25,
        "tomorrow_temp_max": round(max(tmrw_temps), 1) if tmrw_temps else 31,
        "tomorrow_max_gust": round_knots(max(tmrw_gusts) if tmrw_gusts else 26),
        "current": {
            "wind_kts": cur_wind,
            "gust_kts": cur_gust,
            "direction": cur_dir,
            "degrees": cur_dir_deg,
            "temp": cur_temp
        },
        "shoreline": cur_shore,
        "stability": cur_stability,
        "consensus": cur_consensus,
        "schedule": schedule,
        "schedule_hourly": schedule_hourly,
        "schedule_tomorrow": schedule_tomorrow,
        "schedule_tomorrow_hourly": schedule_tomorrow_hourly,
        "weekly_forecast": weekly_forecast,
        "peak_session": peak_session,
        "tomorrow_peak_session": tomorrow_peak_session,
        "thermal": thermal_meta
    }


def fetch_weather_metno(spot: dict) -> dict:
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={spot['lat']}&lon={spot['lon']}"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0 (team@holygust.com)"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    series = data.get("properties", {}).get("timeseries", [])
    if not series:
        raise ValueError("Empty timeseries from Met.no")

    cur_details = series[0]["data"]["instant"]["details"]
    cur_wind = round_knots(cur_details["wind_speed"] * 1.94384)
    cur_gust = round_knots(cur_details.get("wind_speed_of_gust", cur_details["wind_speed"]) * 1.94384)
    cur_temp = round(cur_details["air_temperature"], 1)
    cur_dir_deg = round(cur_details.get("wind_from_direction", 90))
    cur_dir = degrees_to_cardinal(cur_dir_deg)

    beach_angle = resolve_beach_angle(spot.get("name", ""), spot.get("beach_angle"))
    cur_stability = calculate_stability_score(cur_wind, cur_gust)
    cur_shoreline = calculate_shoreline_status(cur_dir_deg, beach_angle)
    cur_consensus = calculate_model_consensus(cur_wind, cur_wind + 1, cur_wind)

    target_2h_slots = {
        "07:00 Early Dawn": 7,
        "09:00 Morning Breeze": 9,
        "11:00 Thermal Building": 11,
        "13:00 Midday Peak": 13,
        "15:00 Afternoon Session": 15,
        "17:00 Sunset Session": 17,
        "19:00 Evening Wind-down": 19
    }
    daylight_hours = list(range(7, 20))

    schedule = {}
    for label, hr in target_2h_slots.items():
        w_adj = cur_wind + (1 if 11 <= hr <= 15 else 0)
        g_adj = cur_gust + (2 if 11 <= hr <= 15 else 0)
        schedule[label] = {
            "hour": hr,
            "wind_kts": w_adj,
            "gust_kts": g_adj,
            "direction": cur_dir,
            "degrees": cur_dir_deg,
            "temp": cur_temp,
            "stability": cur_stability,
            "shoreline": cur_shoreline,
            "consensus": cur_consensus,
            "thermal": {"is_active": 11 <= hr <= 15, "boost_kts": 1.5, "reason": "Estimated thermal"}
        }

    schedule_hourly = {}
    for hr in daylight_hours:
        w_adj = cur_wind + (1 if 11 <= hr <= 15 else 0)
        g_adj = cur_gust + (2 if 11 <= hr <= 15 else 0)
        schedule_hourly[f"{hr:02d}:00"] = {
            "hour": hr,
            "wind_kts": w_adj,
            "gust_kts": g_adj,
            "direction": cur_dir,
            "degrees": cur_dir_deg,
            "temp": cur_temp,
            "stability": cur_stability,
            "shoreline": cur_shoreline,
            "consensus": cur_consensus,
            "thermal": {"is_active": 11 <= hr <= 15, "boost_kts": 1.5, "reason": "Estimated thermal"}
        }

    schedule_tomorrow = {label: dict(slot) for label, slot in schedule.items()}
    schedule_tomorrow_hourly = {label: dict(slot) for label, slot in schedule_hourly.items()}

    approx_offset = round(spot.get("lon", -38.7297) / 15.0) * 3600
    return {
        "spot": spot["name"],
        "beach_angle": beach_angle,
        "timezone": spot.get("timezone", "America/Fortaleza"),
        "utc_offset_seconds": approx_offset,
        "temp_min": round(cur_temp - 3, 1),
        "temp_max": round(cur_temp + 2, 1),
        "max_gust": round_knots(max(s["gust_kts"] for s in schedule.values())),
        "tomorrow_temp_min": round(cur_temp - 3, 1),
        "tomorrow_temp_max": round(cur_temp + 2, 1),
        "tomorrow_max_gust": round_knots(max(s["gust_kts"] for s in schedule_tomorrow.values())),
        "current": {
            "wind_kts": cur_wind,
            "gust_kts": cur_gust,
            "direction": cur_dir,
            "degrees": cur_dir_deg,
            "temp": cur_temp
        },
        "shoreline": cur_shoreline,
        "stability": cur_stability,
        "consensus": cur_consensus,
        "schedule": schedule,
        "schedule_hourly": schedule_hourly,
        "schedule_tomorrow": schedule_tomorrow,
        "schedule_tomorrow_hourly": schedule_tomorrow_hourly,
        "peak_session": {"tag": "⚡ Peak Session: 12:00 – 15:30", "wind_range": f"{cur_wind}–{cur_wind+2} kts", "best_hour": 13},
        "tomorrow_peak_session": {"tag": "⚡ Peak Session: 12:00 – 15:30", "wind_range": f"{cur_wind}–{cur_wind+2} kts", "best_hour": 13},
        "thermal": {"is_active": False, "boost_kts": 0.0, "reason": "Met.no standard"}
    }


def fetch_live_forecast(spot: dict) -> dict:
    today_tides, tomorrow_tides, today_sst, tomorrow_sst = fetch_tides_both_days(spot["lat"], spot["lon"], spot.get("timezone", "auto"))
    forecast = None
    try:
        forecast = fetch_weather_openmeteo(spot, today_sst=today_sst, tomorrow_sst=tomorrow_sst)
    except Exception as e:
        print(f"Open-Meteo ({e}), switching to Met.no...")
        try:
            forecast = fetch_weather_metno(spot)
        except Exception as e2:
            print(f"Met.no ({e2}), using cache...")
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    forecast = json.load(f)

    if not forecast:
        beach_angle = resolve_beach_angle(spot.get("name", ""), spot.get("beach_angle"))
        stab_default = calculate_stability_score(16.0, 25.0)
        shore_default = calculate_shoreline_status(90, beach_angle)
        cons_default = calculate_model_consensus(16.0, 17.0, 15.5)

        target_2h_slots = {
            "07:00 Early Dawn": 7,
            "09:00 Morning Breeze": 9,
            "11:00 Thermal Building": 11,
            "13:00 Midday Peak": 13,
            "15:00 Afternoon Session": 15,
            "17:00 Sunset Session": 17,
            "19:00 Evening Wind-down": 19
        }
        sched_default = {}
        for l, h in target_2h_slots.items():
            sched_default[l] = {"hour": h, "wind_kts": 16.0, "gust_kts": 24.0, "direction": "E", "degrees": 90, "temp": 29.0, "stability": stab_default, "shoreline": shore_default, "consensus": cons_default}

        forecast = {
            "spot": spot["name"],
            "beach_angle": beach_angle,
            "timezone": spot.get("timezone", "America/Fortaleza"),
            "utc_offset_seconds": -10800,
            "temp_min": 25.5,
            "temp_max": 30.5,
            "max_gust": 28.0,
            "tomorrow_temp_min": 25.0,
            "tomorrow_temp_max": 31.0,
            "tomorrow_max_gust": 26.0,
            "current": {"wind_kts": 16.0, "gust_kts": 25.0, "direction": "E", "degrees": 90, "temp": 29.0},
            "shoreline": shore_default,
            "stability": stab_default,
            "consensus": cons_default,
            "schedule": sched_default,
            "schedule_hourly": {f"{h:02d}:00": {"hour": h, "wind_kts": 16.0, "gust_kts": 24.0, "direction": "E", "degrees": 90, "temp": 29.0, "stability": stab_default, "shoreline": shore_default, "consensus": cons_default} for h in range(7, 20)},
            "schedule_tomorrow": sched_default,
            "schedule_tomorrow_hourly": {f"{h:02d}:00": {"hour": h, "wind_kts": 16.0, "gust_kts": 24.0, "direction": "E", "degrees": 90, "temp": 29.0, "stability": stab_default, "shoreline": shore_default, "consensus": cons_default} for h in range(7, 20)},
            "peak_session": {"tag": "⚡ Peak Session: 12:00 – 15:30 (16–17 kts)", "wind_range": "16–17 kts"},
            "tomorrow_peak_session": {"tag": "⚡ Peak Session: 12:00 – 15:30 (16–17 kts)", "wind_range": "16–17 kts"},
            "thermal": {"is_active": True, "boost_kts": 2.5, "reason": "Sand-dune thermal venturi"}
        }

    forecast["tides"] = today_tides
    forecast["tides_tomorrow"] = tomorrow_tides
    forecast["sea_temp"] = today_sst
    forecast["tomorrow_sea_temp"] = tomorrow_sst

    beach_angle = resolve_beach_angle(spot.get("name", ""), spot.get("beach_angle"))
    forecast["beach_angle"] = beach_angle

    cur_wind = forecast.get("current", {}).get("wind_kts", 16)
    cur_gust = forecast.get("current", {}).get("gust_kts", 20)
    cur_dir_deg = forecast.get("current", {}).get("degrees", 90)
    cur_temp = forecast.get("current", {}).get("temp", 28.0)

    if "shoreline" not in forecast:
        forecast["shoreline"] = calculate_shoreline_status(cur_dir_deg, beach_angle)
    if "stability" not in forecast:
        forecast["stability"] = calculate_stability_score(cur_wind, cur_gust)
    if "consensus" not in forecast:
        forecast["consensus"] = calculate_model_consensus(cur_wind, cur_wind + 1, cur_wind - 1)

    # Attach Wetsuit & Thermal Comfort Guide (accounting for wind chill & evaporative heat loss)
    cur_apparent = forecast.get("current", {}).get("apparent_temp")
    forecast["wetsuit"] = calculate_wetsuit_guide(today_sst, cur_temp, wind_kts=cur_wind, apparent_temp=cur_apparent)
    tmrw_temp = forecast.get("tomorrow_temp_max", cur_temp)
    tmrw_wind = forecast.get("tomorrow_max_wind", 15.0)
    forecast["tomorrow_wetsuit"] = calculate_wetsuit_guide(tomorrow_sst, tmrw_temp, wind_kts=tmrw_wind)

    # Attach Regional Meteorological Wind Model Label
    try:
        from kite_spots import GLOBAL_KITE_SPOTS
        spot_name_clean = spot.get("name", "").lower()
        matched_model = "ECMWF (9km) + High-Res Local Model"
        for s in GLOBAL_KITE_SPOTS:
            if s["id"] in spot_name_clean or s["name"].lower() in spot_name_clean or spot_name_clean in s["name"].lower():
                matched_model = s.get("model_label", matched_model)
                break
        forecast["model_info"] = matched_model
    except Exception:
        forecast["model_info"] = "ECMWF (9km) + High-Res Ensemble"

    # Guaranteed 7-Day Weekly Forecast Fallback
    if "weekly_forecast" not in forecast or not forecast.get("weekly_forecast"):
        cur_w = forecast.get("current", {}).get("wind_kts", 16.0)
        cur_g = forecast.get("current", {}).get("gust_kts", 22.0)
        cur_deg = forecast.get("current", {}).get("degrees", 90)
        cur_card = forecast.get("current", {}).get("direction", "E")
        synth_week = []
        base_now = datetime.now()
        for d in range(7):
            d_time = base_now + timedelta(days=d)
            d_name = "Today" if d == 0 else ("Tomorrow" if d == 1 else d_time.strftime("%A"))
            date_disp = d_time.strftime("%a, %b %d")
            factor = 1.0 + ((d % 3) - 1) * 0.08
            d_w = round_knots(cur_w * factor)
            d_g = round_knots(cur_g * factor)
            day_model = forecast.get("model_info", "ECMWF IFS (9km)") if d < 2 else "ECMWF IFS (9km) Synoptic Ensemble"
            synth_week.append({
                "day_index": d,
                "day_name": d_name,
                "date": d_time.strftime("%Y-%m-%d"),
                "date_display": date_disp,
                "weather_code": 1,
                "weather_desc": "Clear / Breezy",
                "weather_icon": "☀️",
                "wind_min_kts": max(8.0, round_knots(d_w * 0.8)),
                "wind_peak_kts": d_w,
                "wind_avg_kts": d_w,
                "gust_peak_kts": d_g,
                "direction": cur_card,
                "degrees": cur_deg,
                "shoreline": forecast.get("shoreline", {"type": "Sideshore", "safe": True}),
                "stability": forecast.get("stability", {"status": "Solid", "score": 8}),
                "best_window": "12:00 – 16:30",
                "best_hour": 14,
                "model_used": day_model,
                "hourly": [
                    {
                        "hour": f"{h:02d}:00",
                        "wind_kts": d_w,
                        "gust_kts": d_g,
                        "direction": cur_card,
                        "degrees": cur_deg,
                        "shoreline": forecast.get("shoreline", {"type": "Sideshore", "safe": True})
                    } for h in range(7, 20)
                ]
            })
        forecast["weekly_forecast"] = synth_week

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(forecast, f)
    except Exception:
        pass
    return forecast


def evaluate_active_kite(
    kite_entry: dict,
    weight_kg: float,
    wind_kts: float,
    gust_kts: float,
    level: str = "intermediate",
    board: str = "twintip"
) -> dict:
    specs = lookup_kite_specs(kite_entry["brand"], kite_entry["model"], kite_entry["size"])
    # 60% aerodynamic lift scaling + 40% hydrodynamic displacement/planing scaling
    w_factor = (math.sqrt(weight_kg / 75.0) * 0.6) + ((weight_kg / 75.0) * 0.4)

    min_k = specs["min"] * w_factor
    sweet_min = specs["sweet"][0] * w_factor
    sweet_max = specs["sweet"][1] * w_factor
    max_k = specs["max"] * w_factor

    # Rider Skill Level adjustments
    lvl = (level or "intermediate").lower()
    if lvl == "beginner":
        min_k *= 1.15
        sweet_min *= 1.10
        max_k *= 0.88
    elif lvl == "advanced":
        min_k *= 0.92
        sweet_max *= 1.08
        max_k *= 1.12

    # Board Discipline & Hydrodynamic adjustments
    brd = (board or "twintip").lower()
    if "surf" in brd or "strapless" in brd:
        min_k *= 0.84
        sweet_min *= 0.85
        sweet_max *= 0.90
        max_k *= 0.88
    elif "foil" in brd:
        min_k *= 0.60
        sweet_min *= 0.65
        sweet_max *= 0.75
        max_k *= 0.78
    else:
        # Twintip sizing factor (e.g. 136cm vs 142cm vs door)
        tt_match = re.search(r"(\d{3})", brd)
        tt_len = float(tt_match.group(1)) if tt_match else 138.0
        if tt_len >= 145:
            min_k *= 0.88
            sweet_min *= 0.90
            sweet_max *= 0.94
            max_k *= 0.94
        elif tt_len >= 141:
            min_k *= 0.94
            sweet_min *= 0.95
            sweet_max *= 0.97
            max_k *= 0.97
        elif tt_len <= 133:
            min_k *= 1.08
            sweet_min *= 1.08
            sweet_max *= 1.03
            max_k *= 1.04
        elif tt_len <= 136:
            min_k *= 1.05
            sweet_min *= 1.05
            sweet_max *= 1.02
            max_k *= 1.03

    in_range = min_k <= wind_kts <= max_k
    in_sweet = sweet_min <= wind_kts <= sweet_max
    mid_sweet = (sweet_min + sweet_max) / 2.0
    dist_to_sweet = abs(wind_kts - mid_sweet)
    year_str = f" ({kite_entry['year']})" if kite_entry.get("year") else ""

    return {
        "display_name": f"{specs['brand']} {specs['model']}{year_str} *{specs['size']}m*",
        "brand": specs["brand"],
        "model": specs["model"],
        "year": kite_entry.get("year"),
        "size": specs["size"],
        "material": specs["material"],
        "min_k": min_k,
        "sweet_min": sweet_min,
        "sweet_max": sweet_max,
        "max_k": max_k,
        "in_range": in_range,
        "in_sweet": in_sweet,
        "dist_to_sweet": dist_to_sweet
    }


def recommend_from_available_quiver(
    weight_kg: float,
    active_inventory: list,
    wind_kts: float,
    gust_kts: float,
    all_inventory: list = None,
    level: str = "intermediate",
    board: str = "twintip",
    slot_hour: int = None
) -> str:
    if not active_inventory:
        if all_inventory:
            return "🎒 No kites packed in backpack today! Type `/take all` or enjoy a Caipirinha 🍹"
        return "⚠️ No kites registered yet! (type `/kite 1 <Brand> <Model> <Size>`)"

    evaluated = [evaluate_active_kite(k, weight_kg, wind_kts, gust_kts, level=level, board=board) for k in active_inventory]

    # 1. Exact sweet spot match
    sweet_matches = [k for k in evaluated if k["in_sweet"]]
    if sweet_matches:
        best = min(sweet_matches, key=lambda k: k["dist_to_sweet"])
        advisory = ""
        if gust_kts and (gust_kts - wind_kts >= 11) and (wind_kts - best["sweet_min"] <= 1.5):
            advisory = f" (Punchy Gusts {round_knots(gust_kts)} kts)"
        return f"{best['display_name']}{advisory}"

    # 2. Inside rideable wind range
    range_matches = [k for k in evaluated if k["in_range"]]
    if range_matches:
        best = min(range_matches, key=lambda k: k["dist_to_sweet"])
        if wind_kts > best["sweet_max"]:
            tag = " (Overpowered)"
        else:
            if gust_kts and (gust_kts - wind_kts >= 9 or gust_kts >= best["sweet_min"]):
                tag = f" (Underpowered in lulls · Gusts {round_knots(gust_kts)} kts)"
            else:
                tag = " (Underpowered)"
        return f"{best['display_name']}{tag}"

    mins = [k["min_k"] for k in evaluated]
    maxs = [k["max_k"] for k in evaluated]

    # Check if user has an even smaller kite left at home (inactive in inventory)
    smallest = min(evaluated, key=lambda k: k["size"])
    smaller_at_home = []
    if all_inventory:
        for k in all_inventory:
            if not k.get("active", True) and k.get("size", 99) < smallest["size"]:
                smaller_at_home.append(k)

    home_tip = ""
    if smaller_at_home:
        home_kite = min(smaller_at_home, key=lambda k: k["size"])
        yr_str = f" ({home_kite['year']})" if home_kite.get("year") else ""
        home_tip = f" 💡 Pack your {home_kite['brand']} {home_kite['model']}{yr_str} {home_kite['size']}m: `/take all`"

    # 3. Wind too light (< min of active quiver): Caipirinha Time!
    if wind_kts < min(mins):
        biggest = max(evaluated, key=lambda k: k["size"])
        # Check if heavy gusts make it rideable in spikes
        if gust_kts and gust_kts >= biggest["sweet_min"] and (gust_kts - wind_kts >= 10):
            return f"{biggest['display_name']} (Underpowered in lulls · Gusts {round_knots(gust_kts)} kts)"
        min_k_rounded = round_knots(biggest["min_k"])
        w_kts_rounded = round_knots(wind_kts)
        yr_str = f" ({biggest['year']})" if biggest.get("year") else ""
        kite_desc = f"{biggest['brand']} {biggest['model']}{yr_str} {biggest['size']}m"

        # Check if user has an even bigger kite left at home (inactive in inventory)
        bigger_at_home = []
        if all_inventory:
            for k in all_inventory:
                if not k.get("active", True) and k.get("size", 0) > biggest["size"]:
                    bigger_at_home.append(k)

        bigger_home_tip = ""
        if bigger_at_home:
            b_home = max(bigger_at_home, key=lambda k: k["size"])
            b_yr = f" ({b_home['year']})" if b_home.get("year") else ""
            bigger_home_tip = f" 💡 Pack your {b_home['brand']} {b_home['model']}{b_yr} {b_home['size']}m from home: `/take all`"

        if slot_hour is not None and slot_hour < 12:
            return f"☕ Too early for Caipi time, enjoy a beach coffee :) Wind ({w_kts_rounded} kts) is too light for your {kite_desc} (min ~{min_k_rounded} kts) — enjoy the morning ocean view! ☕🥐{bigger_home_tip}"
        return f"🍹 Caipirinha Time! Wind ({w_kts_rounded} kts) is too light for your {kite_desc} (min ~{min_k_rounded} kts) — none of your gear fits, time to chill at the beach bar! 🏖️🍹{bigger_home_tip}"

    # 4. Wind above max of active quiver
    if wind_kts > max(maxs):
        max_k_rounded = round_knots(smallest["max_k"])
        if wind_kts <= smallest["max_k"] + 4:
            return f"{smallest['display_name']} (🚨 Overpowered — max ~{max_k_rounded} kts, depower fully){home_tip}"
        elif wind_kts <= smallest["max_k"] + 8:
            return f"{smallest['display_name']} (🚨 Heavily Overpowered — max ~{max_k_rounded} kts!){home_tip}"
        else:
            if slot_hour is not None and slot_hour < 12:
                return f"☕ Holy Storm Coffee Time! Nuking at {round_knots(wind_kts)} kts — too wild for your {smallest['display_name']} (max ~{max_k_rounded} kts). Grab a hot brew and watch the show safely from the beach cafe! ☕⚡{home_tip}"
            if home_tip:
                return f"🍹 Double Caipirinha Time! Nuking at {round_knots(wind_kts)} kts — too wild for your {smallest['display_name']} (max ~{max_k_rounded} kts). Watch from the beach bar! 🍹🔥{home_tip}"
            return f"🍹 Double Caipirinha Time! Nuking at {round_knots(wind_kts)} kts — too wild for your {smallest['display_name']} (max ~{max_k_rounded} kts). Enjoy a cocktail and watch the big air show! 🍹🔥"

    nearest = min(evaluated, key=lambda k: k["dist_to_sweet"])
    return f"{nearest['display_name']} (Marginal)"


def build_quiver_header_text(inventory: list, active_kites: list) -> str:
    if not inventory:
        return "  ⚠️ *No kites registered yet!* Enter your gear:\n  👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`"
    if not active_kites:
        return "  ⚠️ *No active kites in bag today!* Type `/take all` to activate your gear."
    lines = []
    for k in active_kites:
        yr = f" ({k['year']})" if k.get("year") else ""
        lines.append(f"  • {k['brand']} {k['model']}{yr} {k['size']}m")
    return "\n".join(lines)


def format_tides_text(tides: list) -> str:
    if not tides:
        return "• Tide data unavailable for spot."
    highs = [f"{t['time']} ({t['height']:+.2f}m)" for t in tides if t["type"] == "High"]
    lows = [f"{t['time']} ({t['height']:+.2f}m)" for t in tides if t["type"] == "Low"]
    lines = []
    if lows:
        lines.append(f"• ⬇️ *Low Tide:* {' | '.join(lows)}")
    if highs:
        lines.append(f"• ⬆️ *High Tide:* {' | '.join(highs)}")
    return "\n".join(lines)


def format_briefing(forecast: dict, user_profile: dict) -> str:
    spot = user_profile.get("spot", {})
    spot_now = get_spot_local_now(spot, forecast.get("utc_offset_seconds"))
    date_str = spot_now.strftime("%A, %b %d")
    time_str = spot_now.strftime("%H:%M")

    rider_name = user_profile.get("rider_name", "Kiter")
    weight = user_profile.get("rider_weight_kg", 75.0)
    board = user_profile.get("board_type", "Twintip")
    level = user_profile.get("level", "intermediate").capitalize()

    inventory = user_profile.get("inventory", [])
    active_kites = [k for k in inventory if k.get("active", True)]

    quiver_str = build_quiver_header_text(inventory, active_kites)

    shore = forecast.get("shoreline", {})
    stab = forecast.get("stability", {})
    wet = forecast.get("wetsuit", {})
    cons = forecast.get("consensus", {})

    peak = forecast.get("peak_session", {})
    thermal = forecast.get("thermal", {})
    peak_line = f"• *Peak Session Window:* {peak.get('tag', '12:00 – 15:30')}" if peak else ""
    thermal_line = f"• *Thermal Effect:* Active (+{thermal.get('boost_kts', 2.5)} kts · {thermal.get('reason', '')})" if thermal.get("is_active") else ""

    lines = [
        f"🏄‍♂️ *Kitesurf Morning Briefing: {forecast['spot']}*",
        f"📅 *Date:* {date_str} (Local Time: {time_str})",
        f"👤 *Rider:* {rider_name} · {weight}kg ({board} · {level})",
        f"🎒 *Available Gear:*",
        quiver_str,
        f"\n🌡 *Temp:* {forecast['temp_min']}°C – {forecast['temp_max']}°C · {wet.get('tag', '🩳 Boardshorts')}",
        f"🛡 *Conditions Overview:*",
        f"• *Coast Safety:* {shore.get('tag', '🟢 Safe')} ({shore.get('description', '')})",
        f"• *Wind Stability:* ⚡ *{stab.get('rating', '9/10')}* ({stab.get('label', '')})",
        f"• *Thermal Guide:* {wet.get('advice', '')}",
        f"• *Model Consensus:* {cons.get('tag', '🎯 90% Consensus')}"
    ]
    if peak_line:
        lines.append(peak_line)
    if thermal_line:
        lines.append(thermal_line)

    lines.extend([
        f"\n🌊 *Tides Today:*",
        format_tides_text(forecast.get("tides", [])),
        f"\n🎯 *Daylight Schedule (07:00 – 19:00):*"
    ])

    for slot_name, slot in forecast["schedule"].items():
        rec = recommend_from_available_quiver(weight, active_kites, slot["wind_kts"], slot["gust_kts"], all_inventory=inventory, level=level, board=board)
        w_kts = round_knots(slot['wind_kts'])
        g_kts = round_knots(slot['gust_kts'])
        slot_stab = slot.get("stability", {}).get("score", "-")
        slot_shore = slot.get("shoreline", {}).get("type", "")
        slot_tag = f" [{slot_shore} · ⚡{slot_stab}/10]" if slot_shore else ""
        lines.append(
            f"• *{slot_name}:* {w_kts} kts (gusts {g_kts} kts, {slot['direction']}){slot_tag} "
            f"→ {rec}"
        )

    if forecast["max_gust"] >= GUST_WARNING_THRESHOLD_KTS:
        lines.append(f"\n⚠️ *Gust Alert:* Max gusts reaching *{round_knots(forecast['max_gust'])} knots* today.")

    if not inventory:
        lines.append("\n⚠️ *Action Required:* No kites registered yet! Please enter your gear:\n👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`")

    lines.append("\n_Need live conditions? Tap below for /report_")
    return "\n".join(lines)


def format_tomorrow_report(forecast: dict, user_profile: dict, is_evening_auto: bool = False) -> str:
    spot = user_profile.get("spot", {})
    spot_now = get_spot_local_now(spot, forecast.get("utc_offset_seconds"))
    tomorrow_date = spot_now + timedelta(days=1)
    
    local_time_str = spot_now.strftime("%H:%M")
    tomorrow_date_str = tomorrow_date.strftime("%A, %b %d")

    rider_name = user_profile.get("rider_name", "Kiter")
    weight = user_profile.get("rider_weight_kg", 75.0)
    board = user_profile.get("board_type", "Twintip")
    level = user_profile.get("level", "intermediate").capitalize()

    inventory = user_profile.get("inventory", [])
    active_kites = [k for k in inventory if k.get("active", True)]

    t_min = forecast.get("tomorrow_temp_min", forecast.get("temp_min", 25))
    t_max = forecast.get("tomorrow_temp_max", forecast.get("temp_max", 31))
    max_gust = round_knots(forecast.get("tomorrow_max_gust", forecast.get("max_gust", 26)))

    tmrw_wet = forecast.get("tomorrow_wetsuit", forecast.get("wetsuit", {}))
    cons = forecast.get("consensus", {})
    quiver_str = build_quiver_header_text(inventory, active_kites)

    tmrw_peak = forecast.get("tomorrow_peak_session") or forecast.get("peak_session", {})
    tmrw_thermal = forecast.get("thermal", {})

    lines = [
        f"🌅 *Tomorrow's Kitesurf Forecast: {forecast['spot']}*",
        f"📅 *Date:* {tomorrow_date_str} (Day After)",
        f"📍 *Spot Local Time:* {local_time_str}",
        f"👤 *Rider:* {rider_name} · {weight}kg ({board} · {level})",
        f"🎒 *Available Gear:*",
        quiver_str,
        f"\n🌡 *Temp:* {t_min}°C – {t_max}°C · 💨 *Max Gusts:* {max_gust} kts",
        f"🩳 *Thermal Guide:* {tmrw_wet.get('tag', '🩳 Boardshorts')} ({tmrw_wet.get('advice', '')})",
        f"🎯 *Forecast Reliability:* {cons.get('tag', '🎯 90% Consensus')}"
    ]
    if tmrw_peak and tmrw_peak.get("tag"):
        lines.append(f"• *Peak Session Window:* {tmrw_peak['tag']}")
    if tmrw_thermal and tmrw_thermal.get("is_active"):
        lines.append(f"• *Thermal Effect:* Active (+{tmrw_thermal.get('boost_kts', 2.5)} kts · {tmrw_thermal.get('reason', '')})")

    if is_evening_auto:
        lines.append(f"\n_🌙 Past 17:00 local time — showing tomorrow's forecast so you can pack your gear tonight!_")
    else:
        lines.append(f"\n_📋 Showing requested tomorrow's forecast:_")

    lines.append(f"\n🌬 *Tomorrow's Daylight Schedule (07:00 – 19:00):*")
    schedule = forecast.get("schedule_tomorrow") or forecast.get("schedule", {})
    for slot_name, slot in schedule.items():
        rec = recommend_from_available_quiver(weight, active_kites, slot["wind_kts"], slot["gust_kts"], all_inventory=inventory, level=level, board=board)
        w_kts = round_knots(slot['wind_kts'])
        g_kts = round_knots(slot['gust_kts'])
        slot_stab = slot.get("stability", {}).get("score", "-")
        slot_shore = slot.get("shoreline", {}).get("type", "")
        slot_tag = f" [{slot_shore} · ⚡{slot_stab}/10]" if slot_shore else ""
        lines.append(f"• *{slot_name}:* {w_kts} kts (gusts {g_kts} kts, {slot.get('direction', 'E')}){slot_tag} → {rec}")

    lines.append(f"\n🌊 *Tomorrow's Tides:*")
    lines.append(format_tides_text(forecast.get("tides_tomorrow", [])))

    if max_gust >= GUST_WARNING_THRESHOLD_KTS:
        lines.append(f"\n⚠️ *Gust Alert:* Max gusts reaching *{max_gust} knots* tomorrow.")

    if not inventory:
        lines.append("\n⚠️ *Action Required:* No kites registered yet! Please enter your gear:\n👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`")

    lines.append("\n_Tip: For live conditions right now, type `/report today`._")
    lines.append("_On a new spot? Tap the button below to update via phone GPS!_")
    return "\n".join(lines)


def format_realtime_report(forecast: dict, user_profile: dict) -> str:
    spot = user_profile.get("spot", {})
    spot_now = get_spot_local_now(spot, forecast.get("utc_offset_seconds"))
    local_time_str = spot_now.strftime("%H:%M")
    local_date_str = spot_now.strftime("%A, %b %d")

    rider_name = user_profile.get("rider_name", "Kiter")
    weight = user_profile.get("rider_weight_kg", 75.0)
    board = user_profile.get("board_type", "Twintip")
    level = user_profile.get("level", "intermediate").capitalize()

    inventory = user_profile.get("inventory", [])
    active_kites = [k for k in inventory if k.get("active", True)]

    cur = forecast.get("current", {})
    wind_kts = round_knots(cur.get("wind_kts", 16.0))
    gust_kts = round_knots(cur.get("gust_kts", 22.0))
    direct = cur.get("direction", "E")
    temp = cur.get("temp", 28.0)

    shore = forecast.get("shoreline", {})
    stab = forecast.get("stability", {})
    wet = forecast.get("wetsuit", {})
    cons = forecast.get("consensus", {})

    rec = recommend_from_available_quiver(weight, active_kites, wind_kts, gust_kts, all_inventory=inventory, level=level, board=board)
    quiver_str = build_quiver_header_text(inventory, active_kites)

    peak = forecast.get("peak_session", {})
    thermal = forecast.get("thermal", {})

    lines = [
        f"🏄‍♂️ *Live Spot Report: {forecast['spot']}*",
        f"📍 *Spot Local Time:* {local_time_str} · {local_date_str}",
        f"🌡 *Temp:* {temp}°C (Sea: {wet.get('water_temp', temp)}°C)",
        f"👤 *Rider:* {rider_name} · {weight}kg ({board} · {level})",
        f"🎒 *Available Gear:*",
        quiver_str,
        f"\n🌬 *Wind Right Now:*",
        f"• *Speed:* *{wind_kts} knots* (Gusts: *{gust_kts} knots*, {direct})",
        f"• *Coast Safety:* {shore.get('tag', '🟢 Safe')} ({shore.get('description', '')})",
        f"• *Wind Stability:* ⚡ *{stab.get('rating', '9/10')}* ({stab.get('label', '')})",
        f"• *Thermal Guide:* {wet.get('tag', '🩳 Boardshorts')} ({wet.get('advice', '')})",
        f"• *Forecast Reliability:* {cons.get('tag', '🎯 90% Consensus')} ({cons.get('description', '')})",
        f"• *Right Now Recommendation:* → {rec}\n"
    ]
    if peak and peak.get("tag"):
        lines.append(f"• *Today's Peak Window:* {peak['tag']}")
    if thermal and thermal.get("is_active"):
        lines.append(f"• *Thermal Effect:* Active (+{thermal.get('boost_kts', 2.5)} kts · {thermal.get('reason', '')})")

    lines.extend([
        f"\n🌊 *Tides Today:*",
        format_tides_text(forecast.get("tides", [])),
        f"\n📅 *Upcoming Today (07:00 – 19:00):*"
    ])

    for slot_name, slot in forecast.get("schedule", {}).items():
        r = recommend_from_available_quiver(weight, active_kites, slot["wind_kts"], slot["gust_kts"], all_inventory=inventory, level=level, board=board)
        w_kts = round_knots(slot['wind_kts'])
        g_kts = round_knots(slot['gust_kts'])
        slot_stab = slot.get("stability", {}).get("score", "-")
        slot_shore = slot.get("shoreline", {}).get("type", "")
        slot_tag = f" [{slot_shore} · ⚡{slot_stab}/10]" if slot_shore else ""
        lines.append(f"• *{slot_name}:* {w_kts} kts (gusts {g_kts} kts){slot_tag} → {r}")

    if not inventory:
        lines.append("\n⚠️ *Action Required:* No kites registered yet! Please enter your gear:\n👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`")

    lines.append("\n_Tip: Type `/report tomorrow` anytime to see tomorrow's forecast!_")
    lines.append("_On a new spot? Tap the button below to update via phone GPS!_")
    return "\n".join(lines)


def parse_kite_params(raw_text: str):
    raw = raw_text.strip()

    # 1. First, check if pure tagged format: (brand)... (model)... (size)... (year)...
    if "(brand)" in raw.lower() or "(model)" in raw.lower() or "(size)" in raw.lower():
        tags = {}
        for m in re.finditer(r"\(([a-zA-Z]+)\)\s*([^\(]+)", raw):
            tags[m.group(1).lower().strip()] = m.group(2).strip()
        brand = tags.get("brand", "").strip()
        model = tags.get("model", "").strip()
        size_raw = tags.get("size", "0")
        size = float(re.sub(r"[^\d.]", "", size_raw) or 0)
        year_raw = tags.get("year", "")
        year = int(re.sub(r"[^\d]", "", year_raw)) if year_raw else 2024
        return brand, model, year, size

    # 2. Extract Year if present
    # Could be (year)2024, (year) 2024, (2024), [2024], year 2024, yr 2024, or a 4-digit number
    year = 2024

    # Look for (year) <num> or (year)<num>
    m_year_tag = re.search(r"\(year\)\s*(\d{4})", raw, re.IGNORECASE)
    if m_year_tag:
        year = int(m_year_tag.group(1))
        raw = raw[:m_year_tag.start()] + " " + raw[m_year_tag.end():]
    else:
        # Look for (2024) or [2024]
        m_paren_year = re.search(r"[\(\[]\s*(\d{4})\s*[\)\]]", raw)
        if m_paren_year:
            year = int(m_paren_year.group(1))
            raw = raw[:m_paren_year.start()] + " " + raw[m_paren_year.end():]
        else:
            # Look for 'year 2024' or 'yr 2024'
            m_word_year = re.search(r"\b(?:year|yr)\s*[:=]?\s*(\d{4})\b", raw, re.IGNORECASE)
            if m_word_year:
                year = int(m_word_year.group(1))
                raw = raw[:m_word_year.start()] + " " + raw[m_word_year.end():]

    # Clean leftover (year) if user wrote (year) without digits
    raw = re.sub(r"\(year\)", "", raw, flags=re.IGNORECASE).strip()

    # Split into remaining tokens
    tokens = raw.split()
    if len(tokens) < 2:
        return None, None, None, None

    # Check if a 4-digit year is among remaining tokens (e.g. 1990-2035)
    year_idx = None
    for idx, t in enumerate(tokens):
        if t.isdigit() and len(t) == 4 and 1990 <= int(t) <= 2035:
            year = int(t)
            year_idx = idx
            break

    if year_idx is not None:
        tokens.pop(year_idx)

    if len(tokens) < 2:
        return None, None, None, None

    # Find size token: look for token with 'm' (e.g. 10m, 11M, 9.5m) or the last numeric token
    size = None
    size_idx = None
    for idx, t in enumerate(tokens):
        m_size = re.match(r"^(\d+(?:\.\d+)?)[mM]$", t)
        if m_size:
            size = float(m_size.group(1))
            size_idx = idx
            break

    if size is None:
        try:
            size = float(tokens[-1])
            size_idx = len(tokens) - 1
        except ValueError:
            for idx in range(len(tokens) - 1, 0, -1):
                try:
                    val = float(tokens[idx])
                    if 3.0 <= val <= 25.0:
                        size = val
                        size_idx = idx
                        break
                except ValueError:
                    pass

    if size is None or size_idx is None:
        return None, None, None, None

    tokens.pop(size_idx)
    if not tokens:
        return None, None, None, None

    brand = tokens[0]
    model = " ".join(tokens[1:]) if len(tokens) > 1 else tokens[0]

    return brand, model, year, size


def get_user_kites_list_text(user_profile: dict) -> str:
    inventory = user_profile.get("inventory", [])
    lines = [
        "🪁 *Your Available Kites:*",
        f"👤 Rider: {user_profile.get('rider_name', 'Kiter')} · {user_profile.get('rider_weight_kg', 75)}kg\n"
    ]
    if not inventory:
        lines.append("⚠️ *No quiver existing yet!*")
        lines.append("You have not entered any kites. Please add your kites below to get personalized gear recommendations:\n")
    for idx, k in enumerate(inventory, start=1):
        status = "✅ In Bag" if k.get("active", True) else "🏠 Left Home"
        yr = f" ({k['year']})" if k.get("year") else ""
        specs = lookup_kite_specs(k["brand"], k["model"], k["size"])
        lines.append(f"  *{idx}.* [{status}] *{k['brand']} {k['model']}{yr} {k['size']}m* _{specs['material']}_")

    lines.append("\n✏️ *To set or change a kite slot:*")
    lines.append("• `/kite 1 Duotone Rebel SLS 10 (2024)`")
    lines.append("• `/kite 2 North Orbit 9 (2023)`")
    lines.append("• `/kite 3 Cabrinha Switchblade 12 (2022)`")
    lines.append("• `/kite 1 <Brand> <Model> <Size> (<Year>)`")
    lines.append("\n🎒 *To pick what you have with you today:*")
    lines.append("• `/take 1, 2` → (Only takes kite 1 & 2)")
    lines.append("• `/take all` → (Takes all kites)")
    lines.append("\n🗑️ *To delete or reset:*")
    lines.append("• `/delkite 1` → (Deletes kite slot 1)")
    lines.append("• `/reset profile` → (Wipes all kites & resets profile clean)")
    lines.append("\n🏄 *For live conditions & kite choice:* `/report`")
    return "\n".join(lines)


def reverse_geocode(lat: float, lon: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            addr = data.get("address", {})
            name = (
                data.get("name")
                or addr.get("beach")
                or addr.get("suburb")
                or addr.get("village")
                or addr.get("town")
                or addr.get("city")
                or "Current Location"
            )
            country = addr.get("country", "")
            return f"{name}, {country}".strip(", ")
    except Exception:
        return f"Spot ({lat:.3f}, {lon:.3f})"


def geocode_place_name(query: str, ref_lat: float = None, ref_lon: float = None):
    if not query:
        return None, None, None

    # 1. Check curated global kite spots catalog first
    try:
        from kite_spots import search_spots_catalog, haversine_distance_km
        matches = search_spots_catalog(query, max_results=5)
        if matches:
            if ref_lat is not None and ref_lon is not None and len(matches) > 1:
                matches.sort(key=lambda s: haversine_distance_km(ref_lat, ref_lon, s["lat"], s["lon"]))
            top = matches[0]
            return float(top["lat"]), float(top["lon"]), top["name"]
    except Exception:
        pass

    # 2. Open-Meteo High-Availability Geocoding API with smart coastal & proximity scoring
    try:
        from kite_spots import haversine_distance_km
    except Exception:
        def haversine_distance_km(lat1, lon1, lat2, lon2):
            R = 6371.0
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return 2 * R * math.asin(math.sqrt(a))

    try:
        om_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(query.strip())}&count=10&language=en&format=json"
        om_req = urllib.request.Request(om_url, headers={"User-Agent": "KiteForecastBot/1.0"})
        with urllib.request.urlopen(om_req, context=SSL_CTX, timeout=6) as resp:
            om_data = json.loads(resp.read().decode("utf-8"))
            results = om_data.get("results")
            if results and len(results) > 0:
                candidates = []
                q_lower = query.strip().lower()
                for item in results:
                    score = 100
                    # Elevation scoring: kiteboarding spots are at sea level / coastal beaches
                    elev = item.get("elevation")
                    if elev is not None:
                        if elev <= 20.0:
                            score += 40  # Sea-level beach
                        elif elev <= 60.0:
                            score += 15
                        elif elev > 150.0:
                            score -= 50  # Inland hills / mountains
                        elif elev > 300.0:
                            score -= 80

                    # Proximity scoring if reference coordinates are provided (e.g. user currently at Cumbuco)
                    c_lat = float(item["latitude"])
                    c_lon = float(item["longitude"])
                    if ref_lat is not None and ref_lon is not None:
                        dist = haversine_distance_km(ref_lat, ref_lon, c_lat, c_lon)
                        if dist < 200.0:
                            score += 80
                        elif dist < 600.0:
                            score += 40
                        elif dist < 1500.0:
                            score += 20
                        elif dist > 5000.0:
                            score -= 30

                    # Query keyword match bonus
                    admin1 = (item.get("admin1") or "").lower()
                    country = (item.get("country") or "").lower()
                    name = (item.get("name") or "").lower()
                    if q_lower in name:
                        score += 30
                    if q_lower in country or q_lower in admin1:
                        score += 20

                    candidates.append((score, item))

                candidates.sort(key=lambda x: -x[0])
                best = candidates[0][1]

                name_parts = [best.get("name", "")]
                if best.get("admin1"):
                    name_parts.append(best["admin1"])
                if best.get("country"):
                    name_parts.append(best["country"])
                full_name = ", ".join(name_parts)
                return float(best["latitude"]), float(best["longitude"]), full_name
    except Exception:
        pass

    # 3. Fallback to OpenStreetMap Nominatim
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0 (team@holygust.com)"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"].split(",")[0]
    except Exception:
        pass
    return None, None, None


def send_telegram(message: str, token: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": REPLY_KEYBOARD
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def send_photo_telegram(photo_url: str, caption: str, token: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "reply_markup": REPLY_KEYBOARD
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Telegram photo error: {e}")
        return False


def handle_telegram_command(text: str, message_obj: dict, config: dict) -> str:
    user_info = message_obj.get("from", {})
    user_id = user_info.get("id")
    first_name = user_info.get("first_name", "Kiter")
    chat_id = str(message_obj.get("chat", {}).get("id"))

    user_profile, is_new = get_or_create_user(config, user_id, first_name)

    # 1. Location GPS pin from phone
    loc = message_obj.get("location")
    if loc:
        lat, lon = loc["latitude"], loc["longitude"]
        spot_name = reverse_geocode(lat, lon)
        user_profile["spot"] = {
            "name": spot_name,
            "lat": lat,
            "lon": lon,
            "timezone": "auto"
        }
        save_config(config)
        forecast = fetch_live_forecast(user_profile["spot"])
        spot_now = get_spot_local_now(user_profile["spot"], forecast.get("utc_offset_seconds"))
        if spot_now.hour >= 17:
            report = format_tomorrow_report(forecast, user_profile, is_evening_auto=True)
        else:
            report = format_realtime_report(forecast, user_profile)
        return f"📍 *GPS Position Updated for {user_profile['rider_name']}:* {spot_name}\n\n" + report

    cmd = text.strip()

    # 2. First-time welcome or /start (QR code scan or fresh user)
    if cmd.startswith("/start") or is_new:
        save_config(config)
        has_kites = bool(user_profile.get("inventory"))
        quiver_alert = (
            "⚠️ *No kites registered yet!* To calculate your personalized wind ranges and kite choices, you need to enter your gear first."
            if not has_kites
            else f"🎒 *Your gear has {len(user_profile.get('inventory', []))} kite(s) registered.* (Type `/kites` to inspect)"
        )
        welcome_intro = (
            f"👋 *Welcome to HolyGust, {first_name}!* 🏄‍♂️\n\n"
            f"{quiver_alert}\n\n"
            "⚡ *Quick Setup Guide:*\n"
            f"1️⃣ *Set your rider weight:* `/weight 75` (currently {user_profile['rider_weight_kg']} kg — tunes wind ranges)\n"
            "2️⃣ *Add your kites by slot (including year):*\n"
            "   • `/kite 1 <Brand> <Model> <Size> (<Year>)`\n"
            "   _Examples:_\n"
            "   • `/kite 1 Duotone Rebel SLS 10 (2024)`\n"
            "   • `/kite 2 North Orbit 9 (2023)`\n"
            "   • `/kite 3 Cabrinha Switchblade 12 (2022)`\n"
            "3️⃣ *Pick your spot & get forecast:*\n"
            "   • Tap `[ 📍 Send Current Location & Report ]` for instant phone GPS\n"
            "   • Or type `/spot Tarifa` or `/spot Cumbuco`\n"
            "   • Tap `[ /report ]` (Live conditions, auto-switches to tomorrow after 17:00)\n"
            "   • Tap `[ /report tomorrow ]` anytime for tomorrow's forecast\n\n"
            "🎒 *Gear Management:*\n"
            "• `/kites` → View your kites and bag status\n"
            "• `/take 1, 2` → Pick which kites you brought to the beach today\n"
            "• `/take all` → Mark all your kites active in your bag\n"
            "• `/reset profile` → Wipe your gear and start over\n\n"
            "_All calculations and wind ranges will be tuned specifically to YOU and YOUR bag!_"
        )
        return welcome_intro

    elif any(cmd.lower().startswith(p) for p in ["/reset", "/clear"]):
        user_profile["inventory"] = []
        user_profile["rider_weight_kg"] = 75.0
        user_profile["rider_name"] = first_name
        user_profile["board_type"] = "Twintip"
        user_profile["morning_briefing"] = True
        save_config(config)
        return (
            f"🗑️ *Profile & Kites Reset Successfully!* 🏄‍♂️\n\n"
            f"All your kites, custom weight, and saved gear have been wiped clean for *{first_name}*.\n\n"
            "⚠️ *No quiver is currently loaded.*\n\n"
            "⚡ *Set up fresh in 3 quick steps:*\n"
            "1️⃣ *Set your weight:* `/weight 75` (or your weight in kg)\n"
            "2️⃣ *Add your kites by slot (including year):*\n"
            "   • `/kite 1 Duotone Rebel SLS 10 (2024)`\n"
            "   • `/kite 2 North Orbit 9 (2023)`\n"
            "   • `/kite 3 Cabrinha Switchblade 12 (2022)`\n"
            "3️⃣ *Get report:* Tap `[ 📍 Send Current Location & Report ]` or `/report`\n\n"
            "_You have a completely fresh profile! Check `/kites` anytime._"
        )

    elif cmd.startswith("/qr") or cmd.startswith("/share") or cmd.startswith("/invite"):
        qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=600x600&data=https://t.me/KiteForecast_bot&format=png&margin=20"
        caption = (
            "📲 *Share HolyGust with your buddies!*\n\n"
            "Direct link: https://t.me/KiteForecast_bot\n\n"
            "When they scan this QR code or tap the link, they get their own private rider profile, quiver, and GPS spot forecasts!"
        )
        send_photo_telegram(qr_url, caption, config["telegram_token"], chat_id)
        return None

    elif cmd.startswith("/app") or cmd.startswith("/web") or "interactive web app" in cmd.lower():
        return (
            "📱 *HolyGust Interactive Web App:* 🏄‍♂️\n\n"
            "👉 https://holygust.com\n\n"
            "✨ *What you can do in the App:*\n"
            "• Interactive gear garage with brand & model dropdowns\n"
            "• 'In My Backpack' toggle switches for your kites\n"
            "• Real-time rider weight slider (instantly scales wind ranges!)\n"
            "• Live interactive wind & gust bar charts\n"
            "• Tide height wave curves\n"
            "• Instant GPS spot locator\n\n"
            "💡 _Tip: Tap 'Add to Home Screen' in Safari (iOS) or Chrome (Android) to use it just like a native app!_"
        )

    elif cmd.startswith("/setup") or cmd.startswith("/help"):
        return get_user_kites_list_text(user_profile)

    elif cmd.startswith("/report") or cmd.startswith("/now") or cmd.startswith("/tomorrow"):
        cmd_lower = cmd.lower()
        force_tomorrow = any(w in cmd_lower for w in ["tomorrow", "tmrw", "manana", "mañana"]) or cmd.startswith("/tomorrow")
        force_today = any(w in cmd_lower for w in ["today", "hoy"])

        clean_text = cmd
        for prefix in ["/report", "/now", "/tomorrow"]:
            if clean_text.lower().startswith(prefix):
                clean_text = clean_text[len(prefix):].strip()
                break

        words = clean_text.split()
        spot_words = [w for w in words if w.lower() not in ["tomorrow", "tmrw", "manana", "mañana", "today", "hoy"]]
        target_spot = " ".join(spot_words).strip()

        if target_spot:
            lat, lon, resolved_name = geocode_place_name(target_spot)
            if lat and lon:
                user_profile["spot"] = {
                    "name": resolved_name,
                    "lat": lat,
                    "lon": lon,
                    "timezone": "auto"
                }
                save_config(config)

        forecast = fetch_live_forecast(user_profile["spot"])
        spot_now = get_spot_local_now(user_profile["spot"], forecast.get("utc_offset_seconds"))

        if force_tomorrow:
            return format_tomorrow_report(forecast, user_profile, is_evening_auto=False)
        elif not force_today and spot_now.hour >= 17:
            return format_tomorrow_report(forecast, user_profile, is_evening_auto=True)
        else:
            return format_realtime_report(forecast, user_profile)

    elif cmd.startswith("/kites"):
        return get_user_kites_list_text(user_profile)

    elif cmd.startswith("/kite"):
        tokens = cmd.split(maxsplit=2)
        if len(tokens) == 1:
            return get_user_kites_list_text(user_profile)

        slot_str = tokens[1]
        if not slot_str.isdigit():
            return "❌ Please specify a kite slot number (e.g. `/kite 1 Duotone Rebel SLS 11`)."

        slot_idx = int(slot_str) - 1
        inventory = user_profile.setdefault("inventory", [])

        if len(tokens) == 2:
            if 0 <= slot_idx < len(inventory):
                k = inventory[slot_idx]
                specs = lookup_kite_specs(k["brand"], k["model"], k["size"])
                yr = f" ({k['year']})" if k.get("year") else ""
                status = "✅ In Bag" if k.get("active", True) else "🏠 Left Home"
                return (
                    f"🪁 *Kite Slot {slot_idx + 1}:* [{status}]\n"
                    f"• {k['brand']} {k['model']}{yr} *{k['size']}m*\n"
                    f"• Material: {specs['material']}\n"
                    f"• Type: {specs['type']}"
                )
            return f"Kite slot {slot_idx + 1} is currently empty."

        param_text = tokens[2]
        brand, model, year, size = parse_kite_params(param_text)
        if not brand or not model or size <= 0:
            return (
                "❌ Couldn't parse kite details.\n"
                "Examples:\n"
                "• `/kite 1 Duotone Rebel SLS 10 (2024)`\n"
                "• `/kite 2 North Orbit 9 (2023)`\n"
                "• `/kite 3 Cabrinha Switchblade 12 (2022)`\n"
                "• `/kite 1 <Brand> <Model> <Size> (<Year>)`"
            )

        specs = lookup_kite_specs(brand, model, size)
        size_clean = int(size) if size.is_integer() else size

        kite_data = {
            "brand": specs["brand"],
            "model": specs["model"],
            "year": year,
            "size": size_clean,
            "active": True
        }

        if 0 <= slot_idx < len(inventory):
            inventory[slot_idx] = kite_data
        else:
            inventory.append(kite_data)
            slot_idx = len(inventory) - 1

        save_config(config)
        return (
            f"✅ *Kite Slot {slot_idx + 1} Saved for {user_profile['rider_name']}!* 🪁\n"
            f"• *{specs['brand']} {specs['model']} ({year}) {size_clean}m*\n"
            f"• Year: *{year}*\n"
            f"• Frame: _{specs['material']}_\n"
            f"• Discipline: _{specs['type']}_\n"
            f"• Status: Active in bag"
        )

    elif cmd.startswith("/take"):
        sub = cmd[5:].strip()
        inventory = user_profile.get("inventory", [])
        if not sub or sub.lower() == "all":
            for k in inventory:
                k["active"] = True
            save_config(config)
            return f"✅ *All {len(inventory)} kites packed in your bag today, {user_profile['rider_name']}!*"

        req_slots = []
        for token in sub.replace(",", " ").split():
            try:
                req_slots.append(int(token) - 1)
            except ValueError:
                pass

        if req_slots:
            active_names = []
            for idx, k in enumerate(inventory):
                k["active"] = idx in req_slots
                if k["active"]:
                    yr = f" ({k['year']})" if k.get("year") else ""
                    active_names.append(f"{k['brand']} {k['model']}{yr} {k['size']}m")
            save_config(config)
            pack_str = "\n  • " + "\n  • ".join(active_names) if active_names else "None"
            return f"🎒 *Packed in bag for {user_profile['rider_name']}:*{pack_str}\n\n_Other kites marked as left at home._"
        return "❌ Format: `/take 1, 2` or `/take all`"

    elif cmd.startswith("/name"):
        parts = cmd.split(maxsplit=1)
        if len(parts) >= 2:
            new_name = parts[1].strip()
            user_profile["rider_name"] = new_name
            save_config(config)
            return f"✅ *Rider Name updated to:* {new_name}"
        return f"👤 *Current Name:* {user_profile.get('rider_name', 'Kiter')}\nTo change: `/name YourName`"

    elif cmd.startswith("/weight"):
        parts = cmd.split()
        if len(parts) >= 2:
            try:
                new_weight = float(parts[1].replace(",", "."))
                user_profile["rider_weight_kg"] = new_weight
                save_config(config)
                return f"✅ *Weight updated to:* {new_weight} kg for {user_profile['rider_name']}\nQuiver calculations recalibrated."
            except ValueError:
                return "❌ Please enter a valid number (e.g. `/weight 75`)."
        return f"⚖️ *Current weight:* {user_profile.get('rider_weight_kg', 75)} kg\nTo change: `/weight 75`"

    elif cmd.startswith("/level") or cmd.startswith("/skill"):
        parts = cmd.split()
        if len(parts) >= 2:
            new_lvl = parts[1].lower()
            if new_lvl in ["beginner", "beg", "novice"]:
                user_profile["level"] = "beginner"
            elif new_lvl in ["advanced", "adv", "pro", "expert"]:
                user_profile["level"] = "advanced"
            else:
                user_profile["level"] = "intermediate"
            save_config(config)
            return f"🎯 *Rider Level updated to:* {user_profile['level'].capitalize()} for {user_profile['rider_name']}.\nWind ranges and overpower limits recalibrated."
        cur_lvl = user_profile.get("level", "intermediate").capitalize()
        return f"🎯 *Current Rider Level:* {cur_lvl}\nTo change: `/level beginner`, `/level medium`, or `/level advanced`."

    elif cmd.startswith("/year"):
        parts = cmd.split()
        if len(parts) >= 3:
            try:
                idx = int(parts[1]) - 1
                new_yr = int(parts[2])
                inventory = user_profile.get("inventory", [])
                if 0 <= idx < len(inventory):
                    inventory[idx]["year"] = new_yr
                    save_config(config)
                    return f"✅ *Updated:* {inventory[idx]['brand']} {inventory[idx]['model']} {inventory[idx]['size']}m year set to *{new_yr}*."
                return "❌ Kite index out of range. Check list with `/kites`."
            except ValueError:
                return "❌ Format: `/year <kite_number> <year>` (e.g. `/year 1 2024`)"
        return "❌ Format: `/year <kite_number> <year>` (e.g. `/year 1 2024`)"

    elif cmd.startswith("/delkite"):
        parts = cmd.split()
        if len(parts) >= 2:
            try:
                idx = int(parts[1]) - 1
                inventory = user_profile.get("inventory", [])
                if 0 <= idx < len(inventory):
                    removed = inventory.pop(idx)
                    save_config(config)
                    return f"🗑 *Removed slot {idx + 1}:* {removed['brand']} {removed['model']} {removed['size']}m"
                return "❌ Kite index out of range. Check list with `/kites`."
            except ValueError:
                return "❌ Format: `/delkite <number>` (e.g. `/delkite 2`)"
        return "❌ Format: `/delkite <number>` (e.g. `/delkite 2`)"

    elif cmd.startswith("/tide"):
        spot = user_profile.get("spot", {})
        tides = fetch_tides(spot["lat"], spot["lon"], spot.get("timezone", "auto"))
        return f"🌊 *Tides for {spot.get('name', 'Spot')}:*\n" + format_tides_text(tides)

    elif cmd.startswith("/spot"):
        parts = cmd.split(maxsplit=1)
        if len(parts) > 1 and parts[1].strip():
            place = parts[1].strip()
            lat, lon, res_name = geocode_place_name(place)
            if lat and lon:
                user_profile["spot"] = {"name": res_name, "lat": lat, "lon": lon, "timezone": "auto"}
                save_config(config)
                return f"📍 *Spot updated to:* {res_name}\nCoordinates: `{lat:.4f}, {lon:.4f}`\n\nTap `/report` below to see live conditions!"
            return f"❌ Could not find location for '{place}'."

        spot = user_profile.get("spot", {})
        return f"📍 *Current Spot for {user_profile['rider_name']}:* {spot.get('name')}\nCoordinates: `{spot.get('lat')}, {spot.get('lon')}`\n\n_Tip: Type `/spot Taiba` or tap 'Send Location' button below to update!_"

    elif cmd.startswith("/briefing") or cmd.startswith("/today"):
        forecast = fetch_live_forecast(user_profile["spot"])
        return format_briefing(forecast, user_profile)

    return None


def start_embedded_http_server(port: int = 8080):
    """Embeds an HTTP server serving the interactive PWA web app, REST API endpoints, and cloud health checks."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, "web")

    class AppServerHandler(BaseHTTPRequestHandler):
        def _send_cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def do_OPTIONS(self):
            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()

        def do_HEAD(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            host = (self.headers.get("Host") or "").lower().split(":")[0]
            if "onrender.com" in host and path not in ["/api/health", "/health", "/ping"]:
                self.send_response(301)
                self.send_header("Location", f"https://holygust.com{self.path}")
                self._send_cors_headers()
                self.end_headers()
                return
            self.send_response(200)
            if path in ["/api/health", "/health", "/ping"]:
                self.send_header("Content-Type", "application/json")
            elif path in ["/", "/index.html"]:
                self.send_header("Content-Type", "text/html; charset=utf-8")
            else:
                self.send_header("Content-Type", "text/plain")
            self._send_cors_headers()
            self.end_headers()

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            params = urllib.parse.parse_qs(parsed.query)
            user_agent = (self.headers.get("User-Agent") or "").lower()

            # 1. Health check & uptime monitors (Render, cron-job.org, UptimeRobot, etc.)
            if path in ["/api/health", "/health", "/ping"]:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"status": "ok", "service": "KiteForecastApp", "multi_user": true}\n')
                return

            # CANONICAL REDIRECT: Redirect all old onrender.com domain traffic to https://holygust.com
            host = (self.headers.get("Host") or "").lower().split(":")[0]
            if "onrender.com" in host and "beta" not in host:
                target_url = f"https://holygust.com{self.path}"
                self.send_response(301)
                self.send_header("Location", target_url)
                self.send_header("Cache-Control", "public, max-age=86400")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(f"Redirecting permanently to {target_url}\n".encode("utf-8"))
                return

            # Intercept uptime monitoring bots hitting root URL to prevent "Response data too big" errors
            # (e.g. cron-job.org free accounts enforce a small response size buffer)
            if path in ["/", "/index.html"] and any(bot in user_agent for bot in ["cron-job", "uptimerobot", "betteruptime", "pingdom", "statuscake"]):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b"OK\n")
                return

            # BETA: 1-Click Browser Decision (Telegram Link Fallback)
            if path == "/api/beta/decision":
                action = (params.get("action", [""])[0]).lower()
                email = (params.get("email", [""])[0]).strip().lower()
                token_val = params.get("token", [""])[0]
                expected = get_beta_decision_token(email)
                
                if not token_val or token_val != expected:
                    self.send_response(403)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"<h1>Invalid or expired beta decision link</h1>")
                    return
                
                if action == "approve":
                    _, r_name = approve_beta_rider(email)
                    status_text = f"⚡ {r_name} ({email}) has been APPROVED as a HolyGust Beta Rider! Welcome email sent."
                    badge_color = "#f59e0b"
                else:
                    decline_beta_rider(email)
                    status_text = f"❌ Beta request for {email} was declined."
                    badge_color = "#ef4444"
                
                html_resp = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>HolyGust Beta Administration</title></head>
<body style="background:#0b1120; color:#f8fafc; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display:flex; align-items:center; justify-content:center; min-height:100vh; margin:0; padding:20px;">
  <div style="background:#0f172a; padding:32px 24px; border-radius:24px; border:1px solid #1e293b; max-width:440px; text-align:center; box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);">
    <div style="font-size:36px; margin-bottom:12px;">⚡</div>
    <h2 style="color:{badge_color}; margin:0 0 12px; font-size:20px; font-weight:800;">HolyGust Beta Administration</h2>
    <p style="font-size:15px; line-height:1.6; color:#94a3b8; margin:0 0 24px;">{status_text}</p>
    <a href="https://holygust.com" style="display:inline-block; background:#0284c7; color:#ffffff; font-weight:700; font-size:14px; padding:12px 28px; border-radius:12px; text-decoration:none;">Open HolyGust</a>
  </div>
</body>
</html>"""
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_resp.encode("utf-8"))
                return

            # 2. API: Stats & User Count
            if path == "/api/stats":
                db = load_users_db()
                users_list = [
                    {
                        "email": u.get("email"),
                        "name": u.get("name"),
                        "nationality": u.get("nationality", ""),
                        "registered_at": u.get("registered_at"),
                        "gear_count": len(u.get("gear", [])),
                        "weight_kg": u.get("weight_kg"),
                        "level": u.get("level")
                    }
                    for u in db.get("users", {}).values()
                ]
                stats = {
                    "total_users": len(db.get("users", {})),
                    "total_feedback": len(db.get("feedback", [])),
                    "users": users_list
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-cache")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(stats).encode("utf-8"))
                return

            # 2b. ADMIN DASHBOARD: Spot Intelligence & Rider Demographics
            if path in ["/admin", "/admin/spots"]:
                import spot_telemetry, admin_dashboard_html
                summary = spot_telemetry.get_spot_analytics_summary()
                html_out = admin_dashboard_html.render_admin_dashboard(summary)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(html_out.encode("utf-8"))
                return

            # 2c. API: Spot Analytics & Intelligence JSON
            if path == "/api/admin/spot-insights":
                import spot_telemetry
                summary = spot_telemetry.get_spot_analytics_summary()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-cache")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(summary).encode("utf-8"))
                return

            # 3. API: Kite Catalog
            if path == "/api/catalog":
                from kite_catalog import KITE_CATALOG
                data = json.dumps(KITE_CATALOG).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(data)
                return

            # 3. API: Weather & Tides Forecast
            if path == "/api/forecast":
                try:
                    lat = float(params.get("lat", [-3.6247])[0])
                    lon = float(params.get("lon", [-38.7297])[0])
                    name = params.get("name", ["Spot"])[0]
                    tz = params.get("timezone", ["auto"])[0]
                    beach_angle_param = params.get("beach_angle", [None])[0]
                    beach_angle = None
                    if beach_angle_param not in [None, ""]:
                        try:
                            beach_angle = float(beach_angle_param)
                        except ValueError:
                            pass
                    # Telemetry tracking for spot activity & rider demographics
                    try:
                        import spot_telemetry
                        rider_p = params.get("rider", [""])[0]
                        email_p = params.get("email", [""])[0]
                        nat_p = params.get("nationality", [""])[0]
                        ip_p = self.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (self.client_address[0] if self.client_address else "")
                        spot_telemetry.record_spot_view(
                            spot_name=name,
                            lat=lat,
                            lon=lon,
                            email=email_p,
                            rider_name=rider_p,
                            nationality=nat_p,
                            ip=ip_p
                        )
                    except Exception:
                        pass

                    f_data = fetch_live_forecast({"lat": lat, "lon": lon, "name": name, "timezone": tz, "beach_angle": beach_angle})
                    out = json.dumps(f_data).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Expires", "0")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(out)
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                    return
                except Exception as e:
                    try:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                    except Exception:
                        pass
                return

            # 4. API: Geocoding
            if path == "/api/geocode":
                q = params.get("q", [""])[0]
                lat_param = params.get("lat", [None])[0]
                lon_param = params.get("lon", [None])[0]
                ref_lat = float(lat_param) if lat_param not in (None, "") else None
                ref_lon = float(lon_param) if lon_param not in (None, "") else None
                lat, lon, res_name = geocode_place_name(q, ref_lat=ref_lat, ref_lon=ref_lon)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"lat": lat, "lon": lon, "name": res_name}).encode("utf-8"))
                return

            # 4b. API: Spot Verification & Live Forecast Testing
            if path == "/api/spots/verify":
                try:
                    q = params.get("q", [""])[0].strip()
                    lat_str = params.get("lat", [None])[0]
                    lon_str = params.get("lon", [None])[0]
                    angle_str = params.get("beach_angle", [None])[0]
                    ref_lat = params.get("ref_lat", [None])[0]
                    ref_lon = params.get("ref_lon", [None])[0]

                    target_lat = float(lat_str) if lat_str not in (None, "") else None
                    target_lon = float(lon_str) if lon_str not in (None, "") else None
                    resolved_name = q

                    # 1. Geocode if coordinates not explicitly passed
                    if target_lat is None or target_lon is None:
                        if not q:
                            self.send_response(400)
                            self.send_header("Content-Type", "application/json")
                            self._send_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps({"verified": False, "error": "Spot name or coordinates required"}).encode("utf-8"))
                            return

                        r_lat = float(ref_lat) if ref_lat not in (None, "") else None
                        r_lon = float(ref_lon) if ref_lon not in (None, "") else None
                        target_lat, target_lon, resolved_name = geocode_place_name(q, ref_lat=r_lat, ref_lon=r_lon)

                    if target_lat is None or target_lon is None:
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"verified": False, "error": f"Could not locate '{q}'. Try entering nearby coastal town or GPS coordinates."}).encode("utf-8"))
                        return

                    # Beach angle resolution
                    b_angle = None
                    if angle_str not in (None, ""):
                        try:
                            b_angle = float(angle_str)
                        except Exception:
                            pass
                    if b_angle is None:
                        b_angle = resolve_beach_angle(resolved_name or q)

                    # 2. Verify with resilient forecast engine (Open-Meteo + Met.no fallback)
                    f_data = fetch_live_forecast({
                        "lat": target_lat,
                        "lon": target_lon,
                        "name": resolved_name or q,
                        "beach_angle": b_angle
                    })

                    if not f_data or "current" not in f_data:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"verified": False, "error": "No meteorological wind coverage at these coordinates."}).encode("utf-8"))
                        return

                    cur = f_data.get("current", {})
                    cur_w = round_knots(cur.get("wind_kts", 0))
                    cur_g = round_knots(cur.get("gust_kts", cur_w))
                    cur_d = cur.get("degrees", 0)
                    cur_t = round(cur.get("temp", 25.0), 1)
                    cur_app = round(cur.get("apparent_temp", cur_t), 1)
                    tz = f_data.get("timezone", "auto")
                    active_model = f_data.get("model_info") or "ECMWF (9km) + Open-Meteo Verified"

                    slug_id = re.sub(r'[^a-z0-9]+', '_', (resolved_name or q).lower()).strip('_')[:25]
                    spot_obj = {
                        "id": f"custom_{slug_id}",
                        "name": resolved_name or q,
                        "short_name": (resolved_name or q).split(",")[0].strip(),
                        "country": (resolved_name or "").split(",")[-1].strip() if "," in (resolved_name or "") else "Custom",
                        "region": "Custom Verified",
                        "flag": "📍",
                        "lat": round(target_lat, 4),
                        "lon": round(target_lon, 4),
                        "timezone": tz,
                        "beach_angle": b_angle,
                        "model_label": active_model,
                        "is_custom": True,
                        "live_wind_kts": cur_w,
                        "live_gust_kts": cur_g,
                        "live_direction": cur.get("direction") or degrees_to_cardinal(cur_d),
                        "live_temp_c": cur_t,
                        "live_apparent_c": cur_app
                    }

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"verified": True, "spot": spot_obj}).encode("utf-8"))
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"verified": False, "error": str(e)}).encode("utf-8"))
                    return

            # API: Public Community Spots
            if path == "/api/spots/public":
                try:
                    spots = load_public_spots()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-cache")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "spots": spots}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # API: Spot Search (Curated + Public + Open-Meteo Geocoding)
            if path == "/api/spots/search":
                try:
                    q = params.get("q", [""])[0].strip()
                    cc = params.get("country", [""])[0].strip().upper()
                    email_p = params.get("email", [""])[0]
                    try:
                        import spot_telemetry
                        spot_telemetry.record_spot_search(q, country_code=cc, email=email_p)
                    except Exception:
                        pass
                    
                    results = []
                    seen_keys = set()

                    def get_country_flag(c_code):
                        if c_code and len(c_code) == 2:
                            return chr(ord(c_code[0].upper()) + 127397) + chr(ord(c_code[1].upper()) + 127397)
                        return "📍"

                    q_lower = q.lower()

                    # 1. Check curated spots
                    try:
                        from kite_spots import GLOBAL_KITE_SPOTS
                        for s in GLOBAL_KITE_SPOTS:
                            s_cc = (s.get("country_code") or "").upper()
                            s_name = s.get("name", "").lower()
                            s_country = s.get("country", "").lower()
                            s_aliases = [a.lower() for a in s.get("aliases", [])]
                            
                            if cc and s_cc and s_cc != cc and cc.lower() not in s_country:
                                continue
                            
                            if not q or q_lower in s_name or q_lower in s_country or any(q_lower in a for a in s_aliases):
                                k = f"{round(s['lat'], 3)}_{round(s['lon'], 3)}"
                                if k not in seen_keys:
                                    seen_keys.add(k)
                                    results.append({
                                        "id": s["id"],
                                        "name": s["name"],
                                        "short_name": s["short_name"],
                                        "country": s["country"],
                                        "region": s.get("region", ""),
                                        "flag": s.get("flag", "📍"),
                                        "lat": s["lat"],
                                        "lon": s["lon"],
                                        "timezone": s.get("timezone", "auto"),
                                        "beach_angle": s.get("beach_angle", 45),
                                        "model_label": s.get("model_label", "ECMWF (9km)"),
                                        "is_curated": True
                                    })
                    except Exception as e:
                        print("Error searching curated spots:", e)

                    # 2. Check public community spots
                    for s in load_public_spots():
                        s_name = s.get("name", "").lower()
                        s_country = s.get("country", "").lower()
                        s_cc = (s.get("country_code") or "").upper()
                        if cc and s_cc and s_cc != cc and cc.lower() not in s_country:
                            continue
                        if not q or q_lower in s_name or q_lower in s_country:
                            k = f"{round(s['lat'], 3)}_{round(s['lon'], 3)}"
                            if k not in seen_keys:
                                seen_keys.add(k)
                                results.append(s)

                    # 3. Query Open-Meteo Geocoding API if query is provided
                    if q:
                        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(q)}&count=10&language=en&format=json"
                        req = urllib.request.Request(geo_url, headers={"User-Agent": "HolyGust/1.0"})
                        with urllib.request.urlopen(req, context=SSL_CTX, timeout=6) as resp:
                            geo_data = json.loads(resp.read().decode("utf-8"))
                            for item in geo_data.get("results", []):
                                item_cc = (item.get("country_code") or "").upper()
                                if cc and item_cc != cc:
                                    continue
                                i_lat = item.get("latitude")
                                i_lon = item.get("longitude")
                                if i_lat is None or i_lon is None:
                                    continue
                                k = f"{round(i_lat, 3)}_{round(i_lon, 3)}"
                                if k in seen_keys:
                                    continue
                                seen_keys.add(k)

                                i_name = item.get("name")
                                admin = item.get("admin1") or item.get("admin2") or ""
                                c_name = item.get("country") or item_cc
                                display_name = f"{i_name}, {admin}, {c_name}" if admin else f"{i_name}, {c_name}"

                                p_model, m_label, b_ang = resolve_spot_model_and_angle(i_lat, i_lon, item_cc, display_name)
                                slug_id = re.sub(r'[^a-z0-9]+', '_', i_name.lower()).strip('_')[:20]

                                results.append({
                                    "id": f"spot_{item_cc.lower()}_{slug_id}_{item.get('id', 0)}",
                                    "name": display_name,
                                    "short_name": i_name,
                                    "country": c_name,
                                    "country_code": item_cc,
                                    "region": admin,
                                    "flag": get_country_flag(item_cc),
                                    "lat": round(i_lat, 4),
                                    "lon": round(i_lon, 4),
                                    "timezone": item.get("timezone", "auto"),
                                    "beach_angle": b_ang,
                                    "preferred_model": p_model,
                                    "model_label": m_label,
                                    "is_public": True
                                })

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "results": results[:20]}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e), "results": []}).encode("utf-8"))
                return

            # 5. API: Global Kite Spots & GPS Discovery
            if path == "/api/spots":
                try:
                    from kite_spots import GLOBAL_KITE_SPOTS, find_spots_near_gps, search_spots_catalog
                    lat_str = params.get("lat", [None])[0]
                    lon_str = params.get("lon", [None])[0]
                    q_str = params.get("q", [None])[0]

                    if lat_str and lon_str:
                        nearby = find_spots_near_gps(float(lat_str), float(lon_str), max_spots=15)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"spots": nearby, "type": "nearby"}).encode("utf-8"))
                        return

                    if q_str:
                        matches = search_spots_catalog(q_str, max_results=20)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"spots": matches, "type": "search"}).encode("utf-8"))
                        return

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"spots": GLOBAL_KITE_SPOTS, "type": "all"}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # 6. API: Kite Travel Destinations Directory
            if path == "/api/travel/spots":
                try:
                    import travel_climatology_db
                    spots = travel_climatology_db.get_all_travel_spots()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"spots": spots}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # 6b. API: Kite Travel Countries & Spots (2-tier hierarchy)
            if path == "/api/travel/countries":
                try:
                    import travel_climatology_db
                    data = travel_climatology_db.get_travel_countries_and_spots()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # 7. API: Kite Travel Spot Climatology
            if path == "/api/travel/spot-climate":
                try:
                    import travel_climatology_db
                    spot_id = params.get("spot_id", ["cabarete"])[0]
                    spot_data = travel_climatology_db.get_spot_climatology(spot_id)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "public, max-age=3600")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps(spot_data).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # 8. API: Kite Travel Explore by Month & Style
            if path == "/api/travel/explore":
                try:
                    import travel_climatology_db
                    from datetime import datetime
                    curr_month = datetime.utcnow().month
                    month_p = int(params.get("month", [curr_month])[0])
                    style_p = params.get("style", ["all"])[0]
                    ranked = travel_climatology_db.explore_spots_by_month_and_style(month_p, style_p)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "public, max-age=600")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "month": month_p,
                        "style": style_p,
                        "spots": ranked
                    }).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # 6. Static Files: PWA Web App
            if path in ["/", "/index.html"]:
                index_path = os.path.join(web_dir, "index.html")
                if os.path.exists(index_path):
                    with open(index_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache, must-revalidate")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            # 6. Commercial / Pro Parallel Edition
            if path in ["/pro", "/pro/", "/commercial", "/commercial/"]:
                comm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commercial", "index.html")
                if os.path.exists(comm_path):
                    with open(comm_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache, must-revalidate")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            if path == "/manifest.json":
                m_path = os.path.join(web_dir, "manifest.json")
                if os.path.exists(m_path):
                    with open(m_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/manifest+json; charset=utf-8")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            if path == "/sw.js":
                sw_path = os.path.join(web_dir, "sw.js")
                if os.path.exists(sw_path):
                    with open(sw_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            # Static icon & asset handler
            if path in ["/icon.png", "/icon-192.png", "/icon-512.png", "/apple-touch-icon.png", "/favicon.png", "/icon.svg"]:
                clean_name = path.lstrip("/")
                icon_file = os.path.join(web_dir, clean_name)
                if os.path.exists(icon_file):
                    mime = "image/svg+xml" if path.endswith(".svg") else "image/png"
                    with open(icon_file, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", mime)
                    self.send_header("Cache-Control", "public, max-age=86400")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            if path == "/kiteforecast_bot_qr.png":
                qr_path = os.path.join(base_dir, "kiteforecast_bot_qr.png")
                if os.path.exists(qr_path):
                    with open(qr_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            # Fallback
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found\n")

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            # Redirect old onrender.com domain POST requests preserving method/body (HTTP 308)
            host = (self.headers.get("Host") or "").lower().split(":")[0]
            if "onrender.com" in host and not parsed.path.startswith("/api/health"):
                target_url = f"https://holygust.com{self.path}"
                self.send_response(308)
                self.send_header("Location", target_url)
                self._send_cors_headers()
                self.end_headers()
                return
            if parsed.path == "/api/recommend":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    w = float(data.get("weight_kg", 75.0))
                    inv = data.get("active_inventory", [])
                    w_kts = float(data.get("wind_kts", 16.0))
                    g_kts = float(data.get("gust_kts", 20.0))
                    all_inv = data.get("all_inventory")
                    lvl = data.get("level", "intermediate")
                    brd = data.get("board", "twintip")
                    rec = recommend_from_available_quiver(w, inv, w_kts, g_kts, all_inventory=all_inv, level=lvl, board=brd)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"recommendation": rec}).encode("utf-8"))
                except Exception as e:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # AUTH: User Registration
            if parsed.path == "/api/auth/register":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    email = (data.get("email") or "").strip().lower()
                    password = data.get("password") or ""
                    name = (data.get("name") or "").strip()
                    gear = data.get("gear") or []
                    boards = data.get("boards") or []
                    weight_kg = float(data.get("weight_kg", 75.0))
                    level = data.get("level", "intermediate")
                    board = data.get("board", "Twintip")
                    spot = data.get("spot") or {}

                    if not email or "@" not in email:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Please enter a valid email address."}).encode("utf-8"))
                        return

                    if len(password) < 4:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Password must be at least 4 characters."}).encode("utf-8"))
                        return

                    db = load_users_db()
                    if email in db["users"]:
                        # If existing account has no password yet (e.g. pre-seeded or beta-invited):
                        if not db["users"][email].get("password_hash"):
                            user = db["users"][email]
                            p_hash, p_salt = hash_password(password)
                            user["password_hash"] = p_hash
                            user["password_salt"] = p_salt
                            if name: user["name"] = name
                            if gear: user["gear"] = gear
                            if boards: user["boards"] = boards
                            save_users_db(db)
                            # Notify Daniel on Telegram with true rider count!
                            try:
                                total_count = len(db["users"])
                                send_admin_telegram(
                                    f"🎉 HolyGust Rider Registered (Password Activated)!\n\n"
                                    f"👤 Rider: {user.get('name')}\n"
                                    f"🌍 Nationality: {user.get('nationality') or 'Not specified'}\n"
                                    f"📧 Email: {email}\n"
                                    f"⚖️ Setup: {user.get('weight_kg', 75)} kg · {(user.get('level') or 'intermediate').capitalize()}\n\n"
                                    f"📊 Total HolyGust Riders: {total_count}"
                                )
                            except Exception:
                                pass
                            safe_user = {k: v for k, v in user.items() if not k.startswith("password_")}
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self._send_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True, "user": safe_user}).encode("utf-8"))
                            return
                        else:
                            self.send_response(400)
                            self.send_header("Content-Type", "application/json")
                            self._send_cors_headers()
                            self.end_headers()
                            self.wfile.write(json.dumps({"error": "An account with this email already exists. Try signing in!"}).encode("utf-8"))
                            return

                    p_hash, p_salt = hash_password(password)
                    from datetime import datetime
                    now_str = datetime.utcnow().isoformat() + "Z"
                    nationality = (data.get("nationality") or "").strip()
                    new_user = {
                        "email": email,
                        "name": name or email.split("@")[0],
                        "nationality": nationality,
                        "password_hash": p_hash,
                        "password_salt": p_salt,
                        "registered_at": now_str,
                        "last_login": now_str,
                        "gear": gear,
                        "boards": boards,
                        "weight_kg": weight_kg,
                        "level": level,
                        "board": board,
                        "spot": spot
                    }
                    db["users"][email] = new_user
                    save_users_db(db)

                    # Notify Daniel on Telegram with full rider & gear details!
                    total_count = len(db["users"])
                    gear_count = len(gear)
                    current_yr = 2026
                    gear_lines = []
                    for k in gear:
                        cat = k.get("category", "kite")
                        k_type = k.get("kite_type", "tube")
                        if cat == "wing":
                            icon = "🪽 [Wing]"
                        elif k_type == "soft":
                            icon = "🪁 [Soft Kite / Mat]"
                        else:
                            icon = "🪁 [Tube Kite]"
                        b = k.get("brand", "Kite")
                        m = k.get("model", "")
                        sz = k.get("size", "")
                        yr = int(k.get("year", current_yr))
                        age = current_yr - yr
                        age_str = f" [{age} yrs old]" if age > 0 else " [New]"
                        gear_lines.append(f"  • {icon} {b} {m} {sz}m ({yr}){age_str}")
                    
                    gear_summary = "\n".join(gear_lines) if gear_lines else "  (No gear registered yet)"

                    board_lines = []
                    for b in boards:
                        b_type = b.get("type", "Twintip")
                        b_brand = b.get("brand", "")
                        b_model = b.get("model", "")
                        b_sz = b.get("size", "")
                        b_vol = f" {b.get('volume')}L" if b.get("volume") else ""
                        b_mast = f" ({b.get('mast')}cm mast)" if b.get("mast") else ""
                        b_carb = " [⚡ Carbon/SLS]" if b.get("carbon") else ""
                        unit = "cm" if b_type == "Twintip" else ("cm²" if b_type in ["Hydrofoil", "Wingfoil"] else "")
                        board_lines.append(f"  • [{b_type}] {b_brand} {b_model}{b_vol} {b_sz}{unit}{b_mast}{b_carb}")
                    boards_summary = "\n".join(board_lines) if board_lines else "  (No boards registered yet)"

                    notify_text = (
                        f"🎉 New HolyGust Rider Registered!\n\n"
                        f"👤 Rider: {new_user['name']}\n"
                        f"🌍 Nationality: {nationality or 'Not specified'}\n"
                        f"📧 Email: {email}\n"
                        f"⚖️ Setup: {weight_kg} kg · {level.capitalize()}\n\n"
                        f"🎒 Stored Cloud Gear ({gear_count} items):\n"
                        f"{gear_summary}\n\n"
                        f"🏄 Stored Cloud Boards ({len(boards)} boards):\n"
                        f"{boards_summary}\n\n"
                        f"📊 Total HolyGust Riders: {total_count}"
                    )
                    send_admin_telegram(notify_text)

                    safe_user = {k: v for k, v in new_user.items() if not k.startswith("password_")}
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "user": safe_user}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # AUTH: User Login
            if parsed.path == "/api/auth/login":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    email = (data.get("email") or "").strip().lower()
                    password = data.get("password") or ""

                    db = load_users_db()
                    user = db["users"].get(email)
                    if not user:
                        self.send_response(401)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "No account found with this email."}).encode("utf-8"))
                        return

                    # Auto-set password if account was created without one (e.g. pre-seeded)
                    if not user.get("password_hash"):
                        p_hash, p_salt = hash_password(password)
                        user["password_hash"] = p_hash
                        user["password_salt"] = p_salt
                        save_users_db(db)
                        calc_hash = p_hash
                    else:
                        calc_hash, _ = hash_password(password, user.get("password_salt", ""))

                    if calc_hash != user.get("password_hash"):
                        self.send_response(401)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Incorrect password. Please try again or tap 'Forgot?'."}).encode("utf-8"))
                        return

                    from datetime import datetime
                    user["last_login"] = datetime.utcnow().isoformat() + "Z"
                    save_users_db(db)

                    safe_user = {k: v for k, v in user.items() if not k.startswith("password_")}
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "user": safe_user}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # SPOTS: Add New Public Community Spot
            if parsed.path == "/api/spots/add":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    spot_data = json.loads(body)
                    
                    if not spot_data.get("name") or spot_data.get("lat") is None or spot_data.get("lon") is None:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Missing required spot name or coordinates."}).encode("utf-8"))
                        return

                    spots = load_public_spots()
                    
                    def haversine_km(lat1, lon1, lat2, lon2):
                        R = 6371.0
                        dlat = math.radians(lat2 - lat1)
                        dlon = math.radians(lon2 - lon1)
                        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                        return 2 * R * math.asin(math.sqrt(a))

                    s_lat = float(spot_data["lat"])
                    s_lon = float(spot_data["lon"])
                    
                    existing_idx = None
                    for idx, s in enumerate(spots):
                        if s.get("id") == spot_data.get("id") or haversine_km(s_lat, s_lon, float(s["lat"]), float(s["lon"])) < 2.0:
                            existing_idx = idx
                            break

                    spot_data["is_public"] = True
                    from datetime import datetime
                    spot_data["created_at"] = datetime.utcnow().isoformat() + "Z"

                    if existing_idx is not None:
                        spots[existing_idx] = spot_data
                    else:
                        spots.insert(0, spot_data)

                    save_public_spots(spots)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "spot": spot_data}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # AUTH: User Cloud Data Sync (Auto-Upsert Profile)
            if parsed.path == "/api/auth/sync":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    email = (data.get("email") or "").strip().lower()

                    if not email:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Email is required for sync."}).encode("utf-8"))
                        return

                    db = load_users_db()
                    from datetime import datetime
                    if email not in db["users"]:
                        db["users"][email] = {
                            "email": email,
                            "name": data.get("name") or email.split("@")[0].title(),
                            "created_at": datetime.utcnow().isoformat() + "Z",
                            "gear": [],
                            "boards": [],
                            "favorite_spots": []
                        }

                    user = db["users"][email]
                    if "name" in data and data["name"]:
                        user["name"] = data["name"]
                    if "nationality" in data and data["nationality"]:
                        user["nationality"] = data["nationality"].strip()
                    if "gear" in data and isinstance(data["gear"], list):
                        if len(data["gear"]) > 0 or not user.get("gear"):
                            user["gear"] = data["gear"]
                    if "boards" in data and isinstance(data["boards"], list):
                        if len(data["boards"]) > 0 or not user.get("boards"):
                            user["boards"] = data["boards"]
                    if "weight_kg" in data and data["weight_kg"] is not None:
                        try:
                            user["weight_kg"] = float(data["weight_kg"])
                        except (ValueError, TypeError):
                            pass
                    if "level" in data and data["level"]:
                        user["level"] = data["level"]
                    if "board" in data and data["board"]:
                        user["board"] = data["board"]
                    if "spot" in data and isinstance(data["spot"], dict):
                        user["spot"] = data["spot"]
                    if "favorite_spots" in data and isinstance(data["favorite_spots"], list):
                        if len(data["favorite_spots"]) > 0 or not user.get("favorite_spots"):
                            user["favorite_spots"] = data["favorite_spots"]

                    approved_set = load_approved_beta_emails()
                    if email in approved_set or user.get("is_beta_rider"):
                        user["is_beta_rider"] = True
                        user["beta_status"] = "approved"

                    user["last_sync"] = datetime.utcnow().isoformat() + "Z"
                    save_users_db(db)

                    safe_user = {k: v for k, v in user.items() if not k.startswith("password_")}
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "synced": True, "user": safe_user}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # AUTH: Forgot Password Request
            if parsed.path == "/api/auth/forgot-password":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    email = (data.get("email") or "").strip().lower()

                    if not email:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Please enter a valid email address."}).encode("utf-8"))
                        return

                    db = load_users_db()
                    user = db.get("users", {}).get(email)
                    if not user:
                        self.send_response(404)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "No account found with this email. Please check spelling or create an account."}).encode("utf-8"))
                        return

                    import secrets, time
                    reset_token = secrets.token_urlsafe(32)
                    reset_code = f"{secrets.randbelow(900000) + 100000}"
                    expires_at = time.time() + 3600  # 1 hour expiration

                    user["reset_token"] = reset_token
                    user["reset_code"] = reset_code
                    user["reset_expires"] = expires_at
                    save_users_db(db)

                    user_name = user.get("name") or email.split("@")[0]
                    reset_link = f"https://holygust.com/?reset_token={reset_token}"

                    html_email = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin: 0; padding: 24px 0; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <div style="max-width: 520px; margin: 0 auto; background: #0f172a; border-radius: 20px; overflow: hidden; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
    <div style="padding: 24px 20px; text-align: center; background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);">
      <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">HolyGust</h1>
      <p style="margin: 4px 0 0; color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 500;">Smart Wind &amp; Gear Assistant</p>
    </div>
    <div style="padding: 30px 24px; color: #f8fafc;">
      <h2 style="margin: 0 0 12px; font-size: 19px; color: #ffffff; font-weight: 700;">Password Reset Request</h2>
      <p style="margin: 0 0 20px; font-size: 14px; line-height: 1.6; color: #94a3b8;">
        Hi <strong>{user_name}</strong>,<br>
        We received a request to reset your HolyGust password. Tap the button below to set a new password:
      </p>
      <div style="text-align: center; margin: 28px 0;">
        <a href="{reset_link}" style="display: inline-block; background: #0284c7; color: #ffffff; font-weight: 700; font-size: 14px; padding: 13px 32px; border-radius: 12px; text-decoration: none; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.45);">
          Set New Password
        </a>
      </div>
      <p style="margin: 20px 0 0; font-size: 13px; line-height: 1.5; color: #64748b; text-align: center;">
        Or enter this 6-digit code in the app:<br>
        <strong style="color: #38bdf8; font-size: 20px; letter-spacing: 4px; display: inline-block; margin-top: 6px;">{reset_code}</strong>
      </p>
      <div style="margin: 28px 0 0; padding-top: 18px; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b; text-align: center; line-height: 1.5;">
        This link is valid for 1 hour. If you didn't request a password reset, you can safely ignore this email.
      </div>
    </div>
  </div>
</body>
</html>"""

                    email_sent = send_email_via_resend(
                        to_email=email,
                        subject="Reset Your HolyGust Password",
                        html_body=html_email
                    )

                    # Admin alert
                    tele_msg = f"🔑 Password reset requested for: {email} (Code: {reset_code}, Resend Sent: {email_sent})"
                    send_admin_telegram(tele_msg)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "email_sent": email_sent,
                        "message": "Password reset instructions sent to your email!"
                    }).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # AUTH: Reset Password Submission
            if parsed.path == "/api/auth/reset-password":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    token = (data.get("token") or "").strip()
                    code = (data.get("code") or "").strip()
                    new_password = data.get("new_password") or ""
                    email = (data.get("email") or "").strip().lower()

                    if not new_password or len(new_password) < 4:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Password must be at least 4 characters long."}).encode("utf-8"))
                        return

                    if not token and not code:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Missing reset token or code."}).encode("utf-8"))
                        return

                    db = load_users_db()
                    matched_user = None
                    matched_email = None

                    import time
                    now = time.time()

                    for u_email, u_data in db.get("users", {}).items():
                        token_match = token and u_data.get("reset_token") == token
                        code_match = code and (not email or u_email == email) and u_data.get("reset_code") == code
                        if token_match or code_match:
                            if u_data.get("reset_expires", 0) < now:
                                self.send_response(400)
                                self.send_header("Content-Type", "application/json")
                                self._send_cors_headers()
                                self.end_headers()
                                self.wfile.write(json.dumps({"error": "This reset link or code has expired. Please request a new one."}).encode("utf-8"))
                                return
                            matched_user = u_data
                            matched_email = u_email
                            break

                    if not matched_user:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid or expired reset token or code."}).encode("utf-8"))
                        return

                    # Update password
                    p_hash, p_salt = hash_password(new_password)
                    matched_user["password_hash"] = p_hash
                    matched_user["password_salt"] = p_salt
                    matched_user.pop("reset_token", None)
                    matched_user.pop("reset_code", None)
                    matched_user.pop("reset_expires", None)
                    from datetime import datetime
                    matched_user["last_login"] = datetime.utcnow().isoformat() + "Z"
                    save_users_db(db)

                    safe_user = {k: v for k, v in matched_user.items() if not k.startswith("password_")}
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": "Password reset successfully! You are now signed in.",
                        "user": safe_user
                    }).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # BETA: Apply for Beta Rider Access
            if parsed.path == "/api/beta/apply":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    email = (data.get("email") or "").strip().lower()
                    name = data.get("name") or email.split("@")[0].title()
                    spot = data.get("spot") or "Cumbuco"
                    weight_kg = data.get("weight_kg", 74.0)
                    level = data.get("level", "intermediate")
                    board = data.get("board", "Twintip")

                    if not email or "@" not in email:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "A valid email is required to apply."}).encode("utf-8"))
                        return

                    db = load_users_db()
                    from datetime import datetime, timezone
                    if email not in db.get("users", {}):
                        db.setdefault("users", {})[email] = {
                            "email": email,
                            "name": name,
                            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                            "gear": [],
                            "boards": [],
                            "weight_kg": float(weight_kg),
                            "level": level,
                            "board": board,
                            "favorite_spots": []
                        }
                    user = db["users"][email]
                    user["beta_status"] = "pending"
                    user["beta_applied_at"] = datetime.now(timezone.utc).isoformat() + "Z"
                    save_users_db(db)

                    nat = (data.get("nationality") or user.get("nationality") or "").strip()
                    if nat:
                        user["nationality"] = nat
                        save_users_db(db)

                    # Send Telegram Alert with Inline Buttons for 1-Tap Approval
                    tele_text = (
                        f"⚡ NEW BETA RIDER APPLICATION!\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 Rider: {name}\n"
                        f"🌍 Nationality: {nat or 'Not specified'}\n"
                        f"📧 Email: {email}\n"
                        f"⚖️ Weight: {weight_kg} kg | Level: {level}\n"
                        f"🏄 Board: {board}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Tap below to approve or decline instantly:"
                    )
                    reply_markup = {
                        "inline_keyboard": [
                            [
                                {"text": "✅ Approve ⚡ Beta Rider", "callback_data": f"approve_beta:{email}"},
                                {"text": "❌ Decline", "callback_data": f"decline_beta:{email}"}
                            ]
                        ]
                    }
                    send_admin_telegram(tele_text, reply_markup=reply_markup)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": "The HolyGust team has received your request. You will get an email once approved!"
                    }).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # BETA: Leave Beta Rider Program
            if parsed.path == "/api/beta/leave":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body) if body else {}
                    email = (data.get("email") or "").strip().lower()

                    if not email or "@" not in email:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "A valid email is required."}).encode("utf-8"))
                        return

                    success, r_name = leave_beta_program(email)
                    db = load_users_db()
                    updated_user = db.get("users", {}).get(email, {})

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": "You have left the Beta Rider crew and returned to standard production.",
                        "user": updated_user
                    }).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # KITE TRAVEL: Personalized Quiver Matching & Demand Telemetry
            if parsed.path == "/api/travel/recommend":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body) if body else {}

                    spot_id = (data.get("spot_id") or "cabarete").strip().lower()
                    month = int(data.get("month") or 7)
                    if month < 1 or month > 12:
                        month = 7
                    weight_kg = float(data.get("weight_kg") or 75.0)
                    discipline = (data.get("discipline") or "Twintip").strip()
                    gear = data.get("gear") or []
                    email = (data.get("email") or "").strip().lower()
                    name = (data.get("name") or "").strip()
                    nationality = (data.get("nationality") or "").strip()
                    style = (data.get("style") or "All").strip()

                    import travel_climatology_db
                    rec = travel_climatology_db.calculate_quiver_trip_recommendation(
                        spot_id=spot_id,
                        month=month,
                        rider_weight=weight_kg,
                        discipline=discipline,
                        gear_inventory=gear
                    )

                    # Record commercial demand telemetry for partnerships & monetization
                    try:
                        import spot_telemetry
                        spot_name = rec.get("spot", {}).get("name", spot_id)
                        country = rec.get("spot", {}).get("country", "")
                        quiver_sizes = [g.get("size") for g in gear if isinstance(g, dict) and g.get("size")]
                        rec_pack = [p.get("size") for p in rec.get("quiver_advice", {}).get("pack", [])]
                        gear_gaps = rec.get("quiver_advice", {}).get("gaps", [])

                        spot_telemetry.record_travel_inquiry(
                            spot_id=spot_id,
                            spot_name=spot_name,
                            country=country,
                            month=month,
                            style=style,
                            weight_kg=weight_kg,
                            discipline=discipline,
                            quiver_sizes=quiver_sizes,
                            recommended_pack=rec_pack,
                            gear_gaps=gear_gaps,
                            email=email,
                            rider_name=name,
                            nationality=nationality
                        )
                    except Exception as te:
                        print(f"record_travel_inquiry telemetry error: {te}")

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Cache-Control", "no-cache")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "data": rec}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # API: Request & Auto-Process New Travel Destination
            if parsed.path == "/api/travel/request-spot":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body) if body else {}

                    query = (data.get("query") or "").strip()
                    user_name = (data.get("name") or "").strip()
                    user_email = (data.get("email") or "").strip().lower()

                    import travel_climatology_db
                    new_spot = travel_climatology_db.process_new_destination(
                        query=query,
                        user_name=user_name,
                        user_email=user_email
                    )

                    # Telemetry logging
                    try:
                        import spot_telemetry
                        spot_telemetry.record_spot_search(
                            spot_id=new_spot.get("id"),
                            spot_name=new_spot.get("name"),
                            country=new_spot.get("country"),
                            source="travel_advisor_request"
                        )
                    except Exception as te:
                        print(f"[telemetry] custom spot error: {te}")

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "spot": new_spot,
                        "message": f"'{new_spot['name']}' has been analyzed and added to the destination list!"
                    }).encode("utf-8"))
                except Exception as e:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # FEEDBACK & SUGGESTIONS
            if parsed.path == "/api/feedback":
                try:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len).decode("utf-8")
                    data = json.loads(body)
                    msg = (data.get("message") or data.get("feedback") or "").strip()
                    name = (data.get("name") or "Anonymous").strip()
                    email = (data.get("email") or "Not provided").strip()
                    spot = (data.get("spot") or "General").strip()

                    if not msg:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Please write a suggestion or message."}).encode("utf-8"))
                        return

                    from datetime import datetime
                    now_str = datetime.utcnow().isoformat() + "Z"
                    entry = {
                        "name": name,
                        "email": email,
                        "spot": spot,
                        "message": msg,
                        "created_at": now_str
                    }
                    db = load_users_db()
                    if "feedback" not in db:
                        db["feedback"] = []
                    db["feedback"].append(entry)
                    save_users_db(db)

                    # Send Instant Alert to Daniel on Telegram!
                    tele_text = (
                        f"💡 New KiteApp Feedback / Suggestion!\n\n"
                        f"👤 From: {name} ({email})\n"
                        f"📍 Spot: {spot}\n\n"
                        f"💬 Message:\n\"{msg}\"\n\n"
                        f"📊 Total Feedback Received: {len(db['feedback'])}"
                    )
                    send_admin_telegram(tele_text)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "message": "Thank you! The HolyGust team has received your feedback."}).encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            self.send_response(404)
            self.end_headers()

        def log_message(self, *args):
            pass

    try:
        server = HTTPServer(("0.0.0.0", port), AppServerHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"🌐 Cloud App & Health Server listening on 0.0.0.0:{port} (PWA + API Enabled)...")
    except Exception as e:
        print(f"Cloud health server note: {e}")


def run_poll_listener():
    config = load_config()
    token = config["telegram_token"]
    
    # Start cloud health server for Render / Koyeb / Hugging Face free hosting
    cloud_port = int(os.getenv("PORT", "8080"))
    start_embedded_http_server(cloud_port)

    print(f"🤖 Kitesurf Bot listener started for @KiteForecast_bot (Multi-User Cloud Mode)...")
    print(f"Registered users: {len(config.get('users', {}))}")
    
    last_update_id = 0
    url = f"https://api.telegram.org/bot{token}/getUpdates"

    while True:
        try:
            req_url = f"{url}?offset={last_update_id + 1}&timeout=30"
            req = urllib.request.Request(req_url)
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            for update in data.get("result", []):
                last_update_id = update["update_id"]
                
                # Check for Telegram inline button click (Callback Query)
                cb = update.get("callback_query")
                if cb:
                    handle_telegram_callback(cb, token, config)
                    continue

                msg = update.get("message") or update.get("edited_message")
                if not msg:
                    continue
                
                chat_id = str(msg.get("chat", {}).get("id"))
                text = msg.get("text", "")
                
                reply = handle_telegram_command(text, msg, config)
                if reply:
                    send_telegram(reply, token, chat_id)
                    print(f"Replied to {msg.get('from', {}).get('first_name', 'user')}: {text or 'Location'}")

        except Exception as e:
            err_msg = str(e)
            if "409" in err_msg or "Conflict" in err_msg:
                print("Polling: HTTP 409 Conflict (waiting 5s for previous instance shutdown)...")
                time.sleep(5)
            else:
                print(f"Polling loop error: {e}")
                time.sleep(3)


def send_morning_briefing_to_all():
    """Iterates through all registered friends and sends their custom morning briefing."""
    config = load_config()
    token = config["telegram_token"]
    users = config.get("users", {})
    print(f"Dispatched morning briefings to {len(users)} registered users...")

    for uid, profile in users.items():
        if profile.get("morning_briefing", False):
            try:
                forecast = fetch_live_forecast(profile["spot"])
                briefing = format_briefing(forecast, profile)
                send_telegram(briefing, token, str(profile["user_id"]))
                print(f"Sent morning briefing to {profile.get('rider_name')} ({uid})")
            except Exception as e:
                print(f"Error sending briefing to {uid}: {e}")


def main():
    config = load_config()
    if len(sys.argv) > 1 and sys.argv[1] in ["--poll", "--listen", "-l"]:
        run_poll_listener()
        return
    elif len(sys.argv) > 1 and sys.argv[1] in ["--web", "-w", "--server"]:
        cloud_port = int(os.getenv("PORT", "8080"))
        start_embedded_http_server(cloud_port)
        print(f"HolyGust web server running on http://localhost:{cloud_port}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        return
    elif len(sys.argv) > 1 and sys.argv[1] in ["--briefing-all", "--all"]:
        send_morning_briefing_to_all()
        return

    # Single-user or default run: do NOT send long morning briefings unless explicitly requested
    print("HolyGust App Server started. Automatic morning briefing Telegram spam is disabled by user preference.")
    if len(sys.argv) > 1 and sys.argv[1] in ["--briefing", "-b"]:
        admin_id = str(config.get("admin_id", "7424865438"))
        profile = config.get("users", {}).get(admin_id, list(config.get("users", {}).values())[0])
        forecast = fetch_live_forecast(profile["spot"])
        briefing = format_briefing(forecast, profile)
        send_telegram(briefing, config["telegram_token"], str(profile["user_id"]))
        print(f"Morning briefing delivered to {profile['rider_name']}!")


if __name__ == "__main__":
    main()
