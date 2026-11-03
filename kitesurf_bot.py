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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forecast_cache.json")
GUST_WARNING_THRESHOLD_KTS = 30
SSL_CTX = ssl._create_unverified_context()

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


def fetch_tides(lat: float, lon: float, timezone_str: str = "auto") -> list:
    today_tides, _ = fetch_tides_both_days(lat, lon, timezone_str)
    return today_tides


def fetch_tides_both_days(lat: float, lon: float, timezone_str: str = "auto") -> tuple:
    url = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={lat}&longitude={lon}&hourly=sea_level_height_msl&timezone={timezone_str}&forecast_days=2"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        times = data.get("hourly", {}).get("time", [])
        levels = data.get("hourly", {}).get("sea_level_height_msl", [])
        if not times or not levels:
            return [], []

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

        return today_tides, tomorrow_tides
    except Exception as e:
        print(f"Error fetching tides: {e}")
        return [], []


def fetch_weather_openmeteo(spot: dict) -> dict:
    params = {
        "latitude": spot["lat"],
        "longitude": spot["lon"],
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "hourly": "temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "wind_speed_unit": "kn",
        "timezone": spot.get("timezone", "auto"),
        "forecast_days": 2
    }
    url = f"https://api.open-meteo.com/v1/forecast?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    utc_offset = data.get("utc_offset_seconds")
    spot_tz = data.get("timezone", spot.get("timezone", "auto"))

    current = data.get("current", {})
    hourly = data.get("hourly", {})
    speeds = hourly.get("wind_speed_10m", [])
    gusts = hourly.get("wind_gusts_10m", [])
    directions = hourly.get("wind_direction_10m", [])
    temps = hourly.get("temperature_2m", [])

    target_hours = {
        "Morning (09:00)": 9,
        "Midday (12:00)": 12,
        "Afternoon (15:00)": 15,
        "Sunset (17:00)": 17
    }

    # Today schedule (Day 0: 0..23)
    schedule = {}
    for label, hr in target_hours.items():
        if hr < len(speeds):
            schedule[label] = {
                "wind_kts": round_knots(speeds[hr]),
                "gust_kts": round_knots(gusts[hr]),
                "direction": degrees_to_cardinal(directions[hr]),
                "temp": round(temps[hr], 1)
            }

    # Tomorrow schedule (Day 1: 24..47)
    schedule_tomorrow = {}
    for label, hr in target_hours.items():
        tmrw_hr = hr + 24
        if tmrw_hr < len(speeds):
            schedule_tomorrow[label] = {
                "wind_kts": round_knots(speeds[tmrw_hr]),
                "gust_kts": round_knots(gusts[tmrw_hr]),
                "direction": degrees_to_cardinal(directions[tmrw_hr]),
                "temp": round(temps[tmrw_hr], 1)
            }

    cur_wind = round_knots(current.get("wind_speed_10m", speeds[12] if len(speeds) > 12 else 16.0))
    cur_gust = round_knots(current.get("wind_gusts_10m", gusts[12] if len(gusts) > 12 else cur_wind))
    cur_dir = degrees_to_cardinal(current.get("wind_direction_10m", 90))
    cur_temp = round(current.get("temperature_2m", 28.5), 1)

    today_temps = temps[:24] if len(temps) >= 24 else temps
    today_gusts = gusts[:24] if len(gusts) >= 24 else gusts
    tmrw_temps = temps[24:48] if len(temps) >= 48 else temps
    tmrw_gusts = gusts[24:48] if len(gusts) >= 48 else gusts

    return {
        "spot": spot["name"],
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
            "temp": cur_temp
        },
        "schedule": schedule,
        "schedule_tomorrow": schedule_tomorrow
    }


