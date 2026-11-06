"""
HolyGust Kite Travel Climatology & Quiver Optimization Engine
Provides 12-month historical atmospheric climatology, wind probabilities,
water/thermal protection guides, and personalized quiver packing recommendations.
"""

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

TRAVEL_SPOTS = [
    {
        "id": "cabarete",
        "name": "Cabarete (Kite Beach), Dominican Republic",
        "short_name": "Cabarete",
        "country": "Dominican Republic",
        "country_code": "DO",
        "flag": "🇩🇴",
        "region": "Puerto Plata",
        "lat": 19.75,
        "lon": -70.4167,
        "style_tags": ["Waves Outside", "Chop / Jump", "Thermal Trade", "Warm Water"],
        "prime_season": "June – August & December – March",
        "water_type": "Chop inside with 1–2m reef wave break on outer reef",
        "months": {
            1: {"wind_prob": 72, "avg_kts": 18, "range": [15, 23], "season": "peak", "sea_temp": 26, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Winter trade winds reinforced by north swells. Prime wave riding on outer reef."},
            2: {"wind_prob": 76, "avg_kts": 19, "range": [16, 24], "season": "peak", "sea_temp": 26, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Consistent easterly trades. Wind builds at 13:00 and blows until sunset."},
            3: {"wind_prob": 78, "avg_kts": 20, "range": [16, 25], "season": "peak", "sea_temp": 26, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Peak winter season with warm tropical sea and active thermal afternoon boost."},
            4: {"wind_prob": 70, "avg_kts": 18, "range": [14, 22], "season": "shoulder", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Spring transition. Moderate trades, perfect for 9m to 12m kites."},
            5: {"wind_prob": 65, "avg_kts": 17, "range": [14, 21], "season": "shoulder", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Pleasant uncrowded sessions with reliable 15-20 kt afternoons."},
            6: {"wind_prob": 84, "avg_kts": 21, "range": [17, 26], "season": "peak", "sea_temp": 28, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Summer trade winds at full strength. Afternoon thermal supercharger kicks in."},
            7: {"wind_prob": 90, "avg_kts": 22, "range": [18, 27], "season": "peak", "sea_temp": 28, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Windiest month of the year! 90% rideable days, consistent 18-26 kts every afternoon."},
            8: {"wind_prob": 84, "avg_kts": 20, "range": [17, 25], "season": "peak", "sea_temp": 29, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Strong trade winds and ultra-warm water. Ideal for 7m to 9m kites."},
            9: {"wind_prob": 62, "avg_kts": 16, "range": [13, 20], "season": "shoulder", "sea_temp": 29, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Late summer lull. Good foil/freeride conditions with occasional stronger days."},
            10: {"wind_prob": 48, "avg_kts": 14, "range": [12, 18], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Rainy transition month. Variable wind, pack big gear if visiting."},
            11: {"wind_prob": 58, "avg_kts": 16, "range": [13, 21], "season": "shoulder", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Winter trades return. Great uncrowded waves with early winter swells."},
            12: {"wind_prob": 68, "avg_kts": 18, "range": [15, 23], "season": "peak", "sea_temp": 27, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Christmas winds begin! Energetic atmosphere and steady side-onshore breeze."}
        }
    },
    {
        "id": "las_terrenas",
        "name": "Las Terrenas (Playa Portillo & Bonita), Dominican Republic",
        "short_name": "Las Terrenas",
        "country": "Dominican Republic",
        "country_code": "DO",
        "flag": "🇩🇴",
        "region": "Samaná",
        "lat": 19.32,
        "lon": -69.53,
        "style_tags": ["Flat Water", "Palm Lagoon", "Freeride / Foil", "Warm Water"],
        "prime_season": "December – April & June – August",
        "water_type": "Crystal flat water inside fringing reef, turquoise Caribbean paradise",
        "months": {
            1: {"wind_prob": 70, "avg_kts": 17, "range": [14, 21], "season": "peak", "sea_temp": 26, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Lush tropical scenery. Thermal trade winds pick up by noon."},
            2: {"wind_prob": 74, "avg_kts": 18, "range": [14, 22], "season": "peak", "sea_temp": 26, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Steady easterly breeze, butter-flat water behind the reef."},
            3: {"wind_prob": 75, "avg_kts": 18, "range": [14, 23], "season": "peak", "sea_temp": 26, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Excellent conditions for freeride and strapless cruising."},
            4: {"wind_prob": 68, "avg_kts": 17, "range": [13, 21], "season": "shoulder", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Warm and breezy afternoons, 10m-12m kites ideal."},
            5: {"wind_prob": 60, "avg_kts": 15, "range": [12, 19], "season": "shoulder", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Milder spring trade breeze, great for foiling."},
            6: {"wind_prob": 78, "avg_kts": 19, "range": [15, 23], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Summer trade winds return with warm Caribbean sun."},
            7: {"wind_prob": 82, "avg_kts": 20, "range": [16, 24], "season": "peak", "sea_temp": 28, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Peak summer wind month. 82% rideable days, 9m-11m kites."},
            8: {"wind_prob": 76, "avg_kts": 18, "range": [15, 22], "season": "peak", "sea_temp": 29, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Warm tropical breezes and scenic coconut grove backdrop."},
            9: {"wind_prob": 55, "avg_kts": 14, "range": [11, 18], "season": "low", "sea_temp": 29, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Light wind season, perfect for foil or SUP."},
            10: {"wind_prob": 45, "avg_kts": 13, "range": [10, 17], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Off-season tropical rains."},
            11: {"wind_prob": 55, "avg_kts": 15, "range": [12, 19], "season": "shoulder", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Early winter trades start trickling in."},
            12: {"wind_prob": 68, "avg_kts": 17, "range": [14, 21], "season": "peak", "sea_temp": 27, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Christmas holidays in Caribbean paradise."}
        }
    },
    {
        "id": "cumbuco",
        "name": "Cumbuco, Brazil",
        "short_name": "Cumbuco",
        "country": "Brazil",
        "country_code": "BR",
        "flag": "🇧🇷",
        "region": "Ceará",
        "lat": -3.6247,
        "lon": -38.7297,
        "style_tags": ["Flat Lagoons", "Chop", "Big Air", "Warm Water"],
        "prime_season": "July – December",
        "water_type": "Shorebreak & rolling chop on ocean, butter-flat Cauipe lagoon",
        "months": {
            1: {"wind_prob": 45, "avg_kts": 15, "range": [13, 19], "season": "low", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Rainy season starts. Light breeze, best for 12m-14m kites or foil."},
            2: {"wind_prob": 30, "avg_kts": 14, "range": [11, 17], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Wet season peak, light and unstable winds."},
            3: {"wind_prob": 25, "avg_kts": 13, "range": [10, 16], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Tropical rain periods, low wind consistency."},
            4: {"wind_prob": 20, "avg_kts": 13, "range": [10, 16], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Off-season. Light wind and rains."},
            5: {"wind_prob": 35, "avg_kts": 15, "range": [12, 19], "season": "low", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Rainy season ends, first winter trade days appear."},
            6: {"wind_prob": 68, "avg_kts": 18, "range": [15, 22], "season": "shoulder", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Trades arrive. Consistent 16-22 kts, lagoons fill up."},
            7: {"wind_prob": 88, "avg_kts": 21, "range": [17, 26], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Prime season kicks off. Daily 18-25 kts like clockwork from 10:00."},
            8: {"wind_prob": 94, "avg_kts": 23, "range": [18, 28], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Ultra-reliable trade winds. Peak season, 7m to 9m kites every day."},
            9: {"wind_prob": 96, "avg_kts": 24, "range": [19, 29], "season": "peak", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Peak wind machine! 96% rideable days, strong and smooth side-onshore trades."},
            10: {"wind_prob": 96, "avg_kts": 24, "range": [19, 30], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "The windiest month in Ceará. 7m kites are the daily standard."},
            11: {"wind_prob": 94, "avg_kts": 22, "range": [18, 27], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Consistent steady wind all day, ideal for long downwinders."},
            12: {"wind_prob": 85, "avg_kts": 19, "range": [16, 24], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Warm sunny holidays with reliable 17-23 kts."}
        }
    },
    {
        "id": "taiba",
        "name": "Taíba, Brazil",
        "short_name": "Taíba",
        "country": "Brazil",
        "country_code": "BR",
        "flag": "🇧🇷",
        "region": "Ceará",
        "lat": -3.5042,
        "lon": -38.8953,
        "style_tags": ["Butter Flat Lagoon", "Ocean Waves", "Freestyle", "Warm Water"],
        "prime_season": "July – December",
        "water_type": "World-famous flat lagoon inside, clean wave kickers at the secret wave spot",
        "months": {
            1: {"wind_prob": 50, "avg_kts": 16, "range": [13, 20], "season": "shoulder", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Late season sessions on the lagoon."},
            2: {"wind_prob": 30, "avg_kts": 14, "range": [11, 17], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Rainy season."},
            3: {"wind_prob": 25, "avg_kts": 13, "range": [10, 16], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Wet season."},
            4: {"wind_prob": 20, "avg_kts": 12, "range": [10, 15], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Low season."},
            5: {"wind_prob": 35, "avg_kts": 15, "range": [12, 19], "season": "low", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Rains subside."},
            6: {"wind_prob": 70, "avg_kts": 18, "range": [15, 23], "season": "shoulder", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Trades arrive. Taíba lagoon fills up."},
            7: {"wind_prob": 90, "avg_kts": 22, "range": [18, 27], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Pro freestyle training season kicks off. 8m-9m kites."},
            8: {"wind_prob": 95, "avg_kts": 24, "range": [19, 29], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Epic conditions. Super smooth lagoon and wave point."},
            9: {"wind_prob": 96, "avg_kts": 25, "range": [20, 30], "season": "peak", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Peak wind machine. 7m to 9m daily."},
            10: {"wind_prob": 96, "avg_kts": 25, "range": [20, 30], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Windiest month. Perfect for freestyle pop."},
            11: {"wind_prob": 94, "avg_kts": 23, "range": [18, 28], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Consistent steady trade winds."},
            12: {"wind_prob": 85, "avg_kts": 20, "range": [16, 25], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Holiday season, warm water."}
        }
    },
    {
        "id": "guajiru",
        "name": "Ilha do Guajirú, Brazil",
        "short_name": "Ilha do Guajirú",
        "country": "Brazil",
        "country_code": "BR",
        "flag": "🇧🇷",
        "region": "Ceará",
        "lat": -2.9833,
        "lon": -40.1167,
        "style_tags": ["Butter Flat Lagoon", "Freestyle", "Downwind", "Warm Water"],
        "prime_season": "July – January",
        "water_type": "Super shallow mirror-flat lagoon at mid-high tide",
        "months": {
            1: {"wind_prob": 65, "avg_kts": 17, "range": [14, 22], "season": "shoulder", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Late season trades, warm lagoon, uncrowded."},
            2: {"wind_prob": 35, "avg_kts": 14, "range": [11, 18], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Low season rains."},
            3: {"wind_prob": 25, "avg_kts": 13, "range": [10, 16], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Wet season."},
            4: {"wind_prob": 20, "avg_kts": 12, "range": [10, 15], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Off season."},
            5: {"wind_prob": 35, "avg_kts": 15, "range": [12, 19], "season": "low", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Start of transition."},
            6: {"wind_prob": 72, "avg_kts": 19, "range": [15, 24], "season": "shoulder", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Trades begin, mirror flat lagoon conditions."},
            7: {"wind_prob": 90, "avg_kts": 22, "range": [18, 27], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Freestyle heaven. Check tide table for mid-to-high tide."},
            8: {"wind_prob": 95, "avg_kts": 24, "range": [19, 29], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Rock solid wind all day long. 7m to 9m kites."},
            9: {"wind_prob": 98, "avg_kts": 25, "range": [20, 31], "season": "peak", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "One of the most reliable kite spots on Earth this month."},
            10: {"wind_prob": 98, "avg_kts": 26, "range": [21, 32], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Strongest wind month. 6m-8m kites recommended."},
            11: {"wind_prob": 95, "avg_kts": 24, "range": [19, 29], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Non-stop wind, pristine flat water."},
            12: {"wind_prob": 88, "avg_kts": 20, "range": [16, 25], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Warm tropical sessions, steady breezes."}
        }
    },
    {
        "id": "prea",
        "name": "Preá & Jericoacoara, Brazil",
        "short_name": "Preá / Jeri",
        "country": "Brazil",
        "country_code": "BR",
        "flag": "🇧🇷",
        "region": "Ceará",
        "lat": -2.8139,
        "lon": -40.4189,
        "style_tags": ["Big Air", "Wave / Chop", "Strapless", "Strong Wind"],
        "prime_season": "July – January",
        "water_type": "Rolling chop & wave kickers, heavy venturi wind",
        "months": {
            1: {"wind_prob": 60, "avg_kts": 18, "range": [14, 23], "season": "shoulder", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Late season big air."},
            2: {"wind_prob": 30, "avg_kts": 13, "range": [10, 17], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Wet season."},
            3: {"wind_prob": 25, "avg_kts": 12, "range": [10, 16], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Wet season."},
            4: {"wind_prob": 20, "avg_kts": 12, "range": [10, 15], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Low season."},
            5: {"wind_prob": 35, "avg_kts": 15, "range": [12, 19], "season": "low", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Pre-season."},
            6: {"wind_prob": 70, "avg_kts": 20, "range": [16, 25], "season": "shoulder", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Wind returns early here due to coastal dune geometry."},
            7: {"wind_prob": 90, "avg_kts": 24, "range": [19, 29], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Big air kicks off. Pack 7m and 8m."},
            8: {"wind_prob": 96, "avg_kts": 26, "range": [21, 32], "season": "peak", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Very strong wind. Downwind to Jeri is world-class."},
            9: {"wind_prob": 98, "avg_kts": 28, "range": [22, 35], "season": "peak", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Nuking wind! Daily 25-32 kts, 6m to 8m kites required."},
            10: {"wind_prob": 98, "avg_kts": 28, "range": [22, 35], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Heavy wind, epic kickers for twintip big air and strapless."},
            11: {"wind_prob": 95, "avg_kts": 25, "range": [20, 31], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Still very strong and consistent all afternoon."},
            12: {"wind_prob": 85, "avg_kts": 22, "range": [17, 27], "season": "peak", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Great holiday riding, vibrant Jericoacoara atmosphere."}
        }
    },
    {
        "id": "tarifa",
        "name": "Tarifa (Valdevaqueros & Los Lances), Spain",
        "short_name": "Tarifa",
        "country": "Spain",
        "country_code": "ES",
        "flag": "🇪🇸",
        "region": "Andalusia",
        "lat": 36.0143,
        "lon": -5.6044,
        "style_tags": ["Big Air", "Levante / Poniente", "Waves / Strapless", "Chop"],
        "prime_season": "April – October",
        "water_type": "Chop with swell on Poniente, flat/offshore on Levante",
        "months": {
            1: {"wind_prob": 55, "avg_kts": 17, "range": [13, 25], "season": "low", "sea_temp": 16, "air_temp": 15, "wetsuit": "4/3mm Steamer", "tip": "Winter storms. Poniente brings solid wave swells, cool water."},
            2: {"wind_prob": 60, "avg_kts": 18, "range": [14, 27], "season": "low", "sea_temp": 15, "air_temp": 16, "wetsuit": "4/3mm Steamer", "tip": "Uncrowded, active winter low pressure fronts."},
            3: {"wind_prob": 65, "avg_kts": 19, "range": [14, 28], "season": "shoulder", "sea_temp": 15, "air_temp": 17, "wetsuit": "4/3mm Steamer", "tip": "Spring awakens, first warm Levante days."},
            4: {"wind_prob": 72, "avg_kts": 20, "range": [15, 30], "season": "peak", "sea_temp": 16, "air_temp": 19, "wetsuit": "3/2mm Steamer", "tip": "Great spring conditions, mix of Poniente and Levante."},
            5: {"wind_prob": 76, "avg_kts": 21, "range": [16, 32], "season": "peak", "sea_temp": 17, "air_temp": 22, "wetsuit": "3/2mm or Shorty", "tip": "Warm sunny days, Levante can blow 30+ kts."},
            6: {"wind_prob": 82, "avg_kts": 22, "range": [16, 34], "season": "peak", "sea_temp": 19, "air_temp": 25, "wetsuit": "Shorty / 2mm", "tip": "Summer vibe kicks in, Valdevaqueros thermal boost."},
            7: {"wind_prob": 88, "avg_kts": 23, "range": [16, 38], "season": "peak", "sea_temp": 20, "air_temp": 28, "wetsuit": "Shorty / Boardshorts", "tip": "Peak summer. Heavy Levante can reach 40 kts, pack a 6m-7m!"},
            8: {"wind_prob": 88, "avg_kts": 23, "range": [16, 36], "season": "peak", "sea_temp": 21, "air_temp": 28, "wetsuit": "Shorty / Boardshorts", "tip": "Busy town, daily wind. Valdevaqueros is the epicenter."},
            9: {"wind_prob": 78, "avg_kts": 20, "range": [15, 30], "season": "peak", "sea_temp": 21, "air_temp": 26, "wetsuit": "3/2mm Steamer", "tip": "Best month of the year! Less crowds, warm sea, superb wind."},
            10: {"wind_prob": 70, "avg_kts": 19, "range": [14, 28], "season": "shoulder", "sea_temp": 19, "air_temp": 22, "wetsuit": "3/2mm Steamer", "tip": "Autumn swells arrive, great for strapless wave riding."},
            11: {"wind_prob": 60, "avg_kts": 18, "range": [14, 26], "season": "low", "sea_temp": 18, "air_temp": 18, "wetsuit": "4/3mm Steamer", "tip": "Winter rains begin, uncrowded beaches."},
            12: {"wind_prob": 55, "avg_kts": 17, "range": [13, 25], "season": "low", "sea_temp": 16, "air_temp": 16, "wetsuit": "4/3mm Steamer", "tip": "Quiet holiday sessions on Poniente waves."}
        }
    },
    {
        "id": "fuerteventura",
        "name": "Fuerteventura (Sotavento & Flag Beach), Spain",
        "short_name": "Fuerteventura",
        "country": "Spain",
        "country_code": "ES",
        "flag": "🇪🇸",
        "region": "Canary Islands",
        "lat": 28.1333,
        "lon": -14.2833,
        "style_tags": ["Tidal Lagoon", "Big Air", "Speed", "Trade Winds"],
        "prime_season": "May – September",
        "water_type": "Tidal lagoon at Sotavento (check tide table) and open sea chop",
        "months": {
            1: {"wind_prob": 55, "avg_kts": 16, "range": [13, 22], "season": "low", "sea_temp": 19, "air_temp": 20, "wetsuit": "3/2mm Steamer", "tip": "Warm European winter escape."},
            2: {"wind_prob": 60, "avg_kts": 17, "range": [14, 23], "season": "low", "sea_temp": 18, "air_temp": 21, "wetsuit": "3/2mm Steamer", "tip": "Moderate trade winds."},
            3: {"wind_prob": 68, "avg_kts": 18, "range": [14, 24], "season": "shoulder", "sea_temp": 18, "air_temp": 22, "wetsuit": "3/2mm Steamer", "tip": "Spring trade winds strengthening."},
            4: {"wind_prob": 74, "avg_kts": 20, "range": [15, 26], "season": "shoulder", "sea_temp": 19, "air_temp": 23, "wetsuit": "3/2mm Steamer", "tip": "Start of strong wind season."},
            5: {"wind_prob": 82, "avg_kts": 22, "range": [17, 28], "season": "peak", "sea_temp": 20, "air_temp": 24, "wetsuit": "Shorty / 2mm", "tip": "High season kicks off. Sotavento accelerates through valley."},
            6: {"wind_prob": 88, "avg_kts": 24, "range": [18, 32], "season": "peak", "sea_temp": 21, "air_temp": 26, "wetsuit": "Shorty", "tip": "Strong trades. 7m to 9m kites."},
            7: {"wind_prob": 92, "avg_kts": 26, "range": [20, 35], "season": "peak", "sea_temp": 22, "air_temp": 28, "wetsuit": "Shorty / Boardshorts", "tip": "Windiest month. PWA World Cup season, very strong offshore gusts."},
            8: {"wind_prob": 90, "avg_kts": 25, "range": [19, 33], "season": "peak", "sea_temp": 23, "air_temp": 28, "wetsuit": "Shorty / Boardshorts", "tip": "Peak season, warm water."},
            9: {"wind_prob": 75, "avg_kts": 20, "range": [15, 26], "season": "shoulder", "sea_temp": 23, "air_temp": 27, "wetsuit": "Shorty", "tip": "Milder trades, pleasant and uncrowded."},
            10: {"wind_prob": 62, "avg_kts": 17, "range": [13, 23], "season": "shoulder", "sea_temp": 22, "air_temp": 25, "wetsuit": "3/2mm Steamer", "tip": "Good autumn waves on north shore."},
            11: {"wind_prob": 55, "avg_kts": 16, "range": [13, 22], "season": "low", "sea_temp": 21, "air_temp": 23, "wetsuit": "3/2mm Steamer", "tip": "Milder breezes."},
            12: {"wind_prob": 52, "avg_kts": 15, "range": [12, 21], "season": "low", "sea_temp": 20, "air_temp": 21, "wetsuit": "3/2mm Steamer", "tip": "Winter sun escape."}
        }
    },
    {
        "id": "dakhla",
        "name": "Dakhla (Lagoon & Speed Spot), Morocco",
        "short_name": "Dakhla",
        "country": "Morocco",
        "country_code": "MA",
        "flag": "🇲🇦",
        "region": "Western Sahara",
        "lat": 23.7167,
        "lon": -15.9333,
        "style_tags": ["Flat Water", "Freestyle", "Speed Spot", "Desert Thermal"],
        "prime_season": "April – September",
        "water_type": "Mirror flat inside lagoon, ocean wave spots on West coast",
        "months": {
            1: {"wind_prob": 60, "avg_kts": 17, "range": [14, 22], "season": "shoulder", "sea_temp": 18, "air_temp": 21, "wetsuit": "3/2mm Steamer", "tip": "Pleasant winter escape from Europe, mild desert wind."},
            2: {"wind_prob": 68, "avg_kts": 18, "range": [15, 23], "season": "shoulder", "sea_temp": 18, "air_temp": 22, "wetsuit": "3/2mm Steamer", "tip": "Trade winds begin to strengthen."},
            3: {"wind_prob": 75, "avg_kts": 20, "range": [16, 25], "season": "shoulder", "sea_temp": 18, "air_temp": 23, "wetsuit": "3/2mm Steamer", "tip": "Spring thermal builds, very reliable afternoons."},
            4: {"wind_prob": 82, "avg_kts": 22, "range": [17, 27], "season": "peak", "sea_temp": 19, "air_temp": 24, "wetsuit": "3/2mm Steamer", "tip": "High season starts. Daily 20+ kts on the lagoon."},
            5: {"wind_prob": 88, "avg_kts": 24, "range": [19, 29], "season": "peak", "sea_temp": 19, "air_temp": 25, "wetsuit": "3/2mm or Shorty", "tip": "Consistent strong winds. Speed spot is firing."},
            6: {"wind_prob": 92, "avg_kts": 25, "range": [20, 31], "season": "peak", "sea_temp": 20, "air_temp": 26, "wetsuit": "Shorty / 2mm", "tip": "Non-stop wind day and night. 7m to 9m kites."},
            7: {"wind_prob": 95, "avg_kts": 26, "range": [21, 33], "season": "peak", "sea_temp": 21, "air_temp": 27, "wetsuit": "Shorty", "tip": "Windiest month in Dakhla. Ultra-reliable desert thermal machine."},
            8: {"wind_prob": 94, "avg_kts": 25, "range": [20, 31], "season": "peak", "sea_temp": 21, "air_temp": 27, "wetsuit": "Shorty", "tip": "Peak summer wind, mirror flat Speed Spot."},
            9: {"wind_prob": 86, "avg_kts": 22, "range": [17, 27], "season": "peak", "sea_temp": 21, "air_temp": 27, "wetsuit": "3/2mm Steamer", "tip": "Warm days, steady breezes, fewer crowds."},
            10: {"wind_prob": 74, "avg_kts": 19, "range": [15, 24], "season": "shoulder", "sea_temp": 20, "air_temp": 26, "wetsuit": "3/2mm Steamer", "tip": "Autumn trade winds, great freeride conditions."},
            11: {"wind_prob": 65, "avg_kts": 18, "range": [14, 22], "season": "shoulder", "sea_temp": 19, "air_temp": 23, "wetsuit": "3/2mm Steamer", "tip": "Good winter destination, comfortable temperatures."},
            12: {"wind_prob": 60, "avg_kts": 17, "range": [14, 21], "season": "shoulder", "sea_temp": 18, "air_temp": 21, "wetsuit": "3/2mm Steamer", "tip": "Solid holiday wind, flat water sessions."}
        }
    },
    {
        "id": "cape_town",
        "name": "Cape Town (Blouberg / Kite Beach), South Africa",
        "short_name": "Cape Town",
        "country": "South Africa",
        "country_code": "ZA",
        "flag": "🇿🇦",
        "region": "Western Cape",
        "lat": -33.8,
        "lon": 18.4667,
        "style_tags": ["Big Air Capital", "Mega Waves", "Cape Doctor", "Cold Water"],
        "prime_season": "November – March",
        "water_type": "Clean ocean waves and ramps, cold Atlantic Benguela current",
        "months": {
            1: {"wind_prob": 90, "avg_kts": 26, "range": [20, 38], "season": "peak", "sea_temp": 13, "air_temp": 26, "wetsuit": "4/3mm Steamer + Booties", "tip": "King of the Air season! The Cape Doctor blows 30-40 kts in the afternoon. Pack a 6m-7m kite."},
            2: {"wind_prob": 86, "avg_kts": 25, "range": [19, 36], "season": "peak", "sea_temp": 14, "air_temp": 26, "wetsuit": "4/3mm Steamer", "tip": "Sensational big air and strapless waves at Sunset Beach and Big Bay."},
            3: {"wind_prob": 74, "avg_kts": 21, "range": [16, 30], "season": "shoulder", "sea_temp": 14, "air_temp": 24, "wetsuit": "4/3mm Steamer", "tip": "Late summer, slightly softer wind but excellent wave conditions."},
            4: {"wind_prob": 50, "avg_kts": 17, "range": [13, 24], "season": "low", "sea_temp": 14, "air_temp": 22, "wetsuit": "4/3mm Steamer", "tip": "Autumn transition, Cape Doctor fades."},
            5: {"wind_prob": 35, "avg_kts": 15, "range": [11, 22], "season": "low", "sea_temp": 14, "air_temp": 19, "wetsuit": "5/4mm Steamer", "tip": "Winter approaches with frontal storms."},
            6: {"wind_prob": 30, "avg_kts": 15, "range": [11, 24], "season": "low", "sea_temp": 14, "air_temp": 18, "wetsuit": "5/4mm Steamer", "tip": "Cold winter, large swells for surfing."},
            7: {"wind_prob": 30, "avg_kts": 15, "range": [11, 24], "season": "low", "sea_temp": 13, "air_temp": 17, "wetsuit": "5/4mm Steamer", "tip": "Winter lows, sporadic stormy winds."},
            8: {"wind_prob": 35, "avg_kts": 16, "range": [12, 25], "season": "low", "sea_temp": 13, "air_temp": 18, "wetsuit": "5/4mm Steamer", "tip": "Late winter, whale watching season."},
            9: {"wind_prob": 55, "avg_kts": 19, "range": [14, 27], "season": "shoulder", "sea_temp": 13, "air_temp": 20, "wetsuit": "4/3mm Steamer", "tip": "Spring awakening, first south-easterly breezes."},
            10: {"wind_prob": 72, "avg_kts": 22, "range": [16, 32], "season": "shoulder", "sea_temp": 13, "air_temp": 22, "wetsuit": "4/3mm Steamer", "tip": "Cape Doctor returns! Great uncrowded waves."},
            11: {"wind_prob": 84, "avg_kts": 24, "range": [18, 35], "season": "peak", "sea_temp": 13, "air_temp": 24, "wetsuit": "4/3mm Steamer", "tip": "High season starts, strong afternoon wind every day."},
            12: {"wind_prob": 88, "avg_kts": 25, "range": [19, 38], "season": "peak", "sea_temp": 13, "air_temp": 25, "wetsuit": "4/3mm Steamer", "tip": "Summer holiday rush, legendary 30+ kt sessions."}
        }
    },
    {
        "id": "el_gouna",
        "name": "El Gouna & Soma Bay, Egypt",
        "short_name": "El Gouna / Soma Bay",
        "country": "Egypt",
        "country_code": "EG",
        "flag": "🇪🇬",
        "region": "Red Sea",
        "lat": 27.3942,
        "lon": 33.6782,
        "style_tags": ["Shallow Sandbanks", "Butter Flat", "Freeride", "Warm Water"],
        "prime_season": "April – October",
        "water_type": "Tidal sandbanks, crystal clear turquoise flat water",
        "months": {
            1: {"wind_prob": 50, "avg_kts": 15, "range": [12, 20], "season": "low", "sea_temp": 21, "air_temp": 22, "wetsuit": "4/3mm Steamer", "tip": "Winter lull, cool mornings, 12m-14m kites."},
            2: {"wind_prob": 58, "avg_kts": 17, "range": [13, 22], "season": "shoulder", "sea_temp": 21, "air_temp": 23, "wetsuit": "3/2mm Steamer", "tip": "Wind picks up, uncrowded sandbanks."},
            3: {"wind_prob": 68, "avg_kts": 18, "range": [14, 23], "season": "shoulder", "sea_temp": 22, "air_temp": 25, "wetsuit": "3/2mm Steamer", "tip": "Spring season begins, warming air and water."},
            4: {"wind_prob": 76, "avg_kts": 19, "range": [15, 25], "season": "peak", "sea_temp": 23, "air_temp": 28, "wetsuit": "Shorty / 2mm", "tip": "High season starts, reliable northerly trades."},
            5: {"wind_prob": 82, "avg_kts": 21, "range": [16, 26], "season": "peak", "sea_temp": 25, "air_temp": 31, "wetsuit": "Shorty / Boardshorts", "tip": "Prime conditions, flat lagoon at high tide."},
            6: {"wind_prob": 88, "avg_kts": 22, "range": [17, 27], "season": "peak", "sea_temp": 27, "air_temp": 34, "wetsuit": "Boardshorts & Lycra", "tip": "Hot summer trades, crystal clear water, daily 18-24 kts."},
            7: {"wind_prob": 90, "avg_kts": 23, "range": [17, 28], "season": "peak", "sea_temp": 28, "air_temp": 36, "wetsuit": "Boardshorts & Lycra", "tip": "Most consistent month of the year. Wear sun protection."},
            8: {"wind_prob": 90, "avg_kts": 23, "range": [17, 27], "season": "peak", "sea_temp": 29, "air_temp": 36, "wetsuit": "Boardshorts & Lycra", "tip": "Steady warm winds, ideal for progression and freestyle."},
            9: {"wind_prob": 86, "avg_kts": 21, "range": [16, 26], "season": "peak", "sea_temp": 28, "air_temp": 33, "wetsuit": "Boardshorts & Lycra", "tip": "Peak season sweet spot: warm water and milder air."},
            10: {"wind_prob": 78, "avg_kts": 19, "range": [15, 24], "season": "peak", "sea_temp": 26, "air_temp": 29, "wetsuit": "Shorty / 2mm", "tip": "Comfortable autumn temperatures, reliable trades."},
            11: {"wind_prob": 62, "avg_kts": 16, "range": [13, 21], "season": "shoulder", "sea_temp": 24, "air_temp": 25, "wetsuit": "3/2mm Steamer", "tip": "Good autumn escape, occasional strong days."},
            12: {"wind_prob": 52, "avg_kts": 15, "range": [12, 20], "season": "low", "sea_temp": 22, "air_temp": 22, "wetsuit": "4/3mm Steamer", "tip": "Cooler water, pack 10m-14m kites."}
        }
    },
    {
        "id": "rhodes",
        "name": "Rhodes (Prasonisi), Greece",
        "short_name": "Prasonisi (Rhodes)",
        "country": "Greece",
        "country_code": "GR",
        "flag": "🇬🇷",
        "region": "South Aegean",
        "lat": 35.8833,
        "lon": 27.7667,
        "style_tags": ["Dual Spot: Waves & Flat", "Meltemi", "Freestyle", "Speed"],
        "prime_season": "June – September",
        "water_type": "One spit of sand: Flat offshore on Aegean side, waves on Mediterranean side!",
        "months": {
            1: {"wind_prob": 45, "avg_kts": 14, "range": [11, 20], "season": "low", "sea_temp": 17, "air_temp": 15, "wetsuit": "4/3mm Steamer", "tip": "Winter off-season."},
            2: {"wind_prob": 48, "avg_kts": 15, "range": [11, 21], "season": "low", "sea_temp": 16, "air_temp": 15, "wetsuit": "4/3mm Steamer", "tip": "Winter."},
            3: {"wind_prob": 55, "avg_kts": 16, "range": [12, 22], "season": "low", "sea_temp": 16, "air_temp": 17, "wetsuit": "4/3mm Steamer", "tip": "Spring breezes."},
            4: {"wind_prob": 62, "avg_kts": 17, "range": [13, 23], "season": "shoulder", "sea_temp": 18, "air_temp": 20, "wetsuit": "3/2mm Steamer", "tip": "Pre-season warming."},
            5: {"wind_prob": 72, "avg_kts": 19, "range": [15, 25], "season": "shoulder", "sea_temp": 20, "air_temp": 24, "wetsuit": "Shorty / 2mm", "tip": "Meltemi awakens."},
            6: {"wind_prob": 85, "avg_kts": 22, "range": [17, 28], "season": "peak", "sea_temp": 22, "air_temp": 28, "wetsuit": "Shorty / Boardshorts", "tip": "Meltemi season kicks in full force. 18-25 kts daily."},
            7: {"wind_prob": 92, "avg_kts": 25, "range": [19, 32], "season": "peak", "sea_temp": 24, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Peak Meltemi! Heavy venturi boost between island and mainland. 7m-9m."},
            8: {"wind_prob": 92, "avg_kts": 25, "range": [19, 32], "season": "peak", "sea_temp": 25, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Nuclear wind on the flat side, superb kickers on the wave side."},
            9: {"wind_prob": 80, "avg_kts": 20, "range": [16, 26], "season": "peak", "sea_temp": 25, "air_temp": 28, "wetsuit": "Shorty", "tip": "Warm sea, great end of summer Meltemi."},
            10: {"wind_prob": 58, "avg_kts": 16, "range": [12, 22], "season": "shoulder", "sea_temp": 23, "air_temp": 24, "wetsuit": "3/2mm Steamer", "tip": "Meltemi fades."},
            11: {"wind_prob": 45, "avg_kts": 14, "range": [11, 20], "season": "low", "sea_temp": 20, "air_temp": 19, "wetsuit": "3/2mm Steamer", "tip": "Autumn close."},
            12: {"wind_prob": 42, "avg_kts": 14, "range": [11, 19], "season": "low", "sea_temp": 18, "air_temp": 16, "wetsuit": "4/3mm Steamer", "tip": "Winter."}
        }
    },
    {
        "id": "salinas_del_rey",
        "name": "Salinas del Rey (Santa Verónica), Colombia",
        "short_name": "Salinas del Rey",
        "country": "Colombia",
        "country_code": "CO",
        "flag": "🇨🇴",
        "region": "Atlántico",
        "lat": 10.9,
        "lon": -75.0833,
        "style_tags": ["Clean Waves", "Big Air", "Caribbean Jet", "Warm Water"],
        "prime_season": "December – May",
        "water_type": "Clean ocean waves and point break, coastal jet stream",
        "months": {
            1: {"wind_prob": 90, "avg_kts": 24, "range": [18, 32], "season": "peak", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Caribbean low-level jet in full force. 20-30 kts every day. Pack 7m-9m."},
            2: {"wind_prob": 94, "avg_kts": 26, "range": [20, 34], "season": "peak", "sea_temp": 26, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Windiest month! GKA wave tour spot. Epic right-hand point break."},
            3: {"wind_prob": 92, "avg_kts": 25, "range": [19, 32], "season": "peak", "sea_temp": 26, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Solid and reliable strong trade winds all afternoon."},
            4: {"wind_prob": 82, "avg_kts": 21, "range": [16, 27], "season": "peak", "sea_temp": 27, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Strong trades continue, warm water."},
            5: {"wind_prob": 68, "avg_kts": 18, "range": [14, 23], "season": "shoulder", "sea_temp": 28, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Late season, lighter breezes."},
            6: {"wind_prob": 55, "avg_kts": 16, "range": [12, 21], "season": "shoulder", "sea_temp": 28, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Summer lull (Veranillo de San Juan)."},
            7: {"wind_prob": 65, "avg_kts": 17, "range": [13, 22], "season": "shoulder", "sea_temp": 28, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Short summer breeze window."},
            8: {"wind_prob": 50, "avg_kts": 14, "range": [11, 19], "season": "low", "sea_temp": 29, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Off-season rains."},
            9: {"wind_prob": 35, "avg_kts": 12, "range": [9, 16], "season": "low", "sea_temp": 29, "air_temp": 31, "wetsuit": "Boardshorts", "tip": "Low season."},
            10: {"wind_prob": 30, "avg_kts": 11, "range": [9, 15], "season": "low", "sea_temp": 29, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Low season rains."},
            11: {"wind_prob": 50, "avg_kts": 15, "range": [12, 20], "season": "shoulder", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Trades begin to awaken."},
            12: {"wind_prob": 80, "avg_kts": 22, "range": [17, 28], "season": "peak", "sea_temp": 27, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Season explodes! 20+ kts start from mid-December."}
        }
    },
    {
        "id": "le_morne",
        "name": "Le Morne (One Eye & Lagoon), Mauritius",
        "short_name": "Le Morne",
        "country": "Mauritius",
        "country_code": "MU",
        "flag": "🇲🇺",
        "region": "Black River",
        "lat": -20.45,
        "lon": 57.3167,
        "style_tags": ["World Class Waves", "One Eye", "Flat Lagoon", "Warm Water"],
        "prime_season": "May – October",
        "water_type": "Flat turquoise lagoon inside, legendary One Eye barrel on outer reef",
        "months": {
            1: {"wind_prob": 40, "avg_kts": 14, "range": [11, 18], "season": "low", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Summer cyclone season, light variable winds."},
            2: {"wind_prob": 35, "avg_kts": 13, "range": [10, 17], "season": "low", "sea_temp": 28, "air_temp": 30, "wetsuit": "Boardshorts", "tip": "Hot humid summer, low wind consistency."},
            3: {"wind_prob": 40, "avg_kts": 14, "range": [11, 18], "season": "low", "sea_temp": 28, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Transition period."},
            4: {"wind_prob": 55, "avg_kts": 16, "range": [13, 21], "season": "shoulder", "sea_temp": 27, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Winter south-east trades start arriving."},
            5: {"wind_prob": 70, "avg_kts": 18, "range": [15, 23], "season": "peak", "sea_temp": 26, "air_temp": 26, "wetsuit": "Shorty / Boardshorts", "tip": "Trade winds set in. Clean winter swells for One Eye."},
            6: {"wind_prob": 80, "avg_kts": 20, "range": [16, 25], "season": "peak", "sea_temp": 25, "air_temp": 25, "wetsuit": "Shorty / 2mm", "tip": "Prime wave season! Side-shore trades and massive swells."},
            7: {"wind_prob": 85, "avg_kts": 22, "range": [17, 27], "season": "peak", "sea_temp": 24, "air_temp": 24, "wetsuit": "Shorty / 2mm", "tip": "Windiest month. Consistent 18-25 kts on the lagoon and reef."},
            8: {"wind_prob": 85, "avg_kts": 22, "range": [17, 27], "season": "peak", "sea_temp": 24, "air_temp": 24, "wetsuit": "Shorty / 2mm", "tip": "World-class waves and solid lagoon trades."},
            9: {"wind_prob": 82, "avg_kts": 21, "range": [16, 26], "season": "peak", "sea_temp": 24, "air_temp": 25, "wetsuit": "Shorty / 2mm", "tip": "Very consistent trades, warmer air."},
            10: {"wind_prob": 75, "avg_kts": 19, "range": [15, 24], "season": "peak", "sea_temp": 25, "air_temp": 26, "wetsuit": "Boardshorts", "tip": "Late season sweet spot, warm water and steady wind."},
            11: {"wind_prob": 60, "avg_kts": 17, "range": [13, 21], "season": "shoulder", "sea_temp": 26, "air_temp": 28, "wetsuit": "Boardshorts", "tip": "Trades begin to slow down."},
            12: {"wind_prob": 45, "avg_kts": 15, "range": [12, 19], "season": "low", "sea_temp": 27, "air_temp": 29, "wetsuit": "Boardshorts", "tip": "Summer warmth, sporadic breezes."}
        }
    }
]

def get_all_travel_spots() -> list:
    """Returns directory of all travel destinations."""
    spots = []
    for s in TRAVEL_SPOTS:
        spots.append({
            "id": s["id"],
            "name": s["name"],
            "short_name": s["short_name"],
            "country": s["country"],
            "country_code": s["country_code"],
            "flag": s["flag"],
            "region": s["region"],
            "lat": s["lat"],
            "lon": s["lon"],
            "style_tags": s["style_tags"],
            "prime_season": s["prime_season"],
            "water_type": s["water_type"]
        })
    return spots

def get_spot_climatology(spot_id: str) -> dict:
    """Returns full 12-month climatology for a given spot."""
    clean_id = (spot_id or "").strip().lower()
    for s in TRAVEL_SPOTS:
        if s["id"] == clean_id or clean_id in s["short_name"].lower() or clean_id in s["name"].lower():
            return s
    return TRAVEL_SPOTS[0]

def explore_spots_by_month_and_style(month: int, style: str = "all") -> list:
    """
    Ranks global spots for a specific month (1-12) and preferred riding style.
    Returns sorted list from highest to lowest wind probability.
    """
    results = []
    clean_style = (style or "all").lower().strip()
    
    for s in TRAVEL_SPOTS:
        m_data = s["months"].get(month, s["months"][7])
        
        # Check style filter
        style_match = True
        if clean_style != "all":
            joined_tags = " ".join(s["style_tags"]).lower()
            if "wave" in clean_style and "wave" not in joined_tags and "strapless" not in joined_tags:
                style_match = False
            elif "flat" in clean_style and "flat" not in joined_tags:
                style_match = False
            elif "big air" in clean_style and "big air" not in joined_tags and "strong wind" not in joined_tags:
                style_match = False
            elif "warm" in clean_style and "warm" not in joined_tags and m_data["sea_temp"] < 24:
                style_match = False

        if style_match:
            results.append({
                "id": s["id"],
                "name": s["name"],
                "short_name": s["short_name"],
                "country": s["country"],
                "flag": s["flag"],
                "region": s["region"],
                "month_idx": month,
                "month_name": MONTH_NAMES[month - 1],
                "wind_prob": m_data["wind_prob"],
                "avg_kts": m_data["avg_kts"],
                "range": m_data["range"],
                "season": m_data["season"],
                "sea_temp": m_data["sea_temp"],
                "air_temp": m_data["air_temp"],
                "wetsuit": m_data["wetsuit"],
                "tip": m_data["tip"],
                "water_type": s["water_type"],
                "style_tags": s["style_tags"]
            })

    results.sort(key=lambda x: (x["wind_prob"], x["avg_kts"]), reverse=True)
    return results

def calculate_quiver_trip_recommendation(
    spot_id: str,
    month: int,
    rider_weight: float = 75.0,
    discipline: str = "Twintip",
    gear_inventory: list = None
) -> dict:
    spot = get_spot_climatology(spot_id)
    month_data = spot["months"].get(month, spot["months"][7])
    wind_min, wind_max = month_data["range"]
    avg_wind = month_data["avg_kts"]

    weight = float(rider_weight or 75.0)
    is_strapless = "surf" in (discipline or "").lower() or "strapless" in (discipline or "").lower()
    
    def ideal_kite_size(kts: float) -> float:
        base_size = 210.0 / max(kts, 10.0)
        scaled = base_size * ((weight / 75.0) ** 0.65)
        if is_strapless:
            scaled *= 0.85
        return max(4.0, min(17.0, round(scaled, 1)))

    ideal_for_max = round(ideal_kite_size(wind_max))
    ideal_for_avg = round(ideal_kite_size(avg_wind))
    ideal_for_min = round(ideal_kite_size(wind_min))

    kites = []
    if gear_inventory and isinstance(gear_inventory, list):
        for item in gear_inventory:
            if isinstance(item, dict) and item.get("category", "kite") == "kite":
                try:
                    sz = float(item.get("size", 0))
                    if sz > 0:
                        kites.append({
                            "brand": item.get("brand", "Kite"),
                            "model": item.get("model", ""),
                            "size": sz,
                            "active": item.get("active", True),
                            "label": f"{item.get('brand', '')} {item.get('model', '')} {int(sz)}m".strip()
                        })
                except Exception:
                    pass

    kites.sort(key=lambda x: x["size"])

    packed = []
    leave_home = []
    gaps = []

    if not kites:
        gaps.append({
            "type": "no_kites",
            "size": ideal_for_avg,
            "title": f"Recommended Size: {ideal_for_avg}m & {ideal_for_max}m",
            "desc": f"For {spot['short_name']}'s {avg_wind} kt winds ({discipline}, {weight:.0f}kg), your core everyday kite is a {ideal_for_avg}m, paired with a {ideal_for_max}m for stronger sessions."
        })
    else:
        user_sizes = [k["size"] for k in kites]

        for k in kites:
            sz = k["size"]
            diff_to_avg = abs(sz - ideal_for_avg)
            diff_to_max = abs(sz - ideal_for_max)
            diff_to_min = abs(sz - ideal_for_min)

            if diff_to_avg <= 1.5 or diff_to_max <= 1.5 or diff_to_min <= 1.5:
                role = "Primary Daily Kite" if diff_to_avg <= 1.5 else ("High Wind Kite" if sz <= ideal_for_avg else "Light Wind Backup")
                packed.append({
                    **k,
                    "role": role,
                    "reason": f"Covers {int(max(10, 200/max(sz,1)))}–{int(250/max(sz,1))} kts bracket for your {weight:.0f}kg weight."
                })
            else:
                leave_home.append({
                    **k,
                    "reason": "Outside this destination's typical wind window. Save airline luggage weight!"
                })

        min_user_size = min(user_sizes)
        if min_user_size > (ideal_for_max + 1.5) and wind_max >= 25:
            rec_gap_size = int(ideal_for_max)
            gaps.append({
                "type": "high_wind_gap",
                "size": rec_gap_size,
                "suggested_size": rec_gap_size,
                "title": f"High-Wind Gap: Consider adding a {rec_gap_size}m kite",
                "desc": f"{spot['short_name']} regularly blows up to {wind_max} kts in {MONTH_NAMES[month-1]}. Your smallest kite is {int(min_user_size)}m, which will leave you overpowered on strong days.",
                "advice": f"{spot['short_name']} regularly blows up to {wind_max} kts in {MONTH_NAMES[month-1]}. Your smallest kite is {int(min_user_size)}m, which will leave you overpowered on strong days."
            })

        max_user_size = max(user_sizes)
        if max_user_size < (ideal_for_min - 1.5) and wind_min <= 16:
            rec_gap_size = int(ideal_for_min)
            gaps.append({
                "type": "light_wind_gap",
                "size": rec_gap_size,
                "suggested_size": rec_gap_size,
                "title": f"Light-Wind Gap: Consider adding a {rec_gap_size}m kite",
                "desc": f"Mornings in {spot['short_name']} can start at {wind_min} kts. Your largest kite is {int(max_user_size)}m. A {rec_gap_size}m ensures you never miss a day on the water.",
                "advice": f"Mornings in {spot['short_name']} can start at {wind_min} kts. Your largest kite is {int(max_user_size)}m. A {rec_gap_size}m ensures you never miss a day on the water."
            })

    return {
        "spot": {
            "id": spot["id"],
            "name": spot["name"],
            "short_name": spot["short_name"],
            "country": spot["country"],
            "flag": spot["flag"],
            "water_type": spot["water_type"],
            "style_tags": spot["style_tags"],
            "prime_season": spot["prime_season"]
        },
        "month": {
            "index": month,
            "name": MONTH_NAMES[month - 1],
            "wind_prob": month_data["wind_prob"],
            "avg_kts": month_data["avg_kts"],
            "range": month_data["range"],
            "season": month_data["season"],
            "sea_temp": month_data["sea_temp"],
            "air_temp": month_data["air_temp"],
            "wetsuit": month_data["wetsuit"],
            "tip": month_data["tip"]
        },
        "ideal_sizes": {
            "high_wind": ideal_for_max,
            "core_everyday": ideal_for_avg,
            "light_wind": ideal_for_min
        },
        "quiver_advice": {
            "pack": packed,
            "leave_home": leave_home,
            "gaps": gaps,
            "optimal_match": len(packed) >= 2 and len(gaps) == 0
        },
        "all_months": [
            {
                "month_idx": m,
                "month_name": MONTH_NAMES[m - 1][:3],
                "wind_prob": spot["months"][m]["wind_prob"],
                "avg_kts": spot["months"][m]["avg_kts"],
                "season": spot["months"][m]["season"],
                "sea_temp": spot["months"][m]["sea_temp"],
                "wetsuit": spot["months"][m]["wetsuit"]
            }
            for m in range(1, 13)
        ]
    }
