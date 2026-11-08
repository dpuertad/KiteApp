"""
spot_alerts.py - HolyGust Beta Spot Wind Alarms & Quiver Matching Engine
Handles:
  1. VAPID Key generation & Web Push delivery via pywebpush to Service Worker
  2. Transactional Email Spot Alarms via Resend
  3. Admin Telegram notification to Daniel (no telegram for normal riders)
  4. Quiver-aware 12-48h forecast analysis (weekend windows & forecast improvement triggers)
  5. Anti-spam deduplication & alert history
"""

import os
import json
import time
import base64
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any

VAPID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vapid_keys.json")
VAPID_PEM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vapid_private.pem")
ALERTS_HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spot_alerts_history.json")
SNAPSHOTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spot_wind_snapshots.json")

# ==============================================================================
# 1. VAPID & WEB PUSH MANAGEMENT
# ==============================================================================

def get_or_create_vapid_keys() -> Dict[str, str]:
    """Retrieves or generates permanent VAPID ECDSA keys for Web Push."""
    if os.path.exists(VAPID_FILE):
        try:
            with open(VAPID_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("public_key") and data.get("private_key_pem"):
                    if not os.path.exists(VAPID_PEM_FILE):
                        with open(VAPID_PEM_FILE, "w", encoding="utf-8") as pf:
                            pf.write(data["private_key_pem"])
                    data["private_pem_file"] = VAPID_PEM_FILE
                    return data
                elif data.get("public_key") and os.path.exists(VAPID_PEM_FILE):
                    try:
                        with open(VAPID_PEM_FILE, "r", encoding="utf-8") as pf:
                            data["private_key_pem"] = pf.read()
                        with open(VAPID_FILE, "w", encoding="utf-8") as wf:
                            json.dump(data, wf, indent=2)
                    except Exception:
                        pass
                    return data
        except Exception:
            pass

    try:
        from py_vapid import Vapid
        v = Vapid()
        v.generate_keys()
        
        # Save private PEM file for pywebpush
        v.save_key(VAPID_PEM_FILE)

        from cryptography.hazmat.primitives import serialization
        raw_pub = v.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        b64_pub = base64.urlsafe_b64encode(raw_pub).rstrip(b"=").decode("ascii")

        pem_text = ""
        if os.path.exists(VAPID_PEM_FILE):
            with open(VAPID_PEM_FILE, "r", encoding="utf-8") as pf:
                pem_text = pf.read()

        data = {
            "public_key": b64_pub,
            "private_key_pem": pem_text,
            "private_pem_file": VAPID_PEM_FILE
        }
        with open(VAPID_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data
    except Exception as e:
        print(f"[SpotAlerts] Error generating VAPID keys: {e}")
        return {"public_key": "", "private_pem_file": ""}

def get_vapid_public_key() -> str:
    keys = get_or_create_vapid_keys()
    return keys.get("public_key", "")

def send_web_push(subscription_info: dict, payload: dict) -> Tuple[bool, str]:
    """Sends native Web Push notification to PWA Service Worker via pywebpush."""
    try:
        from pywebpush import webpush, WebPushException
        keys = get_or_create_vapid_keys()
        pem_file = keys.get("private_pem_file") or VAPID_PEM_FILE
        if not os.path.exists(pem_file):
            return False, "VAPID private key file missing"

        data_str = json.dumps(payload)
        webpush(
            subscription_info=subscription_info,
            data=data_str,
            vapid_private_key=pem_file,
            vapid_claims={"sub": "mailto:alerts@holygust.com"}
        )
        return True, "delivered"
    except Exception as e:
        err_msg = str(e)
        if "410" in err_msg or "404" in err_msg or "expired" in err_msg.lower():
            return False, "expired"
        print(f"[SpotAlerts] WebPush failed: {e}")
        return False, err_msg

# ==============================================================================
# 2. EMAIL SPOT ALARM VIA RESEND
# ==============================================================================

def send_spot_alert_email(to_email: str, rider_name: str, alert: dict) -> bool:
    """Sends a branded, high-conversion HolyGust Spot Alarm email via Resend."""
    try:
        from kitesurf_bot import send_email_via_resend
        
        spot_name = alert.get("spot_name", "Your Spot")
        wind_kts = alert.get("wind_kts", 16)
        gust_kts = alert.get("gust_kts", 20)
        direction = alert.get("direction", "E")
        shoreline = alert.get("shoreline", "Side-Onshore")
        timing = alert.get("timing_display", "Tomorrow Afternoon")
        kite_desc = alert.get("kite_desc", "Your Favorite Kite")
        board_desc = alert.get("board_desc", "Twintip")
        reason = alert.get("reason", "Forecast in prime sweet spot")
        spot_url = f"https://holygust.com/?spot={spot_name.replace(' ', '%20')}"

        subject = f"🚨 Wind Alarm: {wind_kts} kts at {spot_name} ({timing})"

        html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HolyGust Wind Alarm</title>
</head>
<body style="margin: 0; padding: 24px 12px; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <div style="max-width: 540px; margin: 0 auto; background: #0f172a; border-radius: 24px; overflow: hidden; border: 1px solid #1e293b; box-shadow: 0 20px 35px rgba(0,0,0,0.5);">
    
    <!-- Top Accent Header -->
    <div style="padding: 24px 24px 20px; background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%); text-align: center;">
      <div style="display: inline-block; background: rgba(15, 23, 42, 0.4); padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; color: #fde68a; margin-bottom: 8px;">
        ⚡ HolyGust Beta · Spot Wind Alarm
      </div>
      <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 900; letter-spacing: -0.5px;">
        {spot_name}
      </h1>
      <p style="margin: 6px 0 0; color: #e0f2fe; font-size: 13px; font-weight: 600;">
        {timing}
      </p>
    </div>

    <!-- Alert Body -->
    <div style="padding: 28px 24px;">
      
      <!-- Wind Hero Card -->
      <div style="background: #1e293b; border-radius: 20px; padding: 20px; text-align: center; border: 1px solid #334155; margin-bottom: 24px;">
        <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #38bdf8; letter-spacing: 0.5px; margin-bottom: 4px;">
          Detected Live Wind Window
        </div>
        <div style="font-size: 42px; font-weight: 900; line-height: 1; color: #38bdf8; font-family: monospace;">
          {wind_kts} <span style="font-size: 18px; font-weight: 700; color: #94a3b8;">KTS</span>
        </div>
        <div style="font-size: 13px; color: #94a3b8; margin-top: 6px;">
          Gusts: <strong>{gust_kts} kts</strong> · Direction: <strong>{direction}</strong> ({shoreline})
        </div>
      </div>

      <!-- Quiver Recommendation -->
      <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 16px; padding: 18px; margin-bottom: 24px;">
        <div style="font-size: 12px; font-weight: 800; color: #f59e0b; text-transform: uppercase; margin-bottom: 6px; display: flex; align-items: center;">
          🪁 Quiver Match Ready
        </div>
        <div style="font-size: 16px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">
          {kite_desc}
        </div>
        <div style="font-size: 13px; color: #cbd5e1;">
          Board: <strong>{board_desc}</strong> · Powered sweet spot session (zero slogging).
        </div>
      </div>

      <!-- Trigger Reason -->
      <div style="background: #1e293b/60; border-radius: 14px; padding: 14px 16px; margin-bottom: 28px; font-size: 12px; color: #94a3b8; line-height: 1.5; border-left: 3px solid #0284c7;">
        <strong>Why you got this alert:</strong> {reason} (12–48h window).
      </div>

      <!-- CTA Button -->
      <div style="text-align: center; margin-bottom: 24px;">
        <a href="{spot_url}" style="display: inline-block; background: #0284c7; color: #ffffff; font-weight: 800; font-size: 14px; padding: 14px 32px; border-radius: 14px; text-decoration: none; box-shadow: 0 4px 16px rgba(2, 132, 199, 0.4);">
          Check Live Conditions & Hourly Slots →
        </a>
      </div>

      <!-- Footer -->
      <p style="margin: 0; font-size: 11px; text-align: center; color: #64748b; line-height: 1.5;">
        You received this because you enabled Beta Spot Alarms for <strong>{spot_name}</strong> on HolyGust.<br>
        To manage or snooze alerts, visit your profile in the web app.
      </p>

    </div>
  </div>
</body>
</html>"""
        return send_email_via_resend(to_email, subject, html_body)
    except Exception as e:
        print(f"[SpotAlerts] send_spot_alert_email error: {e}")
        return False

# ==============================================================================
# 3. ADMIN TELEGRAM NOTIFICATION (Daniel only)
# ==============================================================================

def notify_admin_spot_alert(rider_name: str, rider_email: str, spot_name: str, alert: dict, channels: List[str]) -> bool:
    """Notifies Daniel via Telegram whenever a Spot Alarm is dispatched to a user."""
    try:
        from kitesurf_bot import send_admin_telegram
        tele_text = (
            f"🚨 BETA SPOT ALARM DISPATCHED!\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Rider: {rider_name} ({rider_email})\n"
            f"📍 Spot: {spot_name}\n"
            f"💨 Forecast: {alert.get('wind_kts')} kts (Gusts {alert.get('gust_kts')} kts)\n"
            f"🪁 Quiver Match: {alert.get('kite_desc')}\n"
            f"🏄 Board: {alert.get('board_desc')}\n"
            f"⏰ Window: {alert.get('timing_display')}\n"
            f"💡 Trigger: {alert.get('reason')}\n"
            f"📡 Sent via: {', '.join(channels)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"HolyGust Wind Alarm Engine"
        )
        return send_admin_telegram(tele_text)
    except Exception as e:
        print(f"[SpotAlerts] notify_admin_spot_alert error: {e}")
        return False

# ==============================================================================
# 4. SMART FORECAST & QUIVER EVALUATION
# ==============================================================================

def load_alert_history() -> dict:
    if os.path.exists(ALERTS_HISTORY_FILE):
        try:
            with open(ALERTS_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_alert_history(hist: dict):
    try:
        with open(ALERTS_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
    except Exception as e:
        print(f"[SpotAlerts] Error saving alert history: {e}")

def load_snapshots() -> dict:
    if os.path.exists(SNAPSHOTS_FILE):
        try:
            with open(SNAPSHOTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_snapshots(snaps: dict):
    try:
        with open(SNAPSHOTS_FILE, "w", encoding="utf-8") as f:
            json.dump(snaps, f, indent=2)
    except Exception as e:
        print(f"[SpotAlerts] Error saving snapshots: {e}")

def evaluate_rider_spot_alert(rider: dict, spot_name: str, forecast_data: dict, pref: dict = None) -> Optional[dict]:
    """
    Evaluates 12-48h forecast window for this rider:
      Trigger 1: Weekend window (Saturday or Sunday) with >= 2 consecutive hours of sweet-spot wind.
      Trigger 2: Forecast improved by >= +3 kts into the sweet spot compared to previous snapshot.
    """
    try:
        import kitesurf_bot
        weight_kg = float(rider.get("weight_kg", 75.0))
        gear = rider.get("gear", [])
        boards = rider.get("boards", [])
        board_type = rider.get("board", "Twintip")
        level = rider.get("level", "intermediate")
        weekend_only = (pref or {}).get("weekend_only", False)

        if not gear:
            return None

        weekly = forecast_data.get("weekly_forecast", [])
        if not weekly or len(weekly) < 2:
            return None

        # Look at Day 1 (tomorrow, ~24h) and Day 2 (day after tomorrow, ~48h)
        target_days = [1, 2]
        now_dt = datetime.now(timezone.utc)

        # Snapshots for forecast improvement detection
        snaps = load_snapshots()
        spot_key = spot_name.strip().lower()
        prev_spot_snap = snaps.get(spot_key, {})

        for day_idx in target_days:
            if day_idx >= len(weekly):
                continue
            day_data = weekly[day_idx]
            date_str = day_data.get("date", "")
            date_display = day_data.get("date_display", "")
            hourly = day_data.get("hourly", [])

            # Determine if this day is a weekend (Saturday or Sunday)
            is_weekend = False
            try:
                dt = datetime.fromisoformat(date_str)
                is_weekend = dt.weekday() in (5, 6) # Saturday=5, Sunday=6
            except Exception:
                pass

            if weekend_only and not is_weekend:
                continue

            # Evaluate daylight hours (08:00 - 18:00)
            candidate_hours = []
            for h in hourly:
                h_str = h.get("hour", "00:00")
                try:
                    hr_int = int(h_str.split(":")[0])
                except Exception:
                    continue

                if hr_int < 8 or hr_int > 18:
                    continue

                w_kts = float(h.get("wind_kts", 0))
                g_kts = float(h.get("gust_kts", w_kts))

                # Check quiver matches using traction engine
                best_kite = None
                best_quality = None
                for k in gear:
                    ev = kitesurf_bot.evaluate_active_kite(k, weight_kg, w_kts, g_kts, level=level, board=board_type)
                    if ev["in_sweet"]:
                        best_kite = ev
                        best_quality = "sweet"
                        break
                    elif ev["in_range"] and w_kts >= ev["sweet_min"] - 1.5:
                        if not best_kite:
                            best_kite = ev
                            best_quality = "rideable"

                if best_kite:
                    candidate_hours.append({
                        "hour": hr_int,
                        "hour_str": h_str,
                        "wind_kts": w_kts,
                        "gust_kts": g_kts,
                        "direction": h.get("direction", "E"),
                        "shoreline": (h.get("shoreline") or {}).get("type", "Side-Onshore"),
                        "kite": best_kite,
                        "quality": best_quality
                    })

            if len(candidate_hours) < 2:
                continue

            # Peak hour in this window
            peak_item = max(candidate_hours, key=lambda x: x["wind_kts"])
            peak_wind = peak_item["wind_kts"]
            start_hr = candidate_hours[0]["hour_str"]
            end_hr = candidate_hours[-1]["hour_str"]
            timing_display = f"{date_display} ({start_hr} – {end_hr})"

            # Check trigger condition
            reason = None
            if is_weekend:
                reason = f"Weekend window opened up ({peak_wind:.0f} kts peak)"
            else:
                # Check if forecast improved compared to previous snapshot
                prev_wind = prev_spot_snap.get(date_str, 0)
                if prev_wind > 0 and (peak_wind - prev_wind) >= 3.0:
                    reason = f"Wind improved by +{peak_wind - prev_wind:.0f} kts into your quiver sweet spot"
                elif peak_item["quality"] == "sweet":
                    reason = f"Prime sweet-spot wind detected ({peak_wind:.0f} kts)"

            # Save snapshot for next comparison
            snaps.setdefault(spot_key, {})[date_str] = peak_wind
            save_snapshots(snaps)

            if not reason:
                continue

            # Kite display
            kite_obj = peak_item["kite"]
            kite_desc = f"{kite_obj['brand']} {kite_obj['model']} {kite_obj['size']}m"
            if kite_obj.get("year"):
                kite_desc = f"{kite_obj['brand']} {kite_obj['model']} ({kite_obj['year']}) {kite_obj['size']}m"

            board_desc = board_type
            if boards and len(boards) > 0:
                b0 = boards[0]
                board_desc = f"{b0.get('brand', '')} {b0.get('model', '')} {b0.get('size', '')}".strip() or board_type

            return {
                "spot_name": spot_name,
                "date": date_str,
                "date_display": date_display,
                "timing_display": timing_display,
                "wind_kts": round(peak_wind),
                "gust_kts": round(peak_item["gust_kts"]),
                "direction": peak_item["direction"],
                "shoreline": peak_item["shoreline"],
                "kite_desc": kite_desc,
                "board_desc": board_desc,
                "reason": reason,
                "weight_kg": weight_kg
            }

        return None
    except Exception as e:
        print(f"[SpotAlerts] Error evaluating rider spot alert: {e}")
        return None

# ==============================================================================
# 5. ORCHESTRATION & DISPATCH ENGINE
# ==============================================================================

def check_and_dispatch_alerts_for_user(user_email: str, force_test: bool = False) -> Dict[str, Any]:
    """Evaluates and sends spot alerts for a single user."""
    import kitesurf_bot
    db = kitesurf_bot.load_users_db()
    users = db.get("users", {})
    user = users.get(user_email.strip().lower())
    if not user:
        return {"success": False, "error": "User not found"}

    spot_alerts = user.get("spot_alerts", {})
    if not spot_alerts and not force_test:
        return {"success": True, "message": "No spot alerts configured"}

    rider_name = user.get("name") or user_email.split("@")[0].title()
    push_sub = user.get("push_subscription")
    email_enabled = spot_alerts.get("enable_email", True)
    push_enabled = spot_alerts.get("enable_push", True)
    if force_test and not email_enabled and not push_enabled:
        email_enabled = True
    spots = spot_alerts.get("spots", [])

    # If testing and no spots configured, default to current spot or Cumbuco
    if force_test and not spots:
        default_spot = (user.get("spot") or {}).get("name") if isinstance(user.get("spot"), dict) else user.get("spot")
        spots = [default_spot or "Cumbuco, Brazil"]

    history = load_alert_history()
    dispatched_count = 0
    results = []

    for s_name in spots:
        # Load spot coordinates
        spot_coords = None
        try:
            from kite_spots import GLOBAL_KITE_SPOTS
            for s in GLOBAL_KITE_SPOTS:
                if s.get("name") == s_name or s.get("short_name") == s_name:
                    spot_coords = s
                    break
        except Exception:
            pass
        if not spot_coords:
            spot_coords = {"name": s_name, "lat": -3.6247, "lon": -38.7297}

        try:
            forecast = kitesurf_bot.fetch_live_forecast(spot_coords)
        except Exception as e:
            print(f"[SpotAlerts] Forecast fetch error for {s_name}: {e}")
            continue

        alert_data = None
        if force_test:
            # Build synthetic test alert matching user's gear
            gear = user.get("gear", [])
            k_desc = f"{gear[0].get('brand', 'Kite')} {gear[0].get('model', '')} {gear[0].get('size', '9')}m" if gear else "9m Rebel SLS"
            alert_data = {
                "spot_name": s_name,
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "date_display": "Tomorrow (Saturday)",
                "timing_display": "Tomorrow (Saturday) · 13:30 – 17:00",
                "wind_kts": 18,
                "gust_kts": 22,
                "direction": "E",
                "shoreline": "Side-Onshore",
                "kite_desc": k_desc,
                "board_desc": user.get("board", "Twintip"),
                "reason": "Weekend prime session test trigger",
                "weight_kg": user.get("weight_kg", 74.0)
            }
        else:
            alert_data = evaluate_rider_spot_alert(user, s_name, forecast, spot_alerts)

        if not alert_data:
            continue

        # Deduplication: max 1 alert per user per spot per date window (unless force test)
        hist_key = f"{user_email}_{s_name}_{alert_data['date']}"
        now_ts = time.time()
        if not force_test:
            if hist_key in history and (now_ts - history[hist_key]) < 86400:
                print(f"[SpotAlerts] Alert for {hist_key} already sent in last 24h. Skipping.")
                continue

        channels_sent = []

        # 1. PWA Web Push Notification
        if push_enabled and push_sub:
            push_payload = {
                "title": f"🚨 Wind Alarm: {alert_data['wind_kts']} kts at {alert_data['spot_name']}",
                "body": f"Ready for your {alert_data['kite_desc']}! {alert_data['timing_display']}.",
                "url": f"/?spot={alert_data['spot_name'].replace(' ', '%20')}"
            }
            ok, status = send_web_push(push_sub, push_payload)
            if ok:
                channels_sent.append("PWA Web Push")
            elif status == "expired":
                user.pop("push_subscription", None)
                kitesurf_bot.save_users_db(db)

        # 2. Email Briefing via Resend
        if email_enabled and user_email and "@" in user_email:
            ok_email = send_spot_alert_email(user_email, rider_name, alert_data)
            if ok_email:
                channels_sent.append("Email Briefing")

        # 3. Daniel (Admin) Telegram Alert
        if channels_sent:
            notify_admin_spot_alert(rider_name, user_email, s_name, alert_data, channels_sent)
            history[hist_key] = now_ts
            dispatched_count += 1
            results.append({
                "spot": s_name,
                "channels": channels_sent,
                "alert": alert_data
            })

    save_alert_history(history)
    return {
        "success": True,
        "dispatched_count": dispatched_count,
        "results": results
    }

def run_all_beta_alerts_cycle():
    """Background cycle checking all Beta riders for wind alarms."""
    try:
        import kitesurf_bot
        db = kitesurf_bot.load_users_db()
        users = db.get("users", {})
        total_checked = 0
        total_fired = 0

        for em, u in users.items():
            is_beta = u.get("is_beta_rider") or u.get("beta_status") == "approved"
            if not is_beta:
                continue

            alerts_pref = u.get("spot_alerts", {})
            if not alerts_pref or not alerts_pref.get("enabled", True):
                continue

            total_checked += 1
            res = check_and_dispatch_alerts_for_user(em, force_test=False)
            total_fired += res.get("dispatched_count", 0)

        print(f"[SpotAlerts] Background check cycle finished. Checked {total_checked} beta riders, dispatched {total_fired} alarms.")
    except Exception as e:
        print(f"[SpotAlerts] Error in run_all_beta_alerts_cycle: {e}")