def fetch_weather_metno(spot: dict) -> dict:
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={spot['lat']}&lon={spot['lon']}"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0 (daniel@kitesurf.dev)"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    series = data.get("properties", {}).get("timeseries", [])
    if not series:
        raise ValueError("Empty timeseries from Met.no")

    cur_details = series[0]["data"]["instant"]["details"]
    cur_wind = round_knots(cur_details["wind_speed"] * 1.94384)
    cur_gust = round_knots(cur_details.get("wind_speed_of_gust", cur_details["wind_speed"]) * 1.94384)
    cur_temp = round(cur_details["air_temperature"], 1)
    cur_dir = degrees_to_cardinal(cur_details.get("wind_from_direction", 90))

    schedule = {
        "Morning (09:00)": {"wind_kts": cur_wind, "gust_kts": cur_gust, "direction": cur_dir, "temp": cur_temp},
        "Midday (12:00)": {"wind_kts": cur_wind, "gust_kts": cur_gust, "direction": cur_dir, "temp": cur_temp},
        "Afternoon (15:00)": {"wind_kts": max(12, cur_wind - 1), "gust_kts": cur_gust, "direction": cur_dir, "temp": cur_temp},
        "Sunset (17:00)": {"wind_kts": max(10, cur_wind - 3), "gust_kts": max(14, cur_gust - 3), "direction": cur_dir, "temp": cur_temp - 1}
    }

    schedule_tomorrow = {
        "Morning (09:00)": {"wind_kts": cur_wind, "gust_kts": cur_gust, "direction": cur_dir, "temp": cur_temp},
        "Midday (12:00)": {"wind_kts": cur_wind + 1, "gust_kts": cur_gust + 2, "direction": cur_dir, "temp": cur_temp + 1},
        "Afternoon (15:00)": {"wind_kts": max(12, cur_wind), "gust_kts": cur_gust, "direction": cur_dir, "temp": cur_temp},
        "Sunset (17:00)": {"wind_kts": max(10, cur_wind - 2), "gust_kts": max(14, cur_gust - 2), "direction": cur_dir, "temp": cur_temp - 1}
    }

    approx_offset = round(spot.get("lon", -38.7297) / 15.0) * 3600
    return {
        "spot": spot["name"],
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
            "temp": cur_temp
        },
        "schedule": schedule,
        "schedule_tomorrow": schedule_tomorrow
    }


def fetch_live_forecast(spot: dict) -> dict:
    forecast = None
    try:
        forecast = fetch_weather_openmeteo(spot)
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
        forecast = {
            "spot": spot["name"],
            "timezone": spot.get("timezone", "America/Fortaleza"),
            "utc_offset_seconds": -10800,
            "temp_min": 25.5,
            "temp_max": 30.5,
            "max_gust": 28.0,
            "tomorrow_temp_min": 25.0,
            "tomorrow_temp_max": 31.0,
            "tomorrow_max_gust": 26.0,
            "current": {"wind_kts": 16.0, "gust_kts": 25.0, "direction": "E", "temp": 29.0},
            "schedule": {
                "Morning (09:00)": {"wind_kts": 15.0, "gust_kts": 24.0, "direction": "ESE", "temp": 27.5},
                "Midday (12:00)": {"wind_kts": 18.0, "gust_kts": 28.0, "direction": "E", "temp": 30.0},
                "Afternoon (15:00)": {"wind_kts": 16.5, "gust_kts": 26.0, "direction": "E", "temp": 29.5},
                "Sunset (17:00)": {"wind_kts": 13.0, "gust_kts": 22.0, "direction": "E", "temp": 28.0}
            },
            "schedule_tomorrow": {
                "Morning (09:00)": {"wind_kts": 14.5, "gust_kts": 23.0, "direction": "ESE", "temp": 27.0},
                "Midday (12:00)": {"wind_kts": 17.5, "gust_kts": 27.0, "direction": "E", "temp": 29.5},
                "Afternoon (15:00)": {"wind_kts": 16.0, "gust_kts": 25.0, "direction": "E", "temp": 29.0},
                "Sunset (17:00)": {"wind_kts": 12.5, "gust_kts": 21.0, "direction": "E", "temp": 27.5}
            }
        }

    today_tides, tomorrow_tides = fetch_tides_both_days(spot["lat"], spot["lon"], spot.get("timezone", "auto"))
    forecast["tides"] = today_tides
    forecast["tides_tomorrow"] = tomorrow_tides
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(forecast, f)
    except Exception:
        pass
    return forecast


