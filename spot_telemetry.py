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
        "search_totals": {},
        "travel_inquiries": [],
        "travel_destinations": {},
        "travel_months": {},
        "travel_gear_gaps": {}
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
        
    s_totals = data.setdefault("search_totals", {})
    s_totals[q_clean] = s_totals.get(q_clean, 0) + 1
    
    _save_telemetry(data)

def record_travel_inquiry(
    spot_id: str,
    spot_name: str,
    country: str,
    month: int,
    style: str = "All",
    weight_kg: float = 75.0,
    discipline: str = "Twintip",
    quiver_sizes: list = None,
    recommended_pack: list = None,
    gear_gaps: list = None,
    email: str = "",
    rider_name: str = "",
    nationality: str = ""
):
    data = _load_telemetry()
    now_iso = datetime.now(timezone.utc).isoformat() + "Z"
    
    clean_nat = (nationality or "").strip().title()
    clean_rider = (rider_name or (email.split("@")[0].title() if email else "Visiting Rider")).strip()
    
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    m_name = month_names[month-1] if 1 <= month <= 12 else "All Year"
    
    inquiry = {
        "timestamp": now_iso,
        "spot_id": spot_id,
        "spot_name": spot_name,
        "country": country,
        "month": month,
        "month_name": m_name,
        "style": style,
        "weight_kg": weight_kg,
        "discipline": discipline,
        "quiver_sizes": quiver_sizes or [],
        "recommended_pack": recommended_pack or [],
        "gear_gaps": gear_gaps or [],
        "email": email or "anonymous",
        "rider_name": clean_rider,
        "nationality": clean_nat or "Not specified"
    }
    
    inquiries = data.setdefault("travel_inquiries", [])
    inquiries.insert(0, inquiry)
    if len(inquiries) > 2000:
        data["travel_inquiries"] = inquiries[:2000]
        
    t_spots = data.setdefault("travel_destinations", {})
    t_spots[spot_name] = t_spots.get(spot_name, 0) + 1
    
    t_months = data.setdefault("travel_months", {})
    m_key = str(month) if 1 <= month <= 12 else "all_year"
    t_months[m_key] = t_months.get(m_key, 0) + 1
    
    if gear_gaps:
        t_gaps = data.setdefault("travel_gear_gaps", {})
        for g in gear_gaps:
            sz = str(g.get("size") or g.get("suggested_size") or "")
            if sz:
                t_gaps[sz] = t_gaps.get(sz, 0) + 1
                
    _save_telemetry(data)

