import os
import json
import time
from datetime import datetime, timezone

TELEMETRY_FILE = "spot_telemetry_db.json"
MAX_HISTORY = 5000

def _load_telemetry() -> dict:
    if os.path.exists(TELEMETRY_FILE):
        try:
            with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading telemetry: {e}")
    return {
        "spot_views": [],
        "spot_totals": {},
        "nationality_totals": {},
        "spot_by_nationality": {},
        "searches": [],
        "search_totals": {}
    }

def _save_telemetry(data: dict):
    try:
        with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving telemetry: {e}")

def record_spot_view(spot_name: str, lat: float, lon: float, email: str = "", rider_name: str = "", nationality: str = "", ip: str = "", user_agent: str = ""):
    if not spot_name:
        return
    data = _load_telemetry()
    now_iso = datetime.now(timezone.utc).isoformat() + "Z"
    
    clean_nat = (nationality or "").strip().title()
    clean_rider = (rider_name or (email.split("@")[0].title() if email else "Visitor")).strip()
    
    entry = {
        "timestamp": now_iso,
        "spot_name": spot_name,
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "email": email or "anonymous",
        "rider_name": clean_rider,
        "nationality": clean_nat or "Not specified",
        "ip_hash": str(hash(ip))[-8:] if ip else "",
        "action": "view_forecast"
    }
    
    # 1. Append to recent views (ring buffer)
    views = data.setdefault("spot_views", [])
    views.insert(0, entry)
    if len(views) > MAX_HISTORY:
        data["spot_views"] = views[:MAX_HISTORY]
        
    # 2. Increment spot totals
    totals = data.setdefault("spot_totals", {})
    totals[spot_name] = totals.get(spot_name, 0) + 1
    
    # 3. Increment nationality totals
    if clean_nat and clean_nat != "Not Specified":
        nat_totals = data.setdefault("nationality_totals", {})
        nat_totals[clean_nat] = nat_totals.get(clean_nat, 0) + 1
        
        # Spot by nationality mapping
        s_by_nat = data.setdefault("spot_by_nationality", {})
        nat_map = s_by_nat.setdefault(clean_nat, {})
        nat_map[spot_name] = nat_map.get(spot_name, 0) + 1
        
    _save_telemetry(data)

def record_spot_search(query: str, country_code: str = "", results_count: int = 0, email: str = ""):
    q_clean = (query or "").strip().lower()
    if not q_clean:
        return
    data = _load_telemetry()
    now_iso = datetime.now(timezone.utc).isoformat() + "Z"
    
    # Add to searches list
    searches = data.setdefault("searches", [])
    searches.insert(0, {
        "timestamp": now_iso,
        "query": query.strip(),
        "country": country_code.upper() if country_code else "ALL",
        "results": results_count,
        "email": email or "anonymous"
    })
    if len(searches) > 1000:
        data["searches"] = searches[:1000]
        
    # Increment search query totals
    s_totals = data.setdefault("search_totals", {})
    s_totals[q_clean] = s_totals.get(q_clean, 0) + 1
    
    _save_telemetry(data)

def get_spot_analytics_summary() -> dict:
    data = _load_telemetry()
    views = data.get("spot_views", [])
    totals = data.get("spot_totals", {})
    nat_totals = data.get("nationality_totals", {})
    s_totals = data.get("search_totals", {})
    
    # Sort top spots
    sorted_spots = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:15]
    top_spots = []
    total_views = sum(totals.values()) or 1
    
    for s_name, count in sorted_spots:
        # Find latest entry for coordinates
        latest = next((v for v in views if v.get("spot_name") == s_name), {})
        top_spots.append({
            "spot_name": s_name,
            "views": count,
            "share_pct": round((count / total_views) * 100, 1),
            "lat": latest.get("lat"),
            "lon": latest.get("lon"),
            "last_viewed": latest.get("timestamp")
        })
        
    # Sort nationalities
    sorted_nats = sorted(nat_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    total_nats = sum(nat_totals.values()) or 1
    top_nationalities = [
        {
            "nationality": nat,
            "count": cnt,
            "pct": round((cnt / total_nats) * 100, 1)
        }
        for nat, cnt in sorted_nats
    ]
    
    # Top searches
    top_searches = [
        {"query": q.title(), "count": cnt}
        for q, cnt in sorted(s_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Unique riders
    unique_emails = set(v.get("email") for v in views if v.get("email") and v.get("email") != "anonymous")
    
    return {
        "total_spot_views": len(views),
        "total_cumulative_views": sum(totals.values()),
        "unique_registered_riders_active": len(unique_emails),
        "top_spots": top_spots,
        "top_nationalities": top_nationalities,
        "recent_activity": views[:30],
        "top_searches": top_searches,
        "last_updated": datetime.now(timezone.utc).isoformat() + "Z"
    }