def evaluate_active_kite(kite_entry: dict, weight_kg: float, wind_kts: float, gust_kts: float) -> dict:
    specs = lookup_kite_specs(kite_entry["brand"], kite_entry["model"], kite_entry["size"])
    w_factor = math.sqrt(weight_kg / 75.0)

    min_k = specs["min"] * w_factor
    sweet_min = specs["sweet"][0] * w_factor
    sweet_max = specs["sweet"][1] * w_factor
    max_k = specs["max"] * w_factor

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
    all_inventory: list = None
) -> str:
    if not active_inventory:
        if all_inventory:
            return "⚠️ No active kites in bag (type `/take all`)"
        return "⚠️ No quiver existing (type `/kite 1 <Brand> <Model> <Size>`)"

    evaluated = [evaluate_active_kite(k, weight_kg, wind_kts, gust_kts) for k in active_inventory]

    # 1. Exact sweet spot match
    sweet_matches = [k for k in evaluated if k["in_sweet"]]
    if sweet_matches:
        best = min(sweet_matches, key=lambda k: k["dist_to_sweet"])
        return f"Rig {best['display_name']}"

    # 2. Inside rideable wind range
    range_matches = [k for k in evaluated if k["in_range"]]
    if range_matches:
        best = min(range_matches, key=lambda k: k["dist_to_sweet"])
        tag = " (Powered up)" if wind_kts > best["sweet_max"] else " (Light end)"
        return f"Rig {best['display_name']}{tag}"

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

    # 3. Wind too light (< min of active quiver): DO NOT recommend rigging the biggest kite!
    if wind_kts < min(mins):
        biggest = max(evaluated, key=lambda k: k["size"])
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

        if len(evaluated) > 1:
            return f"⚠️ {w_kts_rounded} kts (not enough for your {kite_desc} kite, as the biggest one you have — needs min ~{min_k_rounded} kts){bigger_home_tip}"
        else:
            return f"⚠️ {w_kts_rounded} kts (not enough for your {kite_desc} kite — needs min ~{min_k_rounded} kts){bigger_home_tip}"

    # 4. Wind above max of active quiver
    if wind_kts > max(maxs):
        max_k_rounded = round_knots(smallest["max_k"])
        if wind_kts <= smallest["max_k"] + 4:
            return f"Rig {smallest['display_name']} (🚨 Overpowered — max ~{max_k_rounded} kts, depower fully){home_tip}"
        elif wind_kts <= smallest["max_k"] + 8:
            return f"Rig {smallest['display_name']} (🚨 Heavily Overpowered — max ~{max_k_rounded} kts!){home_tip}"
        else:
            if home_tip:
                return f"🚨 Wind too strong ({round_knots(wind_kts)} kts) for {smallest['display_name']} (max ~{max_k_rounded} kts).{home_tip}"
            return f"🚨 Wind too strong ({round_knots(wind_kts)} kts) for {smallest['display_name']} (max ~{max_k_rounded} kts) — hold off or rig smaller!"

    nearest = min(evaluated, key=lambda k: k["dist_to_sweet"])
    return f"Rig {nearest['display_name']} (Marginal)"


