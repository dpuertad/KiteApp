# Kitesurf Morning Briefing Assistant - Setup & Cloud Guide

## 1. Credentials Verified & Active
- **Bot Username:** `@KiteForecast_bot`
- **Bot Display Name:** `KitesurfWeatherApp`
- **Bot Token:** `9295432294:AAFK0ZZz_Gww6ewx7D-YpbYTvfbHdU9ogyc`
- **Telegram Chat ID:** `7424865438`
- **Rider Weight:** 78 kg
- **Default Spot:** Cumbuco, Ceará, Brazil (Lat: -3.6247, Lon: -38.7297)
- **Active Quiver:**
  - Core XR8 7m (24 – 36 knots)
  - Core XR8 9m (17 – 27 knots)
  - Duotone Dice SLS 11m (14 – 22 knots)

---

## 2. Option A: Make.com Cloud Scenario (Zero-Maintenance)

To run this in the cloud on Make.com without needing any phone or computer on:

### Step 1: Create a New Scenario
1. Go to [Make.com](https://make.com) and click **Create a new scenario**.

### Step 2: Add Trigger (Schedule)
- Click the clock icon on the initial module:
  - **Run scenario:** At regular intervals (or Specific dates / Time of day)
  - **Time:** `07:00` (choose your local timezone)

### Step 3: Add HTTP Module ("Make a request")
- **URL:** 
  ```text
  https://api.open-meteo.com/v1/forecast?latitude=-3.6247&longitude=-38.7297&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=kn&timezone=America%2FFortaleza&forecast_days=1
  ```
- **Method:** `GET`
- **Parse response:** `Yes`

### Step 4: Add Telegram Bot Module ("Send a Text Message or a Reply")
- Connect your Telegram Bot using token: `9295432294:AAFK0ZZz_Gww6ewx7D-YpbYTvfbHdU9ogyc`
- **Chat ID:** `7424865438`
- **Parse Mode:** `Markdown`
- **Text Body:** (Use the formatted report with morning, midday, and afternoon wind readings).

---

## 3. Option B: GitHub Actions (100% Free Forever, No Limits)
You can also run `kitesurf_bot.py` via a free GitHub Actions cron workflow scheduled at 07:00 AM daily.

See `.github/workflows/morning_briefing.yml` in this repository.