def get_spot_analytics_summary() -> dict:
    data = _load_telemetry()
    views = data.get("spot_views", [])
    totals = data.get("spot_totals", {})
    nat_totals = data.get("nationality_totals", {})
    s_totals = data.get("search_totals", {})
    
    # Load and reconcile registered riders via kitesurf_bot.load_users_db()
    users_db = {"users": {}}
    try:
        import kitesurf_bot
        users_db = kitesurf_bot.load_users_db()
    except Exception:
        users_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users_web_db.json")
        if os.path.exists(users_file):
            try:
                with open(users_file, "r", encoding="utf-8") as f:
                    users_db = json.load(f)
            except Exception:
                pass
            
    users = users_db.get("users", {})
    registered_riders = []
    for em, u in users.items():
        user_views = [v for v in views if (v.get("email") or "").strip().lower() == em.lower()]
        last_view = user_views[0] if user_views else {}
        gear_items = u.get("gear", [])
        boards_items = u.get("boards", [])
        gear_desc = []
        gear_list = []
        for g in gear_items:
            b = g.get("brand", "")
            m = g.get("model", "")
            sz = g.get("size", "")
            yr = g.get("year", "")
            cat = g.get("category", "kite")
            ktype = g.get("kite_type", "tube")
            act = g.get("active", True) is not False
            gear_desc.append(f"{b} {m} {sz}m".strip())
            gear_list.append({
                "brand": b,
                "model": m,
                "size": sz,
                "year": yr,
                "category": cat,
                "kite_type": ktype,
                "active": act,
                "label": f"{b} {m} {sz}m".strip()
            })
            
        boards_desc = []
        boards_list = []
        for b in boards_items:
            bt = b.get("type", "Twintip")
            bb = b.get("brand", "")
            bm = b.get("model", "")
            bsz = b.get("size", "")
            bvol = b.get("volume")
            bmast = b.get("mast")
            bcarb = bool(b.get("carbon"))
            bact = b.get("active", True) is not False
            boards_desc.append(f"{bt} {bb} {bm} {bsz}".strip())
            boards_list.append({
                "type": bt,
                "brand": bb,
                "model": bm,
                "size": bsz,
                "volume": bvol,
                "mast": bmast,
                "carbon": bcarb,
                "active": bact,
                "label": f"{bt} · {bb} {bm} {bsz}".strip()
            })

        is_beta = bool(u.get("is_beta_rider") or u.get("beta_status") == "approved")
        b_status = u.get("beta_status") or ("approved" if is_beta else "none")
        nat_val = u.get("nationality") or last_view.get("nationality") or "Not specified"
        if nat_val and nat_val not in ("Not specified", "Undefined"):
            if nat_val not in nat_totals:
                nat_totals[nat_val] = 1

        registered_riders.append({
            "email": em,
            "name": u.get("name") or em.split("@")[0].title(),
            "nationality": nat_val,
            "weight_kg": u.get("weight_kg", 75.0),
            "level": (u.get("level") or "intermediate").capitalize(),
            "board": u.get("board", "Twintip"),
            "gear_count": len(gear_items),
            "boards_count": len(boards_items),
            "gear_list": gear_list,
            "boards_list": boards_list,
            "gear_summary": ", ".join(gear_desc[:5]) if gear_desc else "No kites registered yet",
            "boards_summary": ", ".join(boards_desc[:4]) if boards_desc else "No boards registered yet",
            "is_beta_rider": is_beta,
            "beta_status": b_status,
            "registered_at": u.get("registered_at") or u.get("created_at") or last_view.get("timestamp"),
            "last_active": last_view.get("timestamp") or u.get("last_login") or u.get("last_sync") or u.get("registered_at"),
            "last_spot": last_view.get("spot_name") or (u.get("spot", {}).get("name") if isinstance(u.get("spot"), dict) else u.get("spot")) or "None"
        })

    # Sort riders: pending beta first, then by last active descending
    registered_riders.sort(key=lambda r: (1 if r.get("beta_status") == "pending" else 0, str(r.get("last_active") or r.get("registered_at") or "")), reverse=True)
    total_beta = len([r for r in registered_riders if r.get("is_beta_rider")])
    total_pending = len([r for r in registered_riders if r.get("beta_status") == "pending"])
    
    sorted_spots = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:15]
    top_spots = []
    total_views = sum(totals.values()) or 1
    
    for s_name, count in sorted_spots:
        latest = next((v for v in views if v.get("spot_name") == s_name), {})
        top_spots.append({
            "spot_name": s_name,
            "views": count,
            "share_pct": round((count / total_views) * 100, 1),
            "lat": latest.get("lat"),
            "lon": latest.get("lon"),
            "last_viewed": latest.get("timestamp")
        })
        
    clean_nats = {k: v for k, v in nat_totals.items() if k and k != "Undefined"}
    sorted_nats = sorted((clean_nats or nat_totals).items(), key=lambda x: x[1], reverse=True)[:10]
    total_nats = sum(nat_totals.values()) or 1
    top_nationalities = [
        {
            "nationality": nat,
            "count": cnt,
            "pct": round((cnt / total_nats) * 100, 1)
        }
        for nat, cnt in sorted_nats
    ]
    
    top_searches = [
        {"query": q.title(), "count": cnt}
        for q, cnt in sorted(s_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    # Kite Travel Demand & Monetization Signals
    travel_inquiries = data.get("travel_inquiries", [])
    travel_dests = data.get("travel_destinations", {})
    travel_gaps = data.get("travel_gear_gaps", {})
    
    top_travel_destinations = [
        {"destination": d, "count": cnt}
        for d, cnt in sorted(travel_dests.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    top_gear_gaps = [
        {"size": f"{sz}m Kite", "count": cnt}
        for sz, cnt in sorted(travel_gaps.items(), key=lambda x: x[1], reverse=True)[:8]
    ]
    
    return {
        "summary": {
            "total_views": sum(totals.values()),
            "total_unique_spots": len(totals),
            "total_registered_riders": len(registered_riders),
            "total_beta_riders": total_beta,
            "total_pending_beta": total_pending,
            "total_riders_tracked": len(set(v.get("email") for v in views if v.get("email") and v.get("email") != "anonymous")),
            "total_searches": sum(s_totals.values()),
            "total_travel_inquiries": len(travel_inquiries),
            "total_feedback": len(users_db.get("feedback", []))
        },
        "registered_riders": registered_riders,
        "feedback": users_db.get("feedback", []),
        "top_spots": top_spots,
        "top_nationalities": top_nationalities,
        "recent_views": views[:30],
        "top_searches": top_searches,
        "spot_by_nationality": data.get("spot_by_nationality", {}),
        "travel_intelligence": {
            "total_travel_inquiries": len(travel_inquiries),
            "top_destinations": top_travel_destinations,
            "top_gear_gaps": top_gear_gaps,
            "recent_travel_inquiries": travel_inquiries[:25]
        }
    }