def build_quiver_header_text(inventory: list, active_kites: list) -> str:
    if not inventory:
        return "  ⚠️ *No quiver existing yet!* Enter your gear:\n  👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`"
    if not active_kites:
        return "  ⚠️ *No active kites in bag today!* Type `/take all` to activate your quiver."
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

    inventory = user_profile.get("inventory", [])
    active_kites = [k for k in inventory if k.get("active", True)]

    quiver_str = build_quiver_header_text(inventory, active_kites)

    lines = [
        f"🏄‍♂️ *Kitesurf Morning Briefing: {forecast['spot']}*",
        f"📅 *Date:* {date_str} (Local Time: {time_str})",
        f"👤 *Rider:* {rider_name} · {weight} kg ({board})",
        f"🎒 *Available Quiver:*",
        quiver_str,
        f"\n🌡 *Temp:* {forecast['temp_min']}°C – {forecast['temp_max']}°C\n",
        f"🌊 *Tides Today:*",
        format_tides_text(forecast.get("tides", [])),
        f"\n🎯 *Rigging Schedule:*"
    ]

    for slot_name, slot in forecast["schedule"].items():
        rec = recommend_from_available_quiver(weight, active_kites, slot["wind_kts"], slot["gust_kts"], all_inventory=inventory)
        w_kts = round_knots(slot['wind_kts'])
        g_kts = round_knots(slot['gust_kts'])
        lines.append(
            f"• *{slot_name}:* {w_kts} kts (gusts {g_kts} kts, {slot['direction']}) "
            f"→ {rec}"
        )

    if forecast["max_gust"] >= GUST_WARNING_THRESHOLD_KTS:
        lines.append(f"\n⚠️ *Gust Alert:* Max gusts reaching *{round_knots(forecast['max_gust'])} knots* today.")

    if not inventory:
        lines.append("\n⚠️ *Action Required:* No quiver existing yet! Please enter your kites:\n👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`")

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

    inventory = user_profile.get("inventory", [])
    active_kites = [k for k in inventory if k.get("active", True)]

    t_min = forecast.get("tomorrow_temp_min", forecast.get("temp_min", 25))
    t_max = forecast.get("tomorrow_temp_max", forecast.get("temp_max", 31))
    max_gust = round_knots(forecast.get("tomorrow_max_gust", forecast.get("max_gust", 26)))

    quiver_str = build_quiver_header_text(inventory, active_kites)

    lines = [
        f"🌅 *Tomorrow's Kitesurf Forecast: {forecast['spot']}*",
        f"📅 *Date:* {tomorrow_date_str} (Day After)",
        f"📍 *Spot Local Time:* {local_time_str}",
        f"👤 *Rider:* {rider_name} · {weight}kg ({board})",
        f"🎒 *Available Quiver:*",
        quiver_str,
        f"\n🌡 *Temp:* {t_min}°C – {t_max}°C · 💨 *Max Gusts:* {max_gust} kts"
    ]

    if is_evening_auto:
        lines.append(f"\n_🌙 Past 17:00 local time — showing tomorrow's forecast so you can pack your gear tonight!_")
    else:
        lines.append(f"\n_📋 Showing requested tomorrow's forecast:_")

    lines.append(f"\n🌬 *Tomorrow's Rigging Schedule:*")
    schedule = forecast.get("schedule_tomorrow") or forecast.get("schedule", {})
    for slot_name, slot in schedule.items():
        rec = recommend_from_available_quiver(weight, active_kites, slot["wind_kts"], slot["gust_kts"], all_inventory=inventory)
        w_kts = round_knots(slot['wind_kts'])
        g_kts = round_knots(slot['gust_kts'])
        lines.append(f"• *{slot_name}:* {w_kts} kts (gusts {g_kts} kts, {slot.get('direction', 'E')}) → {rec}")

    lines.append(f"\n🌊 *Tomorrow's Tides:*")
    lines.append(format_tides_text(forecast.get("tides_tomorrow", [])))

    if max_gust >= GUST_WARNING_THRESHOLD_KTS:
        lines.append(f"\n⚠️ *Gust Alert:* Max gusts reaching *{max_gust} knots* tomorrow.")

    if not inventory:
        lines.append("\n⚠️ *Action Required:* No quiver existing yet! Please enter your kites:\n👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`")

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

    inventory = user_profile.get("inventory", [])
    active_kites = [k for k in inventory if k.get("active", True)]

    cur = forecast.get("current", {})
    wind_kts = round_knots(cur.get("wind_kts", 16.0))
    gust_kts = round_knots(cur.get("gust_kts", 22.0))
    direct = cur.get("direction", "E")
    temp = cur.get("temp", 28.0)

    rec = recommend_from_available_quiver(weight, active_kites, wind_kts, gust_kts, all_inventory=inventory)
    quiver_str = build_quiver_header_text(inventory, active_kites)

    lines = [
        f"🏄‍♂️ *Live Spot Report: {forecast['spot']}*",
        f"📍 *Spot Local Time:* {local_time_str} · {local_date_str}",
        f"🌡 *Temp:* {temp}°C",
        f"👤 *Rider:* {rider_name} · {weight}kg ({board})",
        f"🎒 *Available Quiver:*",
        quiver_str,
        f"\n🌬 *Wind Right Now:*",
        f"• *Speed:* *{wind_kts} knots* (Gusts: *{gust_kts} knots*, {direct})",
        f"• *Right Now Recommendation:* → {rec}\n",
        f"🌊 *Tides Today:*",
        format_tides_text(forecast.get("tides", [])),
        f"\n📅 *Upcoming Today:*"
    ]

    for slot_name, slot in forecast.get("schedule", {}).items():
        r = recommend_from_available_quiver(weight, active_kites, slot["wind_kts"], slot["gust_kts"], all_inventory=inventory)
        w_kts = round_knots(slot['wind_kts'])
        g_kts = round_knots(slot['gust_kts'])
        lines.append(f"• *{slot_name}:* {w_kts} kts (gusts {g_kts} kts) → {r}")

    if not inventory:
        lines.append("\n⚠️ *Action Required:* No quiver existing yet! Please enter your kites:\n👉 `/kite 1 <Brand> <Model> <Size> (<Year>)`")

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


def geocode_place_name(query: str):
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "KiteForecastBot/1.0"})
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
            "⚠️ *No quiver existing yet!* To calculate your personalized wind ranges and rigging choices, you need to enter your kites first."
            if not has_kites
            else f"🎒 *Your quiver has {len(user_profile.get('inventory', []))} kite(s) registered.* (Type `/kites` to inspect)"
        )
        welcome_intro = (
            f"👋 *Welcome to KiteForecast, {first_name}!* 🏄‍♂️\n\n"
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
            "🎒 *Quiver Management:*\n"
            "• `/kites` → View your quiver and bag status\n"
            "• `/take 1, 2` → Pick which kites you brought to the beach today\n"
            "• `/take all` → Mark all your kites active in your bag\n"
            "• `/reset profile` → Wipe your quiver and start over\n\n"
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
            "📲 *Share KiteForecast with your buddies!*\n\n"
            "Direct link: https://t.me/KiteForecast_bot\n\n"
            "When they scan this QR code or tap the link, they get their own private rider profile, quiver, and GPS spot forecasts!"
        )
        send_photo_telegram(qr_url, caption, config["telegram_token"], chat_id)
        return None

    elif cmd.startswith("/app") or cmd.startswith("/web") or "interactive web app" in cmd.lower():
        return (
            "📱 *KiteForecast Interactive Web App:* 🏄‍♂️\n\n"
            "👉 https://kiteapp.onrender.com\n\n"
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

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            params = urllib.parse.parse_qs(parsed.query)

            # 1. Health check (for Render & uptime monitors)
            if path in ["/api/health", "/health"]:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"status": "ok", "service": "KiteForecastApp", "multi_user": true}\n')
                return

            # 2. API: Kite Catalog
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
                    f_data = fetch_live_forecast({"lat": lat, "lon": lon, "name": name, "timezone": tz})
                    out = json.dumps(f_data).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(out)
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            # 4. API: Geocoding
            if path == "/api/geocode":
                q = params.get("q", [""])[0]
                lat, lon, res_name = geocode_place_name(q)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"lat": lat, "lon": lon, "name": res_name}).encode("utf-8"))
                return

            # 5. Static Files: PWA Web App
            if path in ["/", "/index.html"]:
                index_path = os.path.join(web_dir, "index.html")
                if os.path.exists(index_path):
                    with open(index_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
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
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return

            if path in ["/icon.png", "/kiteforecast_bot_qr.png"]:
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
                    rec = recommend_from_available_quiver(w, inv, w_kts, g_kts, all_inventory=all_inv)
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
        if profile.get("morning_briefing", True):
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
    elif len(sys.argv) > 1 and sys.argv[1] in ["--briefing-all", "--all"]:
        send_morning_briefing_to_all()
        return

    # Single-user or default run
    admin_id = str(config.get("admin_id", "7424865438"))
    profile = config.get("users", {}).get(admin_id, list(config.get("users", {}).values())[0])
    forecast = fetch_live_forecast(profile["spot"])
    briefing = format_briefing(forecast, profile)
    send_telegram(briefing, config["telegram_token"], str(profile["user_id"]))
    print(f"Morning briefing delivered to {profile['rider_name']}!")


if __name__ == "__main__":
    main()
