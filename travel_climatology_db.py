"""
travel_climatology_db.py
-------------------------
Kite Travel Climatology & Quiver Recommendation Database.
Contains 120+ world-class kitesurf destinations across 35+ countries,
with 12-month historical wind probabilities, wind ranges, thermal behavior,
sea/air temperatures, wetsuit guides, and optimal style tags.

Supports dynamic community spot expansion: when riders request a new destination,
the cloud auto-geocodes coordinates, computes 12-month ERA5 climatology,
and permanently adds it to the global catalog.
"""

import json
import os
import re
import urllib.request
import urllib.parse
import datetime

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

USER_SPOTS_FILE = os.path.join(os.path.dirname(__file__), "user_travel_spots.json")

CORE_TRAVEL_SPOTS = [
  {
    "id": "cumbuco",
    "name": "Cumbuco (Cauipe & Tabuba), Brazil",
    "short_name": "Cumbuco",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -3.624,
    "lon": -38.73,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Wave",
      "Downwind"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Chop, Ocean Waves & Flat Lagoons",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "taiba",
    "name": "Taíba (Lagoon & Secret Wave), Brazil",
    "short_name": "Taíba",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -3.508,
    "lon": -38.893,
    "style_tags": [
      "Freestyle",
      "Wave",
      "Flat Water"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Butter Flat Lagoon & Ocean Shorebreak",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "guajiru",
    "name": "Ilha do Guajirú (The Flatwater Sea), Brazil",
    "short_name": "Ilha do Guajirú",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -2.978,
    "lon": -39.907,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Speed"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Tidal Flatwater Estuary & Secret Lagoon",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "prea",
    "name": "Preá & Jericoacoara, Brazil",
    "short_name": "Preá & Jeri",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -2.812,
    "lon": -40.42,
    "style_tags": [
      "Big Air",
      "Wave",
      "Freeride",
      "Strapless"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Choppy Ocean & Rolling Swell (Strong Wind)",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "paracuru",
    "name": "Paracuru (Quebramar & Reef), Brazil",
    "short_name": "Paracuru",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -3.41,
    "lon": -39.03,
    "style_tags": [
      "Wave",
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Flat Water behind Reef at Low Tide & Outer Waves",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "barra_grande",
    "name": "Barra Grande (Piauí Lagoon), Brazil",
    "short_name": "Barra Grande",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Piauí",
    "lat": -2.915,
    "lon": -41.341,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Downwind"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Shallow River Lagoon & Sandspits",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "macapa",
    "name": "Macapá (Parnaíba Delta Flat), Brazil",
    "short_name": "Macapá",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Piauí",
    "lat": -2.906,
    "lon": -41.442,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Speed"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Ultra-Flat Tidal Sandbanks & Warm Estuary",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "atins",
    "name": "Atins & Lençóis Maranhenses, Brazil",
    "short_name": "Atins",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Maranhão",
    "lat": -2.571,
    "lon": -42.748,
    "style_tags": [
      "Freeride",
      "Flat Water",
      "Downwind"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Freshwater Dune Lagoons & Ocean Mouth",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "icaraizinho",
    "name": "Icaraizinho de Amontada, Brazil",
    "short_name": "Icaraizinho",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -3.125,
    "lon": -39.818,
    "style_tags": [
      "Wave",
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Gentle Waves, Bay Flat & Windswell",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "cauipe",
    "name": "Cauípe Lagoon (World Cup Freestyle), Brazil",
    "short_name": "Cauípe",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Ceará",
    "lat": -3.585,
    "lon": -38.789,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Jul – Jan (Strong Trade Winds)",
    "water_type": "Mirror Flat Freshwater Lagoon",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          22
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Gentler summer trades, great for all-day freestyle and warm cruising."
      },
      "2": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical rainfall season begins, lighter breeze with occasional sunny thermal afternoons."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season. Light wind and occasional tropical showers."
      },
      "4": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          10,
          17
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Low wind season. Ideal for hydrofoil or surf lessons."
      },
      "5": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          19
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Rains subside; first winter southeasterly trades begin building."
      },
      "6": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds turn on reliably. Perfect for mid-size kites."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Prime season kick-off. 20+ knots almost every afternoon."
      },
      "8": {
        "wind_prob": 94,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. Clockwork southeasterly trades blow non-stop."
      },
      "9": {
        "wind_prob": 96,
        "avg_kts": 26,
        "range": [
          22,
          32
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Maximum wind velocity of the year. Small kites (7m-9m) locked and loaded."
      },
      "10": {
        "wind_prob": 97,
        "avg_kts": 26,
        "range": [
          22,
          33
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Megaloop & big air paradise. Consistent nuclear breeze daily."
      },
      "11": {
        "wind_prob": 95,
        "avg_kts": 24,
        "range": [
          20,
          30
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Ultra-reliable wind continues with warm butter-flat lagoons."
      },
      "12": {
        "wind_prob": 85,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Holiday season breeze. Outstanding sessions and vibrant beach vibe."
      }
    }
  },
  {
    "id": "florianopolis",
    "name": "Florianópolis (Campeche & Lagoa), Brazil",
    "short_name": "Florianópolis",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Santa Catarina",
    "lat": -27.595,
    "lon": -48.548,
    "style_tags": [
      "Wave",
      "Freestyle",
      "Big Air"
    ],
    "prime_season": "Sep – Apr (Spring & Summer Cold Fronts / NE)",
    "water_type": "Ocean Waves & Vast Mountain Lagoon",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Warm northeast breeze and summer beach vibe."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Good thermal winds in afternoon."
      },
      "3": {
        "wind_prob": 60,
        "avg_kts": 16,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Transitional month with autumn swells arriving."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Powerful southern swells for strapless wave riding."
      },
      "5": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "low",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Winter sets in; southern frontal winds bring big surf."
      },
      "6": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Cold southern fronts with strong southerly winds."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Big wave conditions during southern gale passages."
      },
      "8": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          25
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up starts; northeasterly winds increase."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime spring wind season opens with strong Vento Nordeste."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 24,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "High reliability northeast winds and great wave sets in Ibiraquera."
      },
      "11": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring winds and long daylight hours."
      },
      "12": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Excellent holiday winds and warm water."
      }
    }
  },
  {
    "id": "ibiraquera",
    "name": "Ibiraquera (Barra de Ibiraquera), Brazil",
    "short_name": "Ibiraquera",
    "country": "Brazil",
    "country_code": "BR",
    "flag": "🇧🇷",
    "region": "Santa Catarina",
    "lat": -28.147,
    "lon": -48.65,
    "style_tags": [
      "Wave",
      "Strapless",
      "Freeride"
    ],
    "prime_season": "Sep – Apr (Spring & Summer Cold Fronts / NE)",
    "water_type": "World-Class Pointbreak Waves & Flat Lake",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Warm northeast breeze and summer beach vibe."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Good thermal winds in afternoon."
      },
      "3": {
        "wind_prob": 60,
        "avg_kts": 16,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Transitional month with autumn swells arriving."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Powerful southern swells for strapless wave riding."
      },
      "5": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "low",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Winter sets in; southern frontal winds bring big surf."
      },
      "6": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Cold southern fronts with strong southerly winds."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Big wave conditions during southern gale passages."
      },
      "8": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          25
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up starts; northeasterly winds increase."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime spring wind season opens with strong Vento Nordeste."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 24,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "High reliability northeast winds and great wave sets in Ibiraquera."
      },
      "11": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring winds and long daylight hours."
      },
      "12": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Excellent holiday winds and warm water."
      }
    }
  },
  {
    "id": "cabarete",
    "name": "Cabarete (Kite Beach & Bozo), Dominican Republic",
    "short_name": "Cabarete",
    "country": "Dominican Republic",
    "country_code": "DO",
    "flag": "🇩🇴",
    "region": "Puerto Plata",
    "lat": 19.752,
    "lon": -70.418,
    "style_tags": [
      "Wave",
      "Freeride",
      "Big Air",
      "Freestyle"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Shore Chop & Outer Barrier Reef Waves",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
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
    "lat": 19.322,
    "lon": -69.539,
    "style_tags": [
      "Freeride",
      "Hydrofoil",
      "Downwind"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Turquoise Flat Water & Gentle Reef Chop",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "buen_hombre",
    "name": "Buen Hombre (Secret Flatwater), Dominican Republic",
    "short_name": "Buen Hombre",
    "country": "Dominican Republic",
    "country_code": "DO",
    "flag": "🇩🇴",
    "region": "Montecristi",
    "lat": 19.882,
    "lon": -71.402,
    "style_tags": [
      "Freestyle",
      "Speed",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Ankle-Deep Butter Flat Outer Sandbars",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "punta_cana",
    "name": "Punta Cana (Playa Blanca & Cabeza de Toro), Dominican Republic",
    "short_name": "Punta Cana",
    "country": "Dominican Republic",
    "country_code": "DO",
    "flag": "🇩🇴",
    "region": "La Altagracia",
    "lat": 18.528,
    "lon": -68.369,
    "style_tags": [
      "Freeride",
      "Hydrofoil",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Protected Coral Lagoon & Clear Waters",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "el_gouna",
    "name": "El Gouna (Mangroovy & Element), Egypt",
    "short_name": "El Gouna",
    "country": "Egypt",
    "country_code": "EG",
    "flag": "🇪🇬",
    "region": "Red Sea",
    "lat": 27.394,
    "lon": 33.678,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Apr – Oct (Gulf of Suez Venturi Thermal)",
    "water_type": "Shallow Sandbank Lagoon (Knee to Waist Deep)",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp winter breeze; sunshine is warm but shorty/steamer needed."
      },
      "2": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Solid wind days with clear skies. Pack 9m-12m."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Spring heating starts accelerating the thermal venturi."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Great wind frequency and warm daytime temperatures."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Prime season opens. Strong morning and afternoon thermal."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 26,
        "air_temp": 35,
        "wetsuit": "Boardshorts",
        "tip": "Very consistent 20-28 knots. Bring sunscreen and rashguard."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Clockwork thermal machine. Butter flat water inside the sandbars."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          32
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Hottest and windiest month. Ride early morning and late afternoon."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Outstanding conditions with more comfortable air temperatures."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Superb autumn riding. Warm water and pleasant breeze."
      },
      "11": {
        "wind_prob": 62,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Comfortable autumn weather with reliable moderate breeze."
      },
      "12": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good winter getaway with empty lagoons."
      }
    }
  },
  {
    "id": "soma_bay",
    "name": "Soma Bay (Abu Soma 7Bft), Egypt",
    "short_name": "Soma Bay",
    "country": "Egypt",
    "country_code": "EG",
    "flag": "🇪🇬",
    "region": "Red Sea",
    "lat": 26.852,
    "lon": 33.991,
    "style_tags": [
      "Freestyle",
      "Speed",
      "Freeride"
    ],
    "prime_season": "Apr – Oct (Gulf of Suez Venturi Thermal)",
    "water_type": "Crystal Clear Turquoise Flatwater Spit",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp winter breeze; sunshine is warm but shorty/steamer needed."
      },
      "2": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Solid wind days with clear skies. Pack 9m-12m."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Spring heating starts accelerating the thermal venturi."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Great wind frequency and warm daytime temperatures."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Prime season opens. Strong morning and afternoon thermal."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 26,
        "air_temp": 35,
        "wetsuit": "Boardshorts",
        "tip": "Very consistent 20-28 knots. Bring sunscreen and rashguard."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Clockwork thermal machine. Butter flat water inside the sandbars."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          32
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Hottest and windiest month. Ride early morning and late afternoon."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Outstanding conditions with more comfortable air temperatures."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Superb autumn riding. Warm water and pleasant breeze."
      },
      "11": {
        "wind_prob": 62,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Comfortable autumn weather with reliable moderate breeze."
      },
      "12": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good winter getaway with empty lagoons."
      }
    }
  },
  {
    "id": "dahab",
    "name": "Dahab (Blue Lagoon), Egypt",
    "short_name": "Dahab",
    "country": "Egypt",
    "country_code": "EG",
    "flag": "🇪🇬",
    "region": "South Sinai",
    "lat": 28.566,
    "lon": 34.529,
    "style_tags": [
      "Freestyle",
      "Speed",
      "Flat Water"
    ],
    "prime_season": "Apr – Oct (Gulf of Suez Venturi Thermal)",
    "water_type": "Enclosed Natural Blue Lagoon Sandspit",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp winter breeze; sunshine is warm but shorty/steamer needed."
      },
      "2": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Solid wind days with clear skies. Pack 9m-12m."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Spring heating starts accelerating the thermal venturi."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Great wind frequency and warm daytime temperatures."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Prime season opens. Strong morning and afternoon thermal."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 26,
        "air_temp": 35,
        "wetsuit": "Boardshorts",
        "tip": "Very consistent 20-28 knots. Bring sunscreen and rashguard."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Clockwork thermal machine. Butter flat water inside the sandbars."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          32
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Hottest and windiest month. Ride early morning and late afternoon."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Outstanding conditions with more comfortable air temperatures."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Superb autumn riding. Warm water and pleasant breeze."
      },
      "11": {
        "wind_prob": 62,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Comfortable autumn weather with reliable moderate breeze."
      },
      "12": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good winter getaway with empty lagoons."
      }
    }
  },
  {
    "id": "hamata",
    "name": "Hamata (Wadi Lahami Mangroves), Egypt",
    "short_name": "Hamata",
    "country": "Egypt",
    "country_code": "EG",
    "flag": "🇪🇬",
    "region": "Red Sea South",
    "lat": 24.364,
    "lon": 35.321,
    "style_tags": [
      "Freeride",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Apr – Oct (Gulf of Suez Venturi Thermal)",
    "water_type": "Vast Uncrowded Sandbars & Warm Lagoon",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp winter breeze; sunshine is warm but shorty/steamer needed."
      },
      "2": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Solid wind days with clear skies. Pack 9m-12m."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Spring heating starts accelerating the thermal venturi."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Great wind frequency and warm daytime temperatures."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Prime season opens. Strong morning and afternoon thermal."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 26,
        "air_temp": 35,
        "wetsuit": "Boardshorts",
        "tip": "Very consistent 20-28 knots. Bring sunscreen and rashguard."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Clockwork thermal machine. Butter flat water inside the sandbars."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          32
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Hottest and windiest month. Ride early morning and late afternoon."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Outstanding conditions with more comfortable air temperatures."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Superb autumn riding. Warm water and pleasant breeze."
      },
      "11": {
        "wind_prob": 62,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Comfortable autumn weather with reliable moderate breeze."
      },
      "12": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good winter getaway with empty lagoons."
      }
    }
  },
  {
    "id": "ras_sudr",
    "name": "Ras Sudr (Sinai Gulf), Egypt",
    "short_name": "Ras Sudr",
    "country": "Egypt",
    "country_code": "EG",
    "flag": "🇪🇬",
    "region": "Gulf of Suez",
    "lat": 29.588,
    "lon": 32.709,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Apr – Oct (Gulf of Suez Venturi Thermal)",
    "water_type": "Thermal Venturi Flat Water Bays",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp winter breeze; sunshine is warm but shorty/steamer needed."
      },
      "2": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Solid wind days with clear skies. Pack 9m-12m."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Spring heating starts accelerating the thermal venturi."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Great wind frequency and warm daytime temperatures."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Prime season opens. Strong morning and afternoon thermal."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 26,
        "air_temp": 35,
        "wetsuit": "Boardshorts",
        "tip": "Very consistent 20-28 knots. Bring sunscreen and rashguard."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Clockwork thermal machine. Butter flat water inside the sandbars."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          32
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 37,
        "wetsuit": "Boardshorts",
        "tip": "Hottest and windiest month. Ride early morning and late afternoon."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Outstanding conditions with more comfortable air temperatures."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Superb autumn riding. Warm water and pleasant breeze."
      },
      "11": {
        "wind_prob": 62,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Comfortable autumn weather with reliable moderate breeze."
      },
      "12": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good winter getaway with empty lagoons."
      }
    }
  },
  {
    "id": "tarifa",
    "name": "Tarifa (Valdevaqueros & Los Lances), Spain",
    "short_name": "Tarifa",
    "country": "Spain",
    "country_code": "ES",
    "flag": "🇪🇸",
    "region": "Andalucía / Cádiz",
    "lat": 36.014,
    "lon": -5.604,
    "style_tags": [
      "Big Air",
      "Wave",
      "Freestyle",
      "Strapless"
    ],
    "prime_season": "Apr – Oct (Levante & Poniente Thermal)",
    "water_type": "Chop, Shorebreak & Rolling Atlantic Swells",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter storms bring powerful Poniente waves and empty beaches."
      },
      "2": {
        "wind_prob": 62,
        "avg_kts": 19,
        "range": [
          14,
          28
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Strong Atlantic swells and gusty Levante days."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring thermal assistance starts boosting afternoon Poniente."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 16,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Excellent mix of steady Poniente and spicy Levante."
      },
      "5": {
        "wind_prob": 80,
        "avg_kts": 23,
        "range": [
          17,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm sunny days with strong Levante cycles (pack 6m-9m)."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 24,
        "range": [
          18,
          36
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 26,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Peak summer season. Valdevaqueros comes alive every day."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong Levante days can exceed 35 kts. Epic Big Air conditions."
      },
      "8": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak European kite hub atmosphere with guaranteed daily wind."
      },
      "9": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          17,
          33
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Local favorite month: summer crowds thin out, wind stays strong."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great autumn riding with warm water and fun wave sets."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 19,
        "range": [
          14,
          27
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Transition to winter Poniente swells; great for strapless riding."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter sessions on wide open beaches."
      }
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
    "lat": 28.118,
    "lon": -14.288,
    "style_tags": [
      "Speed",
      "Big Air",
      "Freestyle",
      "Wave"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Tidal Sandbar Lagoon (Sotavento) & Ocean Chop",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "tenerife",
    "name": "Tenerife (El Médano), Spain",
    "short_name": "Tenerife",
    "country": "Spain",
    "country_code": "ES",
    "flag": "🇪🇸",
    "region": "Canary Islands",
    "lat": 28.045,
    "lon": -16.536,
    "style_tags": [
      "Wave",
      "Big Air",
      "Freeride"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Ocean Chop, Waves & Red Mountain Venturi",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "lanzarote",
    "name": "Lanzarote (Famara Beach), Spain",
    "short_name": "Lanzarote",
    "country": "Spain",
    "country_code": "ES",
    "flag": "🇪🇸",
    "region": "Canary Islands",
    "lat": 29.117,
    "lon": -13.562,
    "style_tags": [
      "Wave",
      "Strapless",
      "Freeride"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Spectacular 6km Curved Beachbreak Waves",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "mallorca",
    "name": "Mallorca (Bay of Pollença), Spain",
    "short_name": "Mallorca",
    "country": "Spain",
    "country_code": "ES",
    "flag": "🇪🇸",
    "region": "Balearic Islands",
    "lat": 39.865,
    "lon": 3.088,
    "style_tags": [
      "Freeride",
      "Hydrofoil",
      "Flat Water"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Protected Mediterranean Thermal Bay",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "denia_oliva",
    "name": "Dénia & Oliva (Playa Les Deveses), Spain",
    "short_name": "Dénia & Oliva",
    "country": "Spain",
    "country_code": "ES",
    "flag": "🇪🇸",
    "region": "Valencia",
    "lat": 38.878,
    "lon": -0.007,
    "style_tags": [
      "Freeride",
      "Hydrofoil",
      "Thermal"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Fine Sand Beach with Afternoon Garbí Thermal",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "delta_ebro",
    "name": "Delta del Ebro (Platja del Trabucador), Spain",
    "short_name": "Delta del Ebro",
    "country": "Spain",
    "country_code": "ES",
    "flag": "🇪🇸",
    "region": "Catalonia",
    "lat": 40.623,
    "lon": 0.722,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Speed"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Shallow Flat Water Bay on Narrow Sandspit",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "guincho",
    "name": "Guincho (Cascais Ocean Waves), Portugal",
    "short_name": "Guincho",
    "country": "Portugal",
    "country_code": "PT",
    "flag": "🇵🇹",
    "region": "Lisbon Coast",
    "lat": 38.732,
    "lon": -9.474,
    "style_tags": [
      "Wave",
      "Big Air",
      "Strapless"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Powerful Atlantic Swells & Heavy Shorebreak",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "esposende",
    "name": "Esposende (River Mouth & Ocean), Portugal",
    "short_name": "Esposende",
    "country": "Portugal",
    "country_code": "PT",
    "flag": "🇵🇹",
    "region": "North Portugal",
    "lat": 41.53,
    "lon": -8.784,
    "style_tags": [
      "Freestyle",
      "Wave",
      "Flat Water"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Flat Water River Lagoon & Waves on Outside",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "viana_castelo",
    "name": "Viana do Castelo (Cabedelo Beach), Portugal",
    "short_name": "Viana do Castelo",
    "country": "Portugal",
    "country_code": "PT",
    "flag": "🇵🇹",
    "region": "Minho",
    "lat": 41.681,
    "lon": -8.831,
    "style_tags": [
      "Wave",
      "Big Air",
      "Freestyle"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Flat Water behind Breakwater & Clean Waves",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "alvor",
    "name": "Alvor Lagoon (Lagos / Portimão), Portugal",
    "short_name": "Alvor Lagoon",
    "country": "Portugal",
    "country_code": "PT",
    "flag": "🇵🇹",
    "region": "Algarve",
    "lat": 37.126,
    "lon": -8.601,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Apr – Oct (Levante & Poniente Thermal)",
    "water_type": "Tidal Estuary Flat Water (Nortada Thermal)",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter storms bring powerful Poniente waves and empty beaches."
      },
      "2": {
        "wind_prob": 62,
        "avg_kts": 19,
        "range": [
          14,
          28
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Strong Atlantic swells and gusty Levante days."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring thermal assistance starts boosting afternoon Poniente."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 16,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Excellent mix of steady Poniente and spicy Levante."
      },
      "5": {
        "wind_prob": 80,
        "avg_kts": 23,
        "range": [
          17,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm sunny days with strong Levante cycles (pack 6m-9m)."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 24,
        "range": [
          18,
          36
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 26,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Peak summer season. Valdevaqueros comes alive every day."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong Levante days can exceed 35 kts. Epic Big Air conditions."
      },
      "8": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak European kite hub atmosphere with guaranteed daily wind."
      },
      "9": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          17,
          33
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Local favorite month: summer crowds thin out, wind stays strong."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great autumn riding with warm water and fun wave sets."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 19,
        "range": [
          14,
          27
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Transition to winter Poniente swells; great for strapless riding."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter sessions on wide open beaches."
      }
    }
  },
  {
    "id": "caparica",
    "name": "Costa da Caparica (Fonte da Telha), Portugal",
    "short_name": "Caparica",
    "country": "Portugal",
    "country_code": "PT",
    "flag": "🇵🇹",
    "region": "Setúbal / Lisbon",
    "lat": 38.575,
    "lon": -9.197,
    "style_tags": [
      "Wave",
      "Freeride",
      "Big Air"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Long Sandy Coastline with Rolling Atlantic Surf",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "dakhla",
    "name": "Dakhla (Lagoon & Speed Spot), Morocco",
    "short_name": "Dakhla Lagoon",
    "country": "Morocco",
    "country_code": "MA",
    "flag": "🇲🇦",
    "region": "Western Sahara",
    "lat": 23.718,
    "lon": -15.938,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Speed",
      "Downwind"
    ],
    "prime_season": "Apr – Sep (Persistent Northern Atlantic Trades)",
    "water_type": "40km Desert Lagoon & Speed Flat Sandbar",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Warm desert sun by day, brisk evenings. Great ocean waves in Lassarga."
      },
      "2": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good steady wind sessions with wide-open lagoons."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring trades kick in reliably across the 40km lagoon."
      },
      "4": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Daily 20+ knots. Perfect flat water freestyle and speed spot runs."
      },
      "5": {
        "wind_prob": 86,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 25,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Very consistent winds from morning till twilight."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Wind blows day and night. 7m-9m kites will be your daily drivers."
      },
      "7": {
        "wind_prob": 94,
        "avg_kts": 27,
        "range": [
          22,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Maximum reliability! Butter flat water in Dakhla Speed Spot."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Nuclear wind days. Excellent downwinders to White Dune."
      },
      "9": {
        "wind_prob": 85,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Still very windy with slightly warmer water."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, ideal for progress and wave riding."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Atlantic winter swells arrive at ocean-side point breaks."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sunny winter escape from European freeze."
      }
    }
  },
  {
    "id": "dakhla_white_dune",
    "name": "Dakhla (White Dune & Lassarga Waves), Morocco",
    "short_name": "Dakhla Lassarga",
    "country": "Morocco",
    "country_code": "MA",
    "flag": "🇲🇦",
    "region": "Western Sahara",
    "lat": 23.605,
    "lon": -15.975,
    "style_tags": [
      "Wave",
      "Strapless",
      "Downwind"
    ],
    "prime_season": "Apr – Sep (Persistent Northern Atlantic Trades)",
    "water_type": "World-Class Right Hand Pointbreak Wave",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Warm desert sun by day, brisk evenings. Great ocean waves in Lassarga."
      },
      "2": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good steady wind sessions with wide-open lagoons."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring trades kick in reliably across the 40km lagoon."
      },
      "4": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Daily 20+ knots. Perfect flat water freestyle and speed spot runs."
      },
      "5": {
        "wind_prob": 86,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 25,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Very consistent winds from morning till twilight."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Wind blows day and night. 7m-9m kites will be your daily drivers."
      },
      "7": {
        "wind_prob": 94,
        "avg_kts": 27,
        "range": [
          22,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Maximum reliability! Butter flat water in Dakhla Speed Spot."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Nuclear wind days. Excellent downwinders to White Dune."
      },
      "9": {
        "wind_prob": 85,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Still very windy with slightly warmer water."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, ideal for progress and wave riding."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Atlantic winter swells arrive at ocean-side point breaks."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sunny winter escape from European freeze."
      }
    }
  },
  {
    "id": "essaouira",
    "name": "Essaouira (Bay & Sidi Kaouki), Morocco",
    "short_name": "Essaouira",
    "country": "Morocco",
    "country_code": "MA",
    "flag": "🇲🇦",
    "region": "Marrakech-Safi",
    "lat": 31.508,
    "lon": -9.771,
    "style_tags": [
      "Wave",
      "Freeride",
      "Big Air"
    ],
    "prime_season": "Apr – Sep (Persistent Northern Atlantic Trades)",
    "water_type": "Curved Sandy Bay with Rolling Swells & Chop",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Warm desert sun by day, brisk evenings. Great ocean waves in Lassarga."
      },
      "2": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good steady wind sessions with wide-open lagoons."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring trades kick in reliably across the 40km lagoon."
      },
      "4": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Daily 20+ knots. Perfect flat water freestyle and speed spot runs."
      },
      "5": {
        "wind_prob": 86,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 25,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Very consistent winds from morning till twilight."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Wind blows day and night. 7m-9m kites will be your daily drivers."
      },
      "7": {
        "wind_prob": 94,
        "avg_kts": 27,
        "range": [
          22,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Maximum reliability! Butter flat water in Dakhla Speed Spot."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Nuclear wind days. Excellent downwinders to White Dune."
      },
      "9": {
        "wind_prob": 85,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Still very windy with slightly warmer water."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, ideal for progress and wave riding."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Atlantic winter swells arrive at ocean-side point breaks."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sunny winter escape from European freeze."
      }
    }
  },
  {
    "id": "taghazout",
    "name": "Taghazout & Tamri (Wave Coast), Morocco",
    "short_name": "Taghazout",
    "country": "Morocco",
    "country_code": "MA",
    "flag": "🇲🇦",
    "region": "Souss-Massa",
    "lat": 30.545,
    "lon": -9.709,
    "style_tags": [
      "Wave",
      "Strapless",
      "Freeride"
    ],
    "prime_season": "Apr – Sep (Persistent Northern Atlantic Trades)",
    "water_type": "Iconic Ocean Pointbreaks & Desert Waves",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Warm desert sun by day, brisk evenings. Great ocean waves in Lassarga."
      },
      "2": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Good steady wind sessions with wide-open lagoons."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring trades kick in reliably across the 40km lagoon."
      },
      "4": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Daily 20+ knots. Perfect flat water freestyle and speed spot runs."
      },
      "5": {
        "wind_prob": 86,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 25,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Very consistent winds from morning till twilight."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Wind blows day and night. 7m-9m kites will be your daily drivers."
      },
      "7": {
        "wind_prob": 94,
        "avg_kts": 27,
        "range": [
          22,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Maximum reliability! Butter flat water in Dakhla Speed Spot."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Nuclear wind days. Excellent downwinders to White Dune."
      },
      "9": {
        "wind_prob": 85,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 27,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Still very windy with slightly warmer water."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          15,
          26
        ],
        "season": "good",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, ideal for progress and wave riding."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Atlantic winter swells arrive at ocean-side point breaks."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sunny winter escape from European freeze."
      }
    }
  },
  {
    "id": "sal_kite_beach",
    "name": "Sal (Kite Beach - Costa da Fragata), Cape Verde",
    "short_name": "Sal Kite Beach",
    "country": "Cape Verde",
    "country_code": "CV",
    "flag": "🇨🇻",
    "region": "Ilha do Sal",
    "lat": 16.602,
    "lon": -22.894,
    "style_tags": [
      "Wave",
      "Freeride",
      "Big Air"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Side-Onshore Ocean Waves & Rolling Swell",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "sal_ponta_preta",
    "name": "Sal (Ponta Preta & Santa Maria), Cape Verde",
    "short_name": "Ponta Preta",
    "country": "Cape Verde",
    "country_code": "CV",
    "flag": "🇨🇻",
    "region": "Ilha do Sal",
    "lat": 16.592,
    "lon": -22.921,
    "style_tags": [
      "Wave",
      "Strapless"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Legendary Fast Barrelling Right-Hander",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "boa_vista",
    "name": "Boa Vista (Sal Rei & Ervatão), Cape Verde",
    "short_name": "Boa Vista",
    "country": "Cape Verde",
    "country_code": "CV",
    "flag": "🇨🇻",
    "region": "Boa Vista",
    "lat": 16.177,
    "lon": -22.918,
    "style_tags": [
      "Wave",
      "Freeride",
      "Flat Water"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Protected Bay & Outer Atlantic Swells",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "cape_town_blouberg",
    "name": "Cape Town (Blouberg / Kite Beach), South Africa",
    "short_name": "Cape Town Blouberg",
    "country": "South Africa",
    "country_code": "ZA",
    "flag": "🇿🇦",
    "region": "Western Cape",
    "lat": -33.824,
    "lon": 18.473,
    "style_tags": [
      "Big Air",
      "Wave",
      "Freeride"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "Atlantic Wave Kickers with Table Mountain Backdrop",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "cape_town_big_bay",
    "name": "Cape Town (Big Bay & Dolphin Beach), South Africa",
    "short_name": "Cape Town Big Bay",
    "country": "South Africa",
    "country_code": "ZA",
    "flag": "🇿🇦",
    "region": "Western Cape",
    "lat": -33.795,
    "lon": 18.459,
    "style_tags": [
      "Wave",
      "Big Air",
      "Strapless"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "Clean Wave Break between Rocky Points",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "langebaan",
    "name": "Langebaan (Shark Bay & Main Beach), South Africa",
    "short_name": "Langebaan",
    "country": "South Africa",
    "country_code": "ZA",
    "flag": "🇿🇦",
    "region": "West Coast",
    "lat": -33.09,
    "lon": 18.033,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "Turquoise Flat Water Tidal Lagoon (Warmer Water)",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "witsand",
    "name": "Witsand (Breede River Mouth), South Africa",
    "short_name": "Witsand",
    "country": "South Africa",
    "country_code": "ZA",
    "flag": "🇿🇦",
    "region": "Garden Route",
    "lat": -34.394,
    "lon": 20.852,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Wave"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "River Estuary Sandbanks & Ocean Sandbar Waves",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "rhodes_prasonisi",
    "name": "Rhodes (Prasonisi Double-Sided Beach), Greece",
    "short_name": "Rhodes Prasonisi",
    "country": "Greece",
    "country_code": "GR",
    "flag": "🇬🇷",
    "region": "Dodecanese",
    "lat": 35.882,
    "lon": 27.769,
    "style_tags": [
      "Freestyle",
      "Wave",
      "Speed",
      "Big Air"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Mirror Flat on Aegean Side & Waves on Med Side",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "rhodes_theologos",
    "name": "Rhodes (Theologos & Fanes), Greece",
    "short_name": "Rhodes Theologos",
    "country": "Greece",
    "country_code": "GR",
    "flag": "🇬🇷",
    "region": "Dodecanese",
    "lat": 36.376,
    "lon": 28.039,
    "style_tags": [
      "Freeride",
      "Big Air",
      "Hydrofoil"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Thermal Sea Breeze with Afternoon Swell Kickers",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "paros_pounda",
    "name": "Paros (Pounda Channel), Greece",
    "short_name": "Paros Pounda",
    "country": "Greece",
    "country_code": "GR",
    "flag": "🇬🇷",
    "region": "Cyclades",
    "lat": 37.054,
    "lon": 25.109,
    "style_tags": [
      "Freestyle",
      "Big Air",
      "Freeride"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Funnel Channel Flat Water & Venturi Boost",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "naxos_mikri_vigla",
    "name": "Naxos (Mikri Vigla Beach), Greece",
    "short_name": "Naxos Mikri Vigla",
    "country": "Greece",
    "country_code": "GR",
    "flag": "🇬🇷",
    "region": "Cyclades",
    "lat": 37.027,
    "lon": 25.371,
    "style_tags": [
      "Freeride",
      "Freestyle",
      "Big Air"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Crystal Clear Water with Natural Point Venturi",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "lefkada_milos",
    "name": "Lefkada (Agios Ioannis & Milos), Greece",
    "short_name": "Lefkada",
    "country": "Greece",
    "country_code": "GR",
    "flag": "🇬🇷",
    "region": "Ionian Islands",
    "lat": 38.835,
    "lon": 20.677,
    "style_tags": [
      "Freeride",
      "Hydrofoil",
      "Freestyle"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Clockwork Afternoon Ionian Thermal & Blue Water",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "limnos_keros",
    "name": "Limnos (Keros Bay), Greece",
    "short_name": "Limnos Keros",
    "country": "Greece",
    "country_code": "GR",
    "flag": "🇬🇷",
    "region": "North Aegean",
    "lat": 39.905,
    "lon": 25.291,
    "style_tags": [
      "Flat Water",
      "Wave",
      "Freeride"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "3-in-1 Bay: Super Flat, Small Chop & Gentle Waves",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "akyaka",
    "name": "Akyaka (Gökova Thermal Bay), Turkey",
    "short_name": "Akyaka",
    "country": "Turkey",
    "country_code": "TR",
    "flag": "🇹🇷",
    "region": "Muğla",
    "lat": 37.053,
    "lon": 28.324,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "3km Sand Beach with Thermal Sea Breeze Venturi",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "alacati",
    "name": "Alaçatı (Cesme Peninsula), Turkey",
    "short_name": "Alaçatı",
    "country": "Turkey",
    "country_code": "TR",
    "flag": "🇹🇷",
    "region": "Izmir",
    "lat": 38.257,
    "lon": 26.388,
    "style_tags": [
      "Speed",
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Enclosed Flatwater Bay & Shallow Banks",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "urla",
    "name": "Urla (Gülbahçe Bay), Turkey",
    "short_name": "Urla",
    "country": "Turkey",
    "country_code": "TR",
    "flag": "🇹🇷",
    "region": "Izmir",
    "lat": 38.334,
    "lon": 26.657,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Shallow Warm Thermal Flatwater",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "le_morne",
    "name": "Le Morne (One Eye, Manawa & Lagoon), Mauritius",
    "short_name": "Le Morne",
    "country": "Mauritius",
    "country_code": "MU",
    "flag": "🇲🇺",
    "region": "Black River",
    "lat": -20.453,
    "lon": 57.311,
    "style_tags": [
      "Wave",
      "Freestyle",
      "Strapless",
      "Freeride"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Massive Turquoise Lagoon & Legendary Reef Passes",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "bel_ombre",
    "name": "Bel Ombre (South Coast Lagoon), Mauritius",
    "short_name": "Bel Ombre",
    "country": "Mauritius",
    "country_code": "MU",
    "flag": "🇲🇺",
    "region": "Savanne",
    "lat": -20.505,
    "lon": 57.408,
    "style_tags": [
      "Freeride",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Uncrowded Outer Coral Reef Flat Lagoon",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "pointe_esny",
    "name": "Pointe d'Esny (Blue Bay Lagoon), Mauritius",
    "short_name": "Pointe d'Esny",
    "country": "Mauritius",
    "country_code": "MU",
    "flag": "🇲🇺",
    "region": "Grand Port",
    "lat": -20.428,
    "lon": 57.726,
    "style_tags": [
      "Hydrofoil",
      "Freeride",
      "Flat Water"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Vast Turquoise Hydrofoil Heaven",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "sakalava",
    "name": "Sakalava Bay (Diego Suarez), Madagascar",
    "short_name": "Sakalava Bay",
    "country": "Madagascar",
    "country_code": "MG",
    "flag": "🇲🇬",
    "region": "Diana",
    "lat": -12.302,
    "lon": 49.387,
    "style_tags": [
      "Freestyle",
      "Wave",
      "Flat Water"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Enclosed Flat Lagoon & Outer Reef Wave",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "babaomby",
    "name": "Babaomby (Emerald Sea), Madagascar",
    "short_name": "Babaomby",
    "country": "Madagascar",
    "country_code": "MG",
    "flag": "🇲🇬",
    "region": "Antsiranana",
    "lat": -12.115,
    "lon": 49.337,
    "style_tags": [
      "Freeride",
      "Speed",
      "Flat Water"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Pristine Emerald Lagoon & Outer Atoll",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "hood_river",
    "name": "Hood River (Columbia River Gorge), USA",
    "short_name": "Hood River",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Oregon",
    "lat": 45.712,
    "lon": -121.512,
    "style_tags": [
      "Big Air",
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "May – Sep (Cascade Thermal Venturi)",
    "water_type": "Freshwater River Waves Rolling against Current",
    "months": {
      "1": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 6,
        "air_temp": 5,
        "wetsuit": "Drysuit",
        "tip": "Freezing winter. Gorge is blanketed in snow and ice."
      },
      "2": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 8,
        "wetsuit": "Drysuit",
        "tip": "Cold winter off-season."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 9,
        "air_temp": 12,
        "wetsuit": "5/4mm + Hood",
        "tip": "Spring warm-up, snowmelt raises the Columbia River."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 11,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "First thermal pressure gradients establish through the Gorge."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 21,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season begins in earnest! The Hatch and Event Site firing."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Nuclear Gorge winds blow against river current for huge kickers."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          20,
          36
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 30,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak season! 25-35 kts rolling swell, warm sun and vibrant scene."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          19,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm water and reliable afternoon venturi breeze every day."
      },
      "9": {
        "wind_prob": 72,
        "avg_kts": 21,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp autumn air, beautiful foliage and solid wind days."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          11,
          23
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Thermal engine slows down as inland desert cools."
      },
      "11": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 10,
        "air_temp": 10,
        "wetsuit": "5/4mm + Hood",
        "tip": "Late autumn cold winds."
      },
      "12": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "Drysuit",
        "tip": "Winter closure."
      }
    }
  },
  {
    "id": "cape_hatteras",
    "name": "Cape Hatteras (Outer Banks Waves & Sound), USA",
    "short_name": "Cape Hatteras",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "North Carolina",
    "lat": 35.228,
    "lon": -75.534,
    "style_tags": [
      "Wave",
      "Freestyle",
      "Downwind"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Pamlico Sound Flatwater on West & Ocean Waves on East",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "maui_kite_beach",
    "name": "Maui (Kite Beach & Kanaha), USA",
    "short_name": "Maui Kite Beach",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Hawaii",
    "lat": 20.899,
    "lon": -156.442,
    "style_tags": [
      "Wave",
      "Strapless",
      "Freeride"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Protected Outer Reef with Punchy Shore Waves",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "oahu_kailua",
    "name": "Oahu (Kailua Beach & Mokuleia), USA",
    "short_name": "Oahu Kailua",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Hawaii",
    "lat": 21.398,
    "lon": -157.74,
    "style_tags": [
      "Wave",
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Turquoise Bay Swell & Outer Reef Waves",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "south_padre",
    "name": "South Padre Island (Laguna Madre & Gulf), USA",
    "short_name": "South Padre Island",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Texas",
    "lat": 26.111,
    "lon": -97.168,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Wave"
    ],
    "prime_season": "Nov – Mar (El Norte & Sea of Cortez Thermal)",
    "water_type": "Waist-Deep Flat Laguna Madre & Gulf Waves",
    "months": {
      "1": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime El Norte wind season. Wind builds at 11am, swells rolling in."
      },
      "2": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Very consistent winds, sunny desert warmth and friendly kite community."
      },
      "3": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring conditions with steady afternoon breeze."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "El Norte fades as spring heats up; great for foiling."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season hot desert weather."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 26,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Summer heatwave on Sea of Cortez."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Extreme desert heat and calm waters."
      },
      "8": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Occasional hurricane swells from Pacific."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season slowly concludes."
      },
      "10": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "First El Norte winds arrive late October; warm water."
      },
      "11": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "Season kick-off! Campgrounds fill with kiters, clockwork breeze."
      },
      "12": {
        "wind_prob": 86,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Classic winter holiday kite destination. Pack 8m-11m kites."
      }
    }
  },
  {
    "id": "corpus_christi",
    "name": "Corpus Christi (Bird Island Basin), USA",
    "short_name": "Corpus Christi",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Texas",
    "lat": 27.587,
    "lon": -97.298,
    "style_tags": [
      "Speed",
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Nov – Mar (El Norte & Sea of Cortez Thermal)",
    "water_type": "Shallow Steady Thermal Saltwater Basin",
    "months": {
      "1": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime El Norte wind season. Wind builds at 11am, swells rolling in."
      },
      "2": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Very consistent winds, sunny desert warmth and friendly kite community."
      },
      "3": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring conditions with steady afternoon breeze."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "El Norte fades as spring heats up; great for foiling."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season hot desert weather."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 26,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Summer heatwave on Sea of Cortez."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Extreme desert heat and calm waters."
      },
      "8": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Occasional hurricane swells from Pacific."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season slowly concludes."
      },
      "10": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "First El Norte winds arrive late October; warm water."
      },
      "11": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "Season kick-off! Campgrounds fill with kiters, clockwork breeze."
      },
      "12": {
        "wind_prob": 86,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Classic winter holiday kite destination. Pack 8m-11m kites."
      }
    }
  },
  {
    "id": "belmont_shore",
    "name": "Belmont Shore (Long Beach), USA",
    "short_name": "Belmont Shore",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "California",
    "lat": 33.758,
    "lon": -118.136,
    "style_tags": [
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "May – Sep (Alisios Trade Winds)",
    "water_type": "Protected Breakwater Ocean Flat & Thermal Sea Breeze",
    "months": {
      "1": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 19,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm European winter escape with moderate breeze."
      },
      "2": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great wave riding on north shores."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 18,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring Alisios begin building in strength."
      },
      "4": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Consistent trade winds setup across all islands."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Full trade wind machine turns on. Sotavento tidal lagoon fills up."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          20,
          34
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong gusty winds in El Medano and Sotavento; 7m-9m kites prime."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          22,
          36
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Peak windiest month. World Cup Big Air conditions."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          21,
          35
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Nuclear trades blow daily from mid-morning to sunset."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Shorty 2mm",
        "tip": "Gentler winds, warmest water of the year."
      },
      "10": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant autumn breeze and start of winter swell season."
      },
      "11": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Surf season begins; waves on northern points."
      },
      "12": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Sunny winter getaways with decent wave sessions."
      }
    }
  },
  {
    "id": "sherman_island",
    "name": "Sherman Island (San Francisco Delta), USA",
    "short_name": "Sherman Island",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "California",
    "lat": 38.066,
    "lon": -121.782,
    "style_tags": [
      "Big Air",
      "Freeride"
    ],
    "prime_season": "May – Sep (Cascade Thermal Venturi)",
    "water_type": "Sacramento River Thermal Venturi & Rolling Swells",
    "months": {
      "1": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 6,
        "air_temp": 5,
        "wetsuit": "Drysuit",
        "tip": "Freezing winter. Gorge is blanketed in snow and ice."
      },
      "2": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 8,
        "wetsuit": "Drysuit",
        "tip": "Cold winter off-season."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 9,
        "air_temp": 12,
        "wetsuit": "5/4mm + Hood",
        "tip": "Spring warm-up, snowmelt raises the Columbia River."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 11,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "First thermal pressure gradients establish through the Gorge."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 21,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season begins in earnest! The Hatch and Event Site firing."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Nuclear Gorge winds blow against river current for huge kickers."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          20,
          36
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 30,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak season! 25-35 kts rolling swell, warm sun and vibrant scene."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          19,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm water and reliable afternoon venturi breeze every day."
      },
      "9": {
        "wind_prob": 72,
        "avg_kts": 21,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp autumn air, beautiful foliage and solid wind days."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          11,
          23
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Thermal engine slows down as inland desert cools."
      },
      "11": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 10,
        "air_temp": 10,
        "wetsuit": "5/4mm + Hood",
        "tip": "Late autumn cold winds."
      },
      "12": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "Drysuit",
        "tip": "Winter closure."
      }
    }
  },
  {
    "id": "st_petersburg",
    "name": "St. Petersburg & Skyway (Tampa Bay), USA",
    "short_name": "St. Petersburg",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Florida",
    "lat": 27.658,
    "lon": -82.651,
    "style_tags": [
      "Freestyle",
      "Hydrofoil",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Warm Shallow Sandbars & Gulf Coast Breeze",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "florida_keys",
    "name": "Islamorada & Florida Keys (Anne's Beach), USA",
    "short_name": "Florida Keys",
    "country": "United States",
    "country_code": "US",
    "flag": "🇺🇸",
    "region": "Florida",
    "lat": 24.898,
    "lon": -80.647,
    "style_tags": [
      "Freeride",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Warm Tropical Flats & Mangrove Channels",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "la_ventana",
    "name": "La Ventana (Sea of Cortez), Mexico",
    "short_name": "La Ventana",
    "country": "Mexico",
    "country_code": "MX",
    "flag": "🇲🇽",
    "region": "Baja California Sur",
    "lat": 24.053,
    "lon": -109.996,
    "style_tags": [
      "Big Air",
      "Freeride",
      "Hydrofoil",
      "Downwind"
    ],
    "prime_season": "Nov – Mar (El Norte & Sea of Cortez Thermal)",
    "water_type": "Deep Cobalt Blue Water with Rolling Swells",
    "months": {
      "1": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime El Norte wind season. Wind builds at 11am, swells rolling in."
      },
      "2": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Very consistent winds, sunny desert warmth and friendly kite community."
      },
      "3": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring conditions with steady afternoon breeze."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "El Norte fades as spring heats up; great for foiling."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season hot desert weather."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 26,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Summer heatwave on Sea of Cortez."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Extreme desert heat and calm waters."
      },
      "8": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Occasional hurricane swells from Pacific."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season slowly concludes."
      },
      "10": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "First El Norte winds arrive late October; warm water."
      },
      "11": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "Season kick-off! Campgrounds fill with kiters, clockwork breeze."
      },
      "12": {
        "wind_prob": 86,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Classic winter holiday kite destination. Pack 8m-11m kites."
      }
    }
  },
  {
    "id": "los_barriles",
    "name": "Los Barriles (East Cape), Mexico",
    "short_name": "Los Barriles",
    "country": "Mexico",
    "country_code": "MX",
    "flag": "🇲🇽",
    "region": "Baja California Sur",
    "lat": 23.682,
    "lon": -109.704,
    "style_tags": [
      "Wave",
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "Nov – Mar (El Norte & Sea of Cortez Thermal)",
    "water_type": "Gentle Shorebreak & Rolling Wind Swell",
    "months": {
      "1": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime El Norte wind season. Wind builds at 11am, swells rolling in."
      },
      "2": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Very consistent winds, sunny desert warmth and friendly kite community."
      },
      "3": {
        "wind_prob": 78,
        "avg_kts": 20,
        "range": [
          16,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring conditions with steady afternoon breeze."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 23,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "El Norte fades as spring heats up; great for foiling."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Off-season hot desert weather."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 26,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Summer heatwave on Sea of Cortez."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Extreme desert heat and calm waters."
      },
      "8": {
        "wind_prob": 35,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 36,
        "wetsuit": "Boardshorts",
        "tip": "Occasional hurricane swells from Pacific."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 34,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season slowly concludes."
      },
      "10": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "First El Norte winds arrive late October; warm water."
      },
      "11": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "Season kick-off! Campgrounds fill with kiters, clockwork breeze."
      },
      "12": {
        "wind_prob": 86,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Classic winter holiday kite destination. Pack 8m-11m kites."
      }
    }
  },
  {
    "id": "isla_blanca",
    "name": "Isla Blanca (Cancun Flatwater Lagoon), Mexico",
    "short_name": "Isla Blanca",
    "country": "Mexico",
    "country_code": "MX",
    "flag": "🇲🇽",
    "region": "Quintana Roo",
    "lat": 21.378,
    "lon": -86.804,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Shallow Knee-Deep Mangrove Lagoon",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "el_cuyo",
    "name": "El Cuyo (Yucatán Emerald Coast), Mexico",
    "short_name": "El Cuyo",
    "country": "Mexico",
    "country_code": "MX",
    "flag": "🇲🇽",
    "region": "Yucatán",
    "lat": 21.518,
    "lon": -87.683,
    "style_tags": [
      "Freeride",
      "Hydrofoil",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Turquoise Sea with Sandy Bottom & Thermal Trades",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "sisal",
    "name": "Sisal (Yucatán Thermal Coast), Mexico",
    "short_name": "Sisal",
    "country": "Mexico",
    "country_code": "MX",
    "flag": "🇲🇽",
    "region": "Yucatán",
    "lat": 21.162,
    "lon": -90.033,
    "style_tags": [
      "Hydrofoil",
      "Freeride"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Warm Thermal Gulf Coastline",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
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
    "lat": 10.898,
    "lon": -75.093,
    "style_tags": [
      "Wave",
      "Big Air",
      "Freestyle"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Pointbreak Waves & Flat Water behind Sandspit",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "cabo_de_la_vela",
    "name": "Cabo de la Vela (La Guajira Desert), Colombia",
    "short_name": "Cabo de la Vela",
    "country": "Colombia",
    "country_code": "CO",
    "flag": "🇨🇴",
    "region": "La Guajira",
    "lat": 12.203,
    "lon": -72.152,
    "style_tags": [
      "Speed",
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Offshore Howling Desert Flat Water",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "san_andres",
    "name": "San Andrés Island (Johnny Cay), Colombia",
    "short_name": "San Andrés",
    "country": "Colombia",
    "country_code": "CO",
    "flag": "🇨🇴",
    "region": "Caribbean",
    "lat": 12.584,
    "lon": -81.7,
    "style_tags": [
      "Wave",
      "Freeride"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "7-Color Sea Coral Reef Waves",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "boracay",
    "name": "Boracay (Bulabog Beach), Philippines",
    "short_name": "Boracay",
    "country": "Philippines",
    "country_code": "PH",
    "flag": "🇵🇭",
    "region": "Aklan",
    "lat": 11.968,
    "lon": 121.93,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Wave"
    ],
    "prime_season": "Nov – Apr (Amihan Northeast Monsoon)",
    "water_type": "Protected Coral Lagoon & Outer Wave Reef",
    "months": {
      "1": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Peak Amihan monsoon. Bulabog beach is pumping non-stop daily."
      },
      "2": {
        "wind_prob": 85,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Solid trade winds and warm turquoise water."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Sunny and reliable winds, ideal for all riding levels."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon transitions to summer lull."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 30,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Off-season; hot weather and calm seas."
      },
      "6": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Habagat southwest monsoon (rainy season)."
      },
      "7": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rainy and gusty southwest winds."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Stormy southwest squalls."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Habagat subsides as typhoon season winds down."
      },
      "10": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "First Amihan breezes detectible late in the month."
      },
      "11": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Amihan setup establishes across the Philippines and Vietnam."
      },
      "12": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Christmas monsoon season delivers great tropical sessions."
      }
    }
  },
  {
    "id": "siargao",
    "name": "Siargao Island (General Luna Lagoon), Philippines",
    "short_name": "Siargao",
    "country": "Philippines",
    "country_code": "PH",
    "flag": "🇵🇭",
    "region": "Surigao del Norte",
    "lat": 9.789,
    "lon": 126.155,
    "style_tags": [
      "Wave",
      "Strapless",
      "Freeride"
    ],
    "prime_season": "Nov – Apr (Amihan Northeast Monsoon)",
    "water_type": "World-Class Tropical Reef Swells",
    "months": {
      "1": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Peak Amihan monsoon. Bulabog beach is pumping non-stop daily."
      },
      "2": {
        "wind_prob": 85,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Solid trade winds and warm turquoise water."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Sunny and reliable winds, ideal for all riding levels."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon transitions to summer lull."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 30,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Off-season; hot weather and calm seas."
      },
      "6": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Habagat southwest monsoon (rainy season)."
      },
      "7": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rainy and gusty southwest winds."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Stormy southwest squalls."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Habagat subsides as typhoon season winds down."
      },
      "10": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "First Amihan breezes detectible late in the month."
      },
      "11": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Amihan setup establishes across the Philippines and Vietnam."
      },
      "12": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Christmas monsoon season delivers great tropical sessions."
      }
    }
  },
  {
    "id": "kingfisher",
    "name": "Kingfisher (Pagudpud, Ilocos Norte), Philippines",
    "short_name": "Kingfisher Pagudpud",
    "country": "Philippines",
    "country_code": "PH",
    "flag": "🇵🇭",
    "region": "Ilocos Norte",
    "lat": 18.571,
    "lon": 120.785,
    "style_tags": [
      "Wave",
      "Big Air"
    ],
    "prime_season": "Nov – Apr (Amihan Northeast Monsoon)",
    "water_type": "Heavy Barrelling Coral Reef Waves",
    "months": {
      "1": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Peak Amihan monsoon. Bulabog beach is pumping non-stop daily."
      },
      "2": {
        "wind_prob": 85,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Solid trade winds and warm turquoise water."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Sunny and reliable winds, ideal for all riding levels."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon transitions to summer lull."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 30,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Off-season; hot weather and calm seas."
      },
      "6": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Habagat southwest monsoon (rainy season)."
      },
      "7": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rainy and gusty southwest winds."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Stormy southwest squalls."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Habagat subsides as typhoon season winds down."
      },
      "10": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "First Amihan breezes detectible late in the month."
      },
      "11": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Amihan setup establishes across the Philippines and Vietnam."
      },
      "12": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Christmas monsoon season delivers great tropical sessions."
      }
    }
  },
  {
    "id": "mui_ne",
    "name": "Mui Ne (East Beach & Malibu), Vietnam",
    "short_name": "Mui Ne",
    "country": "Vietnam",
    "country_code": "VN",
    "flag": "🇻🇳",
    "region": "Bình Thuận",
    "lat": 10.938,
    "lon": 108.287,
    "style_tags": [
      "Wave",
      "Big Air",
      "Freeride"
    ],
    "prime_season": "Nov – Apr (Amihan Northeast Monsoon)",
    "water_type": "Shorebreak & Steep Rolling Wind Swell",
    "months": {
      "1": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Peak Amihan monsoon. Bulabog beach is pumping non-stop daily."
      },
      "2": {
        "wind_prob": 85,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Solid trade winds and warm turquoise water."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Sunny and reliable winds, ideal for all riding levels."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon transitions to summer lull."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 30,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Off-season; hot weather and calm seas."
      },
      "6": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Habagat southwest monsoon (rainy season)."
      },
      "7": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rainy and gusty southwest winds."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Stormy southwest squalls."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Habagat subsides as typhoon season winds down."
      },
      "10": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "First Amihan breezes detectible late in the month."
      },
      "11": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Amihan setup establishes across the Philippines and Vietnam."
      },
      "12": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Christmas monsoon season delivers great tropical sessions."
      }
    }
  },
  {
    "id": "phan_rang",
    "name": "Phan Rang (My Hoa Lagoon), Vietnam",
    "short_name": "Phan Rang",
    "country": "Vietnam",
    "country_code": "VN",
    "flag": "🇻🇳",
    "region": "Ninh Thuận",
    "lat": 11.602,
    "lon": 109.112,
    "style_tags": [
      "Freestyle",
      "Speed",
      "Wave"
    ],
    "prime_season": "Nov – Apr (Amihan Northeast Monsoon)",
    "water_type": "Huge Coral Barrier Flatwater & Outer Wave",
    "months": {
      "1": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Peak Amihan monsoon. Bulabog beach is pumping non-stop daily."
      },
      "2": {
        "wind_prob": 85,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Solid trade winds and warm turquoise water."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Sunny and reliable winds, ideal for all riding levels."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon transitions to summer lull."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 12,
        "range": [
          8,
          17
        ],
        "season": "low",
        "sea_temp": 30,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Off-season; hot weather and calm seas."
      },
      "6": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Habagat southwest monsoon (rainy season)."
      },
      "7": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rainy and gusty southwest winds."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          21
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Stormy southwest squalls."
      },
      "9": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          10,
          20
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Habagat subsides as typhoon season winds down."
      },
      "10": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "First Amihan breezes detectible late in the month."
      },
      "11": {
        "wind_prob": 72,
        "avg_kts": 19,
        "range": [
          14,
          25
        ],
        "season": "good",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Amihan setup establishes across the Philippines and Vietnam."
      },
      "12": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Christmas monsoon season delivers great tropical sessions."
      }
    }
  },
  {
    "id": "kalpitiya",
    "name": "Kalpitiya Lagoon & Kappalady, Sri Lanka",
    "short_name": "Kalpitiya",
    "country": "Sri Lanka",
    "country_code": "LK",
    "flag": "🇱🇰",
    "region": "North Western",
    "lat": 8.228,
    "lon": 79.761,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Speed"
    ],
    "prime_season": "May – Oct (Summer SW Monsoon) & Dec – Feb",
    "water_type": "Butter Flat Lagoon Sandspit & Indian Ocean",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Winter northeast monsoon brings steady afternoon wind."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical sessions on the sandbar."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Inter-monsoonal lull. Good for dolphin watching."
      },
      "4": {
        "wind_prob": 40,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Hot, humid off-season."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Summer SW monsoon hits full power! 20-25 knots daily."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak season. Butter flat water on the lagoon side, waves on ocean."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          32
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Non-stop wind blows 24 hours a day. Small kite heaven."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Strong constant breeze, downwinders to Vella Island."
      },
      "9": {
        "wind_prob": 84,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Still very windy with fewer kiters on the water."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          20
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon changeover brings tropical rain showers."
      },
      "11": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          20
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Intermittent winds between rain bands."
      },
      "12": {
        "wind_prob": 65,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter monsoon starts up nicely for the holidays."
      }
    }
  },
  {
    "id": "mannar",
    "name": "Mannar Island (Adam's Bridge), Sri Lanka",
    "short_name": "Mannar Island",
    "country": "Sri Lanka",
    "country_code": "LK",
    "flag": "🇱🇰",
    "region": "Northern",
    "lat": 9.083,
    "lon": 79.8,
    "style_tags": [
      "Freestyle",
      "Speed",
      "Flat Water"
    ],
    "prime_season": "May – Oct (Summer SW Monsoon) & Dec – Feb",
    "water_type": "Pristine Flat Water Sandbanks between Islands",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Winter northeast monsoon brings steady afternoon wind."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical sessions on the sandbar."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Inter-monsoonal lull. Good for dolphin watching."
      },
      "4": {
        "wind_prob": 40,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Hot, humid off-season."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Summer SW monsoon hits full power! 20-25 knots daily."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak season. Butter flat water on the lagoon side, waves on ocean."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          32
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Non-stop wind blows 24 hours a day. Small kite heaven."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Strong constant breeze, downwinders to Vella Island."
      },
      "9": {
        "wind_prob": 84,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Still very windy with fewer kiters on the water."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          20
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon changeover brings tropical rain showers."
      },
      "11": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          20
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Intermittent winds between rain bands."
      },
      "12": {
        "wind_prob": 65,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter monsoon starts up nicely for the holidays."
      }
    }
  },
  {
    "id": "diani_beach",
    "name": "Diani Beach (Galu & Kongo River), Kenya",
    "short_name": "Diani Beach",
    "country": "Kenya",
    "country_code": "KE",
    "flag": "🇰🇪",
    "region": "Kwale",
    "lat": -4.279,
    "lon": 39.594,
    "style_tags": [
      "Freeride",
      "Wave",
      "Flat Water"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Powder Sand Barrier Reef Lagoon",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "watamu",
    "name": "Watamu (Garoda & Turtle Bay), Kenya",
    "short_name": "Watamu",
    "country": "Kenya",
    "country_code": "KE",
    "flag": "🇰🇪",
    "region": "Kilifi",
    "lat": -3.354,
    "lon": 40.016,
    "style_tags": [
      "Freeride",
      "Wave",
      "Hydrofoil"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Coral Sandbanks & Turquoise Warm Ocean",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "paje",
    "name": "Paje Beach (Zanzibar Lagoon), Tanzania",
    "short_name": "Paje Zanzibar",
    "country": "Tanzania",
    "country_code": "TZ",
    "flag": "🇹🇿",
    "region": "Zanzibar",
    "lat": -6.265,
    "lon": 39.534,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Freeride"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Tidal Turquoise Flat Water Lagoon",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "jambiani",
    "name": "Jambiani (Zanzibar Barrier Reef), Tanzania",
    "short_name": "Jambiani",
    "country": "Tanzania",
    "country_code": "TZ",
    "flag": "🇹🇿",
    "region": "Zanzibar",
    "lat": -6.319,
    "lon": 39.544,
    "style_tags": [
      "Wave",
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "May – Nov (Strong Southeast Trade Winds)",
    "water_type": "Wide Sand Flat & Outer Reef Wave",
    "months": {
      "1": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Summer cyclone season. Light winds and warm tropical showers."
      },
      "2": {
        "wind_prob": 40,
        "avg_kts": 14,
        "range": [
          11,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical lull. Good for surfing or diving."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Seasonal transition as autumn approaches."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Trade winds begin to establish across the lagoons."
      },
      "5": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          16,
          26
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Prime season opens. Consistent SE trades blow over Le Morne lagoon."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 22,
        "range": [
          18,
          28
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Consistent strong trade winds and world-class waves on One Eye."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          19,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak wind month! Manawa and One Eye firing for wave riders."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 24,
        "range": [
          19,
          31
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 24,
        "wetsuit": "Shorty 2mm",
        "tip": "Unstoppable winter trades. Ideal 8m-10m kite weather daily."
      },
      "9": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 25,
        "wetsuit": "Shorty 2mm",
        "tip": "Excellent conditions continue with sunny skies and empty spots."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          27
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Boardshorts",
        "tip": "Warm spring conditions with steady breeze throughout the day."
      },
      "11": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Late season trades, warm water and long sunny daylight."
      },
      "12": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Start of tropical summer lull."
      }
    }
  },
  {
    "id": "safety_bay",
    "name": "Perth (Safety Bay & The Pond), Australia",
    "short_name": "Safety Bay Perth",
    "country": "Australia",
    "country_code": "AU",
    "flag": "🇦🇺",
    "region": "Western Australia",
    "lat": -32.308,
    "lon": 115.707,
    "style_tags": [
      "Freestyle",
      "Speed",
      "Flat Water"
    ],
    "prime_season": "Nov – Mar (Fremantle Doctor Sea Breeze)",
    "water_type": "Legendary Butter Flat Sandspit (The Pond)",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          18,
          32
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "The Fremantle Doctor arrives like clockwork at 12:30 PM. 20-30 kts."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer thermal wind. Safety Bay Pond is butter flat."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm sunny days with solid afternoon sea breezes."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Autumn cool-down; swell increases on outer reefs."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          11,
          22
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Off-season. Winter fronts bring occasional NW winds."
      },
      "6": {
        "wind_prob": 35,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter rain storms with strong gusty winds."
      },
      "7": {
        "wind_prob": 35,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Cold winter lows, good for big wave surfing."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Late winter transitions."
      },
      "9": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          14,
          26
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up begins; first sea breezes of the season."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Season ramps up fast with frequent 20+ knot afternoons."
      },
      "11": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          31
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 27,
        "wetsuit": "Shorty / Boardies",
        "tip": "Outstanding wind consistency and long sunny days."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          19,
          33
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Summer holiday perfection. World-class flat water sessions."
      }
    }
  },
  {
    "id": "woodman_point",
    "name": "Perth (Woodman Point), Australia",
    "short_name": "Woodman Point",
    "country": "Australia",
    "country_code": "AU",
    "flag": "🇦🇺",
    "region": "Western Australia",
    "lat": -32.138,
    "lon": 115.759,
    "style_tags": [
      "Freeride",
      "Big Air"
    ],
    "prime_season": "Nov – Mar (Fremantle Doctor Sea Breeze)",
    "water_type": "Cockburn Sound Flat & Swell",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          18,
          32
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "The Fremantle Doctor arrives like clockwork at 12:30 PM. 20-30 kts."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer thermal wind. Safety Bay Pond is butter flat."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm sunny days with solid afternoon sea breezes."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Autumn cool-down; swell increases on outer reefs."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          11,
          22
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Off-season. Winter fronts bring occasional NW winds."
      },
      "6": {
        "wind_prob": 35,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter rain storms with strong gusty winds."
      },
      "7": {
        "wind_prob": 35,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Cold winter lows, good for big wave surfing."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Late winter transitions."
      },
      "9": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          14,
          26
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up begins; first sea breezes of the season."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Season ramps up fast with frequent 20+ knot afternoons."
      },
      "11": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          31
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 27,
        "wetsuit": "Shorty / Boardies",
        "tip": "Outstanding wind consistency and long sunny days."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          19,
          33
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Summer holiday perfection. World-class flat water sessions."
      }
    }
  },
  {
    "id": "exmouth",
    "name": "Exmouth (Ningaloo Reef), Australia",
    "short_name": "Exmouth Ningaloo",
    "country": "Australia",
    "country_code": "AU",
    "flag": "🇦🇺",
    "region": "Western Australia",
    "lat": -21.933,
    "lon": 114.125,
    "style_tags": [
      "Wave",
      "Freeride",
      "Strapless"
    ],
    "prime_season": "Nov – Mar (Fremantle Doctor Sea Breeze)",
    "water_type": "World Heritage Coral Reef Waves & Flat Lagoon",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 24,
        "range": [
          18,
          32
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "The Fremantle Doctor arrives like clockwork at 12:30 PM. 20-30 kts."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          30
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer thermal wind. Safety Bay Pond is butter flat."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "good",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm sunny days with solid afternoon sea breezes."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 21,
        "air_temp": 25,
        "wetsuit": "3/2mm Steamer",
        "tip": "Autumn cool-down; swell increases on outer reefs."
      },
      "5": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          11,
          22
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Off-season. Winter fronts bring occasional NW winds."
      },
      "6": {
        "wind_prob": 35,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter rain storms with strong gusty winds."
      },
      "7": {
        "wind_prob": 35,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Cold winter lows, good for big wave surfing."
      },
      "8": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Late winter transitions."
      },
      "9": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          14,
          26
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up begins; first sea breezes of the season."
      },
      "10": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Season ramps up fast with frequent 20+ knot afternoons."
      },
      "11": {
        "wind_prob": 88,
        "avg_kts": 23,
        "range": [
          18,
          31
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 27,
        "wetsuit": "Shorty / Boardies",
        "tip": "Outstanding wind consistency and long sunny days."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          19,
          33
        ],
        "season": "peak",
        "sea_temp": 21,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Summer holiday perfection. World-class flat water sessions."
      }
    }
  },
  {
    "id": "sydney_botany",
    "name": "Sydney (Botany Bay & Kurnell), Australia",
    "short_name": "Sydney Botany",
    "country": "Australia",
    "country_code": "AU",
    "flag": "🇦🇺",
    "region": "New South Wales",
    "lat": -34.004,
    "lon": 151.196,
    "style_tags": [
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "Sep – Apr (Spring & Summer Cold Fronts / NE)",
    "water_type": "Wide Coastal Bay with Summer Southerly Busters",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Warm northeast breeze and summer beach vibe."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Good thermal winds in afternoon."
      },
      "3": {
        "wind_prob": 60,
        "avg_kts": 16,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Transitional month with autumn swells arriving."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Powerful southern swells for strapless wave riding."
      },
      "5": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "low",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Winter sets in; southern frontal winds bring big surf."
      },
      "6": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Cold southern fronts with strong southerly winds."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Big wave conditions during southern gale passages."
      },
      "8": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          25
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up starts; northeasterly winds increase."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime spring wind season opens with strong Vento Nordeste."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 24,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "High reliability northeast winds and great wave sets in Ibiraquera."
      },
      "11": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring winds and long daylight hours."
      },
      "12": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Excellent holiday winds and warm water."
      }
    }
  },
  {
    "id": "st_kilda",
    "name": "Melbourne (St Kilda & Green Point), Australia",
    "short_name": "Melbourne St Kilda",
    "country": "Australia",
    "country_code": "AU",
    "flag": "🇦🇺",
    "region": "Victoria",
    "lat": -37.867,
    "lon": 144.973,
    "style_tags": [
      "Freeride",
      "Big Air",
      "Hydrofoil"
    ],
    "prime_season": "Sep – Apr (Spring & Summer Cold Fronts / NE)",
    "water_type": "Port Phillip Bay Sea Breeze Chop",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Warm northeast breeze and summer beach vibe."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Good thermal winds in afternoon."
      },
      "3": {
        "wind_prob": 60,
        "avg_kts": 16,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Transitional month with autumn swells arriving."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Powerful southern swells for strapless wave riding."
      },
      "5": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "low",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Winter sets in; southern frontal winds bring big surf."
      },
      "6": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Cold southern fronts with strong southerly winds."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Big wave conditions during southern gale passages."
      },
      "8": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          25
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up starts; northeasterly winds increase."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime spring wind season opens with strong Vento Nordeste."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 24,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "High reliability northeast winds and great wave sets in Ibiraquera."
      },
      "11": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring winds and long daylight hours."
      },
      "12": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Excellent holiday winds and warm water."
      }
    }
  },
  {
    "id": "cairns",
    "name": "Cairns (Yorkeys Knob), Australia",
    "short_name": "Cairns Yorkeys",
    "country": "Australia",
    "country_code": "AU",
    "flag": "🇦🇺",
    "region": "Queensland",
    "lat": -16.816,
    "lon": 145.722,
    "style_tags": [
      "Freeride",
      "Wave"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Tropical Coral Coast Sea Breeze",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "brouwersdam",
    "name": "Brouwersdam (Zeeland North Sea & Lake), Netherlands",
    "short_name": "Brouwersdam",
    "country": "Netherlands",
    "country_code": "NL",
    "flag": "🇳🇱",
    "region": "Zeeland",
    "lat": 51.761,
    "lon": 3.856,
    "style_tags": [
      "Freestyle",
      "Big Air",
      "Flat Water"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Lake Grevelingen Flat & North Sea Sandbar",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "scheveningen",
    "name": "Scheveningen (The Hague Waves), Netherlands",
    "short_name": "Scheveningen",
    "country": "Netherlands",
    "country_code": "NL",
    "flag": "🇳🇱",
    "region": "South Holland",
    "lat": 52.115,
    "lon": 4.275,
    "style_tags": [
      "Wave",
      "Big Air",
      "Strapless"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "North Sea Wave Kickers & Pier Harbor Currents",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "mirns",
    "name": "Mirns (IJsselmeer Shallow Flat), Netherlands",
    "short_name": "Mirns",
    "country": "Netherlands",
    "country_code": "NL",
    "flag": "🇳🇱",
    "region": "Friesland",
    "lat": 52.855,
    "lon": 5.467,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Freshwater Waist-Deep Lake Flat",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "zandvoort",
    "name": "Zandvoort (North Sea Swell), Netherlands",
    "short_name": "Zandvoort",
    "country": "Netherlands",
    "country_code": "NL",
    "flag": "🇳🇱",
    "region": "North Holland",
    "lat": 52.375,
    "lon": 4.528,
    "style_tags": [
      "Big Air",
      "Wave"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Open North Sea Rolling Waves",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "leucate",
    "name": "Leucate (La Franqui & Les Coussoules), France",
    "short_name": "Leucate",
    "country": "France",
    "country_code": "FR",
    "flag": "🇫🇷",
    "region": "Occitanie",
    "lat": 42.928,
    "lon": 3.033,
    "style_tags": [
      "Speed",
      "Big Air",
      "Freestyle"
    ],
    "prime_season": "Apr – Oct (Levante & Poniente Thermal)",
    "water_type": "Nuclear Tramontana (Mondial du Vent) Flat & Chop",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter storms bring powerful Poniente waves and empty beaches."
      },
      "2": {
        "wind_prob": 62,
        "avg_kts": 19,
        "range": [
          14,
          28
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Strong Atlantic swells and gusty Levante days."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring thermal assistance starts boosting afternoon Poniente."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 16,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Excellent mix of steady Poniente and spicy Levante."
      },
      "5": {
        "wind_prob": 80,
        "avg_kts": 23,
        "range": [
          17,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm sunny days with strong Levante cycles (pack 6m-9m)."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 24,
        "range": [
          18,
          36
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 26,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Peak summer season. Valdevaqueros comes alive every day."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong Levante days can exceed 35 kts. Epic Big Air conditions."
      },
      "8": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak European kite hub atmosphere with guaranteed daily wind."
      },
      "9": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          17,
          33
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Local favorite month: summer crowds thin out, wind stays strong."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great autumn riding with warm water and fun wave sets."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 19,
        "range": [
          14,
          27
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Transition to winter Poniente swells; great for strapless riding."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter sessions on wide open beaches."
      }
    }
  },
  {
    "id": "hyeres",
    "name": "Hyères (Plage de l'Almanarre), France",
    "short_name": "Hyères Almanarre",
    "country": "France",
    "country_code": "FR",
    "flag": "🇫🇷",
    "region": "Provence",
    "lat": 43.078,
    "lon": 6.126,
    "style_tags": [
      "Freeride",
      "Big Air",
      "Wave"
    ],
    "prime_season": "Apr – Oct (Levante & Poniente Thermal)",
    "water_type": "Mistral Storm Chop & Eastern Thermal Flat",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter storms bring powerful Poniente waves and empty beaches."
      },
      "2": {
        "wind_prob": 62,
        "avg_kts": 19,
        "range": [
          14,
          28
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Strong Atlantic swells and gusty Levante days."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring thermal assistance starts boosting afternoon Poniente."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 16,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Excellent mix of steady Poniente and spicy Levante."
      },
      "5": {
        "wind_prob": 80,
        "avg_kts": 23,
        "range": [
          17,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm sunny days with strong Levante cycles (pack 6m-9m)."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 24,
        "range": [
          18,
          36
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 26,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Peak summer season. Valdevaqueros comes alive every day."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong Levante days can exceed 35 kts. Epic Big Air conditions."
      },
      "8": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak European kite hub atmosphere with guaranteed daily wind."
      },
      "9": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          17,
          33
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Local favorite month: summer crowds thin out, wind stays strong."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great autumn riding with warm water and fun wave sets."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 19,
        "range": [
          14,
          27
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Transition to winter Poniente swells; great for strapless riding."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter sessions on wide open beaches."
      }
    }
  },
  {
    "id": "quiberon",
    "name": "Quiberon & Carnac (Brittany Coast), France",
    "short_name": "Quiberon",
    "country": "France",
    "country_code": "FR",
    "flag": "🇫🇷",
    "region": "Brittany",
    "lat": 47.567,
    "lon": -3.136,
    "style_tags": [
      "Wave",
      "Freeride",
      "Flat Water"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Atlantic Ocean Swells & Bay Flatwater",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "port_saint_louis",
    "name": "Port Saint-Louis (Plage Napoléon), France",
    "short_name": "Port Saint-Louis",
    "country": "France",
    "country_code": "FR",
    "flag": "🇫🇷",
    "region": "Camargue",
    "lat": 43.351,
    "lon": 4.887,
    "style_tags": [
      "Speed",
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Apr – Oct (Levante & Poniente Thermal)",
    "water_type": "10km Sand Beach with Howling Mistral Flat",
    "months": {
      "1": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter storms bring powerful Poniente waves and empty beaches."
      },
      "2": {
        "wind_prob": 62,
        "avg_kts": 19,
        "range": [
          14,
          28
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "Strong Atlantic swells and gusty Levante days."
      },
      "3": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring thermal assistance starts boosting afternoon Poniente."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 16,
        "air_temp": 20,
        "wetsuit": "3/2mm or 4/3mm",
        "tip": "Excellent mix of steady Poniente and spicy Levante."
      },
      "5": {
        "wind_prob": 80,
        "avg_kts": 23,
        "range": [
          17,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warm sunny days with strong Levante cycles (pack 6m-9m)."
      },
      "6": {
        "wind_prob": 85,
        "avg_kts": 24,
        "range": [
          18,
          36
        ],
        "season": "peak",
        "sea_temp": 18,
        "air_temp": 26,
        "wetsuit": "3/2mm or Shorty",
        "tip": "Peak summer season. Valdevaqueros comes alive every day."
      },
      "7": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Strong Levante days can exceed 35 kts. Epic Big Air conditions."
      },
      "8": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          38
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak European kite hub atmosphere with guaranteed daily wind."
      },
      "9": {
        "wind_prob": 82,
        "avg_kts": 23,
        "range": [
          17,
          33
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Local favorite month: summer crowds thin out, wind stays strong."
      },
      "10": {
        "wind_prob": 72,
        "avg_kts": 20,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Great autumn riding with warm water and fun wave sets."
      },
      "11": {
        "wind_prob": 64,
        "avg_kts": 19,
        "range": [
          14,
          27
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Transition to winter Poniente swells; great for strapless riding."
      },
      "12": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter sessions on wide open beaches."
      }
    }
  },
  {
    "id": "dossen",
    "name": "Dossen (Santec, Brittany), France",
    "short_name": "Dossen",
    "country": "France",
    "country_code": "FR",
    "flag": "🇫🇷",
    "region": "Finistère",
    "lat": 48.709,
    "lon": -4.072,
    "style_tags": [
      "Wave",
      "Strapless",
      "Big Air"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Tidal Wave Arena & Atlantic Swell",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "lo_stagnone",
    "name": "Lo Stagnone (Marsala, Sicily), Italy",
    "short_name": "Lo Stagnone",
    "country": "Italy",
    "country_code": "IT",
    "flag": "🇮🇹",
    "region": "Sicily",
    "lat": 37.869,
    "lon": 12.464,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Speed"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "2000-Hectare Knee-Deep Mirror Flat Lagoon",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "porto_pollo",
    "name": "Porto Pollo (Sardinia), Italy",
    "short_name": "Porto Pollo",
    "country": "Italy",
    "country_code": "IT",
    "flag": "🇮🇹",
    "region": "Sardinia",
    "lat": 41.192,
    "lon": 9.317,
    "style_tags": [
      "Freestyle",
      "Big Air",
      "Flat Water"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Double Bay Sandspit with Bonifacio Venturi",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "punta_trettu",
    "name": "Punta Trettu (Sardinia Flatwater), Italy",
    "short_name": "Punta Trettu",
    "country": "Italy",
    "country_code": "IT",
    "flag": "🇮🇹",
    "region": "Sardinia",
    "lat": 39.117,
    "lon": 8.442,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Shallow Enclosed Sand Flat (Mistral & Scirocco)",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "lake_garda",
    "name": "Lake Garda (Campione & Malcesine), Italy",
    "short_name": "Lake Garda",
    "country": "Italy",
    "country_code": "IT",
    "flag": "🇮🇹",
    "region": "Lombardy / Veneto",
    "lat": 45.753,
    "lon": 10.749,
    "style_tags": [
      "Hydrofoil",
      "Freeride"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Freshwater Alpine Lake (Morning Peler & Afternoon Ora)",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "gizzeria",
    "name": "Gizzeria Lido (Hang Loose Beach), Italy",
    "short_name": "Gizzeria Lido",
    "country": "Italy",
    "country_code": "IT",
    "flag": "🇮🇹",
    "region": "Calabria",
    "lat": 38.932,
    "lon": 16.208,
    "style_tags": [
      "Hydrofoil",
      "Freestyle",
      "Thermal"
    ],
    "prime_season": "Jun – Sep (Meltemi Trade Winds)",
    "water_type": "Clockwork Thermal Venturi Sea Breeze",
    "months": {
      "1": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 16,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Winter Mediterranean depressions with cold gusty breeze."
      },
      "2": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 15,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Off-season Greek island vibe."
      },
      "3": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring transitions with intermittent thermal breeze."
      },
      "4": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          24
        ],
        "season": "shoulder",
        "sea_temp": 17,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Pleasant spring warm-up, quiet beaches."
      },
      "5": {
        "wind_prob": 68,
        "avg_kts": 19,
        "range": [
          14,
          26
        ],
        "season": "good",
        "sea_temp": 19,
        "air_temp": 24,
        "wetsuit": "3/2mm or Shorty",
        "tip": "First Meltemi cycles blow across the Cyclades and Dodecanese."
      },
      "6": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          29
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 28,
        "wetsuit": "Shorty 2mm",
        "tip": "Meltemi turns on full power! Sunny skies, turquoise warm water."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 24,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak wind machine. 20-30 knots daily, crystal clear Aegean Sea."
      },
      "8": {
        "wind_prob": 92,
        "avg_kts": 25,
        "range": [
          20,
          33
        ],
        "season": "peak",
        "sea_temp": 25,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Rock-solid Meltemi. Prasonisi double-sided beach in full glory."
      },
      "9": {
        "wind_prob": 78,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Shorty / Boardies",
        "tip": "Fantastic late season: warm sea, golden light, fewer crowds."
      },
      "10": {
        "wind_prob": 58,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Gentler autumn breeze, peaceful island ambiance."
      },
      "11": {
        "wind_prob": 48,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Meltemi dies down, winter lows take over."
      },
      "12": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          12,
          23
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 15,
        "wetsuit": "4/3mm Steamer",
        "tip": "Quiet winter season."
      }
    }
  },
  {
    "id": "fehmarn",
    "name": "Fehmarn (Gold & Wulfen), Germany",
    "short_name": "Fehmarn",
    "country": "Germany",
    "country_code": "DE",
    "flag": "🇩🇪",
    "region": "Baltic Sea",
    "lat": 54.437,
    "lon": 11.194,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Freeride"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Baltic Sea Shallow Bays & Flatwater Channels",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "st_peter_ording",
    "name": "St. Peter-Ording (North Sea Sands), Germany",
    "short_name": "SPO",
    "country": "Germany",
    "country_code": "DE",
    "flag": "🇩🇪",
    "region": "North Sea",
    "lat": 54.303,
    "lon": 8.647,
    "style_tags": [
      "Big Air",
      "Wave"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Gigantic Tidal Sandflat & North Sea Breakers",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "ruegen",
    "name": "Rügen (Suhrendorf & Wieck), Germany",
    "short_name": "Rügen",
    "country": "Germany",
    "country_code": "DE",
    "flag": "🇩🇪",
    "region": "Baltic Sea",
    "lat": 54.496,
    "lon": 13.149,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Endless Shallow Flatwater Bodden Lagoon",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "masirah",
    "name": "Masirah Island (Monsoon Winds), Oman",
    "short_name": "Masirah Island",
    "country": "Oman",
    "country_code": "OM",
    "flag": "🇴🇲",
    "region": "Ash Sharqiyah",
    "lat": 20.477,
    "lon": 58.788,
    "style_tags": [
      "Wave",
      "Big Air",
      "Speed"
    ],
    "prime_season": "May – Oct (Summer SW Monsoon) & Dec – Feb",
    "water_type": "Khareef Summer Monsoon (25-35 kts) & Cool Water",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Winter northeast monsoon brings steady afternoon wind."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Warm tropical sessions on the sandbar."
      },
      "3": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          10,
          19
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 32,
        "wetsuit": "Boardshorts",
        "tip": "Inter-monsoonal lull. Good for dolphin watching."
      },
      "4": {
        "wind_prob": 40,
        "avg_kts": 13,
        "range": [
          9,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 33,
        "wetsuit": "Boardshorts",
        "tip": "Hot, humid off-season."
      },
      "5": {
        "wind_prob": 82,
        "avg_kts": 22,
        "range": [
          17,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Summer SW monsoon hits full power! 20-25 knots daily."
      },
      "6": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Peak season. Butter flat water on the lagoon side, waves on ocean."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 26,
        "range": [
          21,
          32
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Non-stop wind blows 24 hours a day. Small kite heaven."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 25,
        "range": [
          20,
          31
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Strong constant breeze, downwinders to Vella Island."
      },
      "9": {
        "wind_prob": 84,
        "avg_kts": 23,
        "range": [
          18,
          29
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Still very windy with fewer kiters on the water."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          20
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Monsoon changeover brings tropical rain showers."
      },
      "11": {
        "wind_prob": 45,
        "avg_kts": 15,
        "range": [
          11,
          20
        ],
        "season": "low",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Intermittent winds between rain bands."
      },
      "12": {
        "wind_prob": 65,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter monsoon starts up nicely for the holidays."
      }
    }
  },
  {
    "id": "bilene",
    "name": "Bilene Lagoon (San Martinho), Mozambique",
    "short_name": "Bilene Lagoon",
    "country": "Mozambique",
    "country_code": "MZ",
    "flag": "🇲🇿",
    "region": "Gaza",
    "lat": -25.263,
    "lon": 33.242,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "27km Warm Saltwater Tidal Lagoon",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "tofo",
    "name": "Tofo & Barra Beach, Mozambique",
    "short_name": "Tofo Barra",
    "country": "Mozambique",
    "country_code": "MZ",
    "flag": "🇲🇿",
    "region": "Inhambane",
    "lat": -23.856,
    "lon": 35.545,
    "style_tags": [
      "Wave",
      "Freeride"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "Tropical Estuary Flats & Outer Ocean Surf",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "namotu",
    "name": "Namotu Island (Cloudbreak & Wilkes), Fiji",
    "short_name": "Namotu Fiji",
    "country": "Fiji",
    "country_code": "FJ",
    "flag": "🇫🇯",
    "region": "Mamanuca Islands",
    "lat": -17.854,
    "lon": 177.203,
    "style_tags": [
      "Wave",
      "Strapless"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "World-Class Heavy Barrier Reef Barrels",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "aruba",
    "name": "Aruba (Boca Grandi & Fisherman's Huts), Aruba",
    "short_name": "Aruba",
    "country": "Aruba",
    "country_code": "AW",
    "flag": "🇦🇼",
    "region": "ABC Islands",
    "lat": 12.433,
    "lon": -69.878,
    "style_tags": [
      "Wave",
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Choppy Waves at Boca & Flat Water at Huts",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "bonaire",
    "name": "Bonaire (Atlantis Beach / Kite Beach), Bonaire",
    "short_name": "Bonaire Atlantis",
    "country": "Bonaire",
    "country_code": "BQ",
    "flag": "🇧🇶",
    "region": "ABC Islands",
    "lat": 12.062,
    "lon": -68.277,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Offshore Trade Winds over Turquoise Deep Flat",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "curacao",
    "name": "Curaçao (Sint Joris Baai), Curaçao",
    "short_name": "Curaçao Sint Joris",
    "country": "Curaçao",
    "country_code": "CW",
    "flag": "🇨🇼",
    "region": "ABC Islands",
    "lat": 12.119,
    "lon": -68.826,
    "style_tags": [
      "Freestyle",
      "Freeride"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Enclosed Inland Sea Bay with Strong Trades",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "poole_harbour",
    "name": "Poole Harbour & Sandbanks, United Kingdom",
    "short_name": "Poole Harbour",
    "country": "United Kingdom",
    "country_code": "GB",
    "flag": "🇬🇧",
    "region": "Dorset",
    "lat": 50.701,
    "lon": -1.944,
    "style_tags": [
      "Freestyle",
      "Flat Water",
      "Hydrofoil"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Massive Natural Harbour Flat & Sandbanks",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "rhosneigr",
    "name": "Rhosneigr (Anglesey Waves), United Kingdom",
    "short_name": "Rhosneigr",
    "country": "United Kingdom",
    "country_code": "GB",
    "flag": "🇬🇧",
    "region": "Wales",
    "lat": 53.226,
    "lon": -4.524,
    "style_tags": [
      "Wave",
      "Big Air"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Atlantic Low Pressure Wave Sets",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "tiree",
    "name": "Isle of Tiree (Hebrides Swell), United Kingdom",
    "short_name": "Isle of Tiree",
    "country": "United Kingdom",
    "country_code": "GB",
    "flag": "🇬🇧",
    "region": "Scotland",
    "lat": 56.502,
    "lon": -6.822,
    "style_tags": [
      "Wave",
      "Big Air"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "White Sand Beaches & Pure Atlantic Groundswell",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "hayling_island",
    "name": "Hayling Island (West Beach), United Kingdom",
    "short_name": "Hayling Island",
    "country": "United Kingdom",
    "country_code": "GB",
    "flag": "🇬🇧",
    "region": "Hampshire",
    "lat": 50.778,
    "lon": -0.985,
    "style_tags": [
      "Freeride",
      "Big Air"
    ],
    "prime_season": "Sep – May (Autumn & Spring Depressions)",
    "water_type": "Solent Thermal Sea Breeze & English Channel Chop",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Powerful winter storms for hardcore cold-water riders."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 21,
        "range": [
          15,
          33
        ],
        "season": "good",
        "sea_temp": 6,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Cold winter gales and empty beaches."
      },
      "3": {
        "wind_prob": 65,
        "avg_kts": 20,
        "range": [
          14,
          30
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Spring thermal assistance starts on sunny days."
      },
      "4": {
        "wind_prob": 62,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 10,
        "air_temp": 14,
        "wetsuit": "4/3mm Steamer",
        "tip": "Pleasant spring riding with warming air."
      },
      "5": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm Steamer",
        "tip": "Sea breeze thermals set in along coastal dunes."
      },
      "6": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 16,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Longest daylight of the year (sessions till 10 PM!)."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Summer beach weather, lighter thermal sea breeze."
      },
      "8": {
        "wind_prob": 54,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 19,
        "air_temp": 23,
        "wetsuit": "3/2mm Steamer",
        "tip": "Warmest water of the year in the North Sea."
      },
      "9": {
        "wind_prob": 68,
        "avg_kts": 20,
        "range": [
          15,
          30
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn storm season begins! Excellent Big Air & wave kickers."
      },
      "10": {
        "wind_prob": 74,
        "avg_kts": 22,
        "range": [
          16,
          34
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 15,
        "wetsuit": "4/3mm or 5/4mm",
        "tip": "Prime autumn gale season with consistent westerly winds."
      },
      "11": {
        "wind_prob": 75,
        "avg_kts": 23,
        "range": [
          17,
          35
        ],
        "season": "peak",
        "sea_temp": 11,
        "air_temp": 10,
        "wetsuit": "5/4mm + Booties",
        "tip": "Deep low pressure depressions bring nuclear wind sessions."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 22,
        "range": [
          16,
          35
        ],
        "season": "good",
        "sea_temp": 8,
        "air_temp": 7,
        "wetsuit": "5/4mm + Booties + Hood",
        "tip": "Rugged winter riding with heavy winds."
      }
    }
  },
  {
    "id": "bahia_salinas",
    "name": "Bahía Salinas (Playa Copal), Costa Rica",
    "short_name": "Bahía Salinas",
    "country": "Costa Rica",
    "country_code": "CR",
    "flag": "🇨🇷",
    "region": "Guanacaste",
    "lat": 11.031,
    "lon": -85.679,
    "style_tags": [
      "Big Air",
      "Freeride"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Papagayo Jet Wind (25-35 kts) & Ocean Chop",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "lake_arenal",
    "name": "Lake Arenal (Tilarán Volcano), Costa Rica",
    "short_name": "Lake Arenal",
    "country": "Costa Rica",
    "country_code": "CR",
    "flag": "🇨🇷",
    "region": "Guanacaste",
    "lat": 10.533,
    "lon": -84.928,
    "style_tags": [
      "Freeride",
      "Big Air"
    ],
    "prime_season": "Dec – Aug (Consistent Atlantic Trades)",
    "water_type": "Freshwater Mountain Lake Swell & Strong Venturi",
    "months": {
      "1": {
        "wind_prob": 74,
        "avg_kts": 18,
        "range": [
          15,
          23
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Winter trades reinforced by north swells. Prime wave riding on outer reefs."
      },
      "2": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Consistent easterly breeze, great for both waves and twin-tip blasting."
      },
      "3": {
        "wind_prob": 80,
        "avg_kts": 19,
        "range": [
          16,
          25
        ],
        "season": "good",
        "sea_temp": 26,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Reliable Atlantic trade winds build daily by 1:00 PM."
      },
      "4": {
        "wind_prob": 75,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Pleasant spring conditions with warm tropical sea and air."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 19,
        "range": [
          15,
          24
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Thermal effect kicks in early with longer sun exposure."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 22,
        "range": [
          18,
          27
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Peak summer trade wind season. 20+ knots almost every single afternoon."
      },
      "7": {
        "wind_prob": 90,
        "avg_kts": 23,
        "range": [
          19,
          28
        ],
        "season": "peak",
        "sea_temp": 28,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Windiest month of the year! Bring your 8m-10m quiver."
      },
      "8": {
        "wind_prob": 82,
        "avg_kts": 20,
        "range": [
          16,
          25
        ],
        "season": "peak",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Solid summer winds continue through mid-afternoon."
      },
      "9": {
        "wind_prob": 55,
        "avg_kts": 15,
        "range": [
          12,
          20
        ],
        "season": "shoulder",
        "sea_temp": 29,
        "air_temp": 31,
        "wetsuit": "Boardshorts",
        "tip": "Tropical storm season; wind is intermittent between sunny intervals."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 14,
        "range": [
          11,
          18
        ],
        "season": "low",
        "sea_temp": 29,
        "air_temp": 30,
        "wetsuit": "Boardshorts",
        "tip": "Lightest month of the year. Good for foiling or scuba diving."
      },
      "11": {
        "wind_prob": 58,
        "avg_kts": 16,
        "range": [
          12,
          21
        ],
        "season": "shoulder",
        "sea_temp": 28,
        "air_temp": 29,
        "wetsuit": "Boardshorts",
        "tip": "Early winter trades return alongside first winter swells."
      },
      "12": {
        "wind_prob": 72,
        "avg_kts": 18,
        "range": [
          14,
          23
        ],
        "season": "good",
        "sea_temp": 27,
        "air_temp": 28,
        "wetsuit": "Boardshorts",
        "tip": "Christmas trades deliver warm winds and fun waves on outer reef."
      }
    }
  },
  {
    "id": "matanzas",
    "name": "Matanzas (Pupuya Waves), Chile",
    "short_name": "Matanzas",
    "country": "Chile",
    "country_code": "CL",
    "flag": "🇨🇱",
    "region": "O'Higgins",
    "lat": -33.958,
    "lon": -71.871,
    "style_tags": [
      "Wave",
      "Strapless"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "Cold Humboldt Current Ocean Waves & Strong S Wind",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  },
  {
    "id": "puclaro",
    "name": "Puclaro Dam (Elqui Valley), Chile",
    "short_name": "Puclaro",
    "country": "Chile",
    "country_code": "CL",
    "flag": "🇨🇱",
    "region": "Coquimbo",
    "lat": -30.015,
    "lon": -70.932,
    "style_tags": [
      "Freestyle",
      "Flat Water"
    ],
    "prime_season": "May – Sep (Cascade Thermal Venturi)",
    "water_type": "Andes Thermal Mountain Reservoir (20-30 kts)",
    "months": {
      "1": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 6,
        "air_temp": 5,
        "wetsuit": "Drysuit",
        "tip": "Freezing winter. Gorge is blanketed in snow and ice."
      },
      "2": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 8,
        "wetsuit": "Drysuit",
        "tip": "Cold winter off-season."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 9,
        "air_temp": 12,
        "wetsuit": "5/4mm + Hood",
        "tip": "Spring warm-up, snowmelt raises the Columbia River."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 11,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "First thermal pressure gradients establish through the Gorge."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 21,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season begins in earnest! The Hatch and Event Site firing."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Nuclear Gorge winds blow against river current for huge kickers."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          20,
          36
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 30,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak season! 25-35 kts rolling swell, warm sun and vibrant scene."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          19,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm water and reliable afternoon venturi breeze every day."
      },
      "9": {
        "wind_prob": 72,
        "avg_kts": 21,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp autumn air, beautiful foliage and solid wind days."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          11,
          23
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Thermal engine slows down as inland desert cools."
      },
      "11": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 10,
        "air_temp": 10,
        "wetsuit": "5/4mm + Hood",
        "tip": "Late autumn cold winds."
      },
      "12": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "Drysuit",
        "tip": "Winter closure."
      }
    }
  },
  {
    "id": "cuesta_del_viento",
    "name": "Cuesta del Viento (Rodeo, San Juan), Argentina",
    "short_name": "Cuesta del Viento",
    "country": "Argentina",
    "country_code": "AR",
    "flag": "🇦🇷",
    "region": "San Juan",
    "lat": -30.222,
    "lon": -69.117,
    "style_tags": [
      "Big Air",
      "Freeride"
    ],
    "prime_season": "May – Sep (Cascade Thermal Venturi)",
    "water_type": "Nuclear Thermal Mountain Lake (30-45 kts daily!)",
    "months": {
      "1": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 6,
        "air_temp": 5,
        "wetsuit": "Drysuit",
        "tip": "Freezing winter. Gorge is blanketed in snow and ice."
      },
      "2": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 8,
        "wetsuit": "Drysuit",
        "tip": "Cold winter off-season."
      },
      "3": {
        "wind_prob": 40,
        "avg_kts": 15,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 9,
        "air_temp": 12,
        "wetsuit": "5/4mm + Hood",
        "tip": "Spring warm-up, snowmelt raises the Columbia River."
      },
      "4": {
        "wind_prob": 60,
        "avg_kts": 18,
        "range": [
          13,
          26
        ],
        "season": "shoulder",
        "sea_temp": 11,
        "air_temp": 16,
        "wetsuit": "4/3mm Steamer",
        "tip": "First thermal pressure gradients establish through the Gorge."
      },
      "5": {
        "wind_prob": 78,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 21,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season begins in earnest! The Hatch and Event Site firing."
      },
      "6": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          34
        ],
        "season": "peak",
        "sea_temp": 17,
        "air_temp": 26,
        "wetsuit": "3/2mm Steamer",
        "tip": "Nuclear Gorge winds blow against river current for huge kickers."
      },
      "7": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          20,
          36
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 30,
        "wetsuit": "Shorty 2mm",
        "tip": "Peak season! 25-35 kts rolling swell, warm sun and vibrant scene."
      },
      "8": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          19,
          35
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 29,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm water and reliable afternoon venturi breeze every day."
      },
      "9": {
        "wind_prob": 72,
        "avg_kts": 21,
        "range": [
          15,
          29
        ],
        "season": "good",
        "sea_temp": 18,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Crisp autumn air, beautiful foliage and solid wind days."
      },
      "10": {
        "wind_prob": 45,
        "avg_kts": 16,
        "range": [
          11,
          23
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 17,
        "wetsuit": "4/3mm Steamer",
        "tip": "Thermal engine slows down as inland desert cools."
      },
      "11": {
        "wind_prob": 25,
        "avg_kts": 13,
        "range": [
          9,
          19
        ],
        "season": "low",
        "sea_temp": 10,
        "air_temp": 10,
        "wetsuit": "5/4mm + Hood",
        "tip": "Late autumn cold winds."
      },
      "12": {
        "wind_prob": 20,
        "avg_kts": 12,
        "range": [
          8,
          18
        ],
        "season": "low",
        "sea_temp": 7,
        "air_temp": 6,
        "wetsuit": "Drysuit",
        "tip": "Winter closure."
      }
    }
  },
  {
    "id": "buenos_aires_riodelaplata",
    "name": "Buenos Aires (San Isidro / Rio de la Plata), Argentina",
    "short_name": "Buenos Aires",
    "country": "Argentina",
    "country_code": "AR",
    "flag": "🇦🇷",
    "region": "Buenos Aires",
    "lat": -34.469,
    "lon": -58.508,
    "style_tags": [
      "Freeride",
      "Hydrofoil"
    ],
    "prime_season": "Sep – Apr (Spring & Summer Cold Fronts / NE)",
    "water_type": "Vast Brown River Estuary (Sudestada Storms)",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Warm northeast breeze and summer beach vibe."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Good thermal winds in afternoon."
      },
      "3": {
        "wind_prob": 60,
        "avg_kts": 16,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Transitional month with autumn swells arriving."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Powerful southern swells for strapless wave riding."
      },
      "5": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "low",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Winter sets in; southern frontal winds bring big surf."
      },
      "6": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Cold southern fronts with strong southerly winds."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Big wave conditions during southern gale passages."
      },
      "8": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          25
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up starts; northeasterly winds increase."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime spring wind season opens with strong Vento Nordeste."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 24,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "High reliability northeast winds and great wave sets in Ibiraquera."
      },
      "11": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring winds and long daylight hours."
      },
      "12": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Excellent holiday winds and warm water."
      }
    }
  },
  {
    "id": "raglan",
    "name": "Raglan (Manu Bay & Harbor), New Zealand",
    "short_name": "Raglan",
    "country": "New Zealand",
    "country_code": "NZ",
    "flag": "🇳🇿",
    "region": "Waikato",
    "lat": -37.801,
    "lon": 174.871,
    "style_tags": [
      "Wave",
      "Freeride"
    ],
    "prime_season": "Sep – Apr (Spring & Summer Cold Fronts / NE)",
    "water_type": "Tasman Sea Ocean Swell & Harbor Flats",
    "months": {
      "1": {
        "wind_prob": 70,
        "avg_kts": 18,
        "range": [
          14,
          24
        ],
        "season": "good",
        "sea_temp": 24,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Warm northeast breeze and summer beach vibe."
      },
      "2": {
        "wind_prob": 68,
        "avg_kts": 17,
        "range": [
          13,
          23
        ],
        "season": "good",
        "sea_temp": 25,
        "air_temp": 28,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Good thermal winds in afternoon."
      },
      "3": {
        "wind_prob": 60,
        "avg_kts": 16,
        "range": [
          13,
          22
        ],
        "season": "shoulder",
        "sea_temp": 24,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Transitional month with autumn swells arriving."
      },
      "4": {
        "wind_prob": 55,
        "avg_kts": 16,
        "range": [
          12,
          22
        ],
        "season": "shoulder",
        "sea_temp": 22,
        "air_temp": 24,
        "wetsuit": "3/2mm Steamer",
        "tip": "Powerful southern swells for strapless wave riding."
      },
      "5": {
        "wind_prob": 50,
        "avg_kts": 15,
        "range": [
          12,
          22
        ],
        "season": "low",
        "sea_temp": 20,
        "air_temp": 21,
        "wetsuit": "3/2mm Steamer",
        "tip": "Winter sets in; southern frontal winds bring big surf."
      },
      "6": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 18,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Cold southern fronts with strong southerly winds."
      },
      "7": {
        "wind_prob": 52,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "low",
        "sea_temp": 17,
        "air_temp": 19,
        "wetsuit": "3/2mm Steamer",
        "tip": "Big wave conditions during southern gale passages."
      },
      "8": {
        "wind_prob": 60,
        "avg_kts": 17,
        "range": [
          13,
          25
        ],
        "season": "shoulder",
        "sea_temp": 18,
        "air_temp": 20,
        "wetsuit": "3/2mm Steamer",
        "tip": "Spring warm-up starts; northeasterly winds increase."
      },
      "9": {
        "wind_prob": 75,
        "avg_kts": 20,
        "range": [
          15,
          27
        ],
        "season": "peak",
        "sea_temp": 19,
        "air_temp": 22,
        "wetsuit": "3/2mm Steamer",
        "tip": "Prime spring wind season opens with strong Vento Nordeste."
      },
      "10": {
        "wind_prob": 80,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 20,
        "air_temp": 24,
        "wetsuit": "Shorty / 3/2mm",
        "tip": "High reliability northeast winds and great wave sets in Ibiraquera."
      },
      "11": {
        "wind_prob": 82,
        "avg_kts": 21,
        "range": [
          16,
          28
        ],
        "season": "peak",
        "sea_temp": 22,
        "air_temp": 26,
        "wetsuit": "Shorty 2mm",
        "tip": "Warm spring winds and long daylight hours."
      },
      "12": {
        "wind_prob": 75,
        "avg_kts": 19,
        "range": [
          15,
          25
        ],
        "season": "peak",
        "sea_temp": 23,
        "air_temp": 27,
        "wetsuit": "Boardshorts / Shorty",
        "tip": "Excellent holiday winds and warm water."
      }
    }
  },
  {
    "id": "foxton",
    "name": "Foxton Beach / Wellington (Kapiti Coast), New Zealand",
    "short_name": "Foxton Beach",
    "country": "New Zealand",
    "country_code": "NZ",
    "flag": "🇳🇿",
    "region": "Manawatū / Wellington",
    "lat": -40.468,
    "lon": 175.218,
    "style_tags": [
      "Big Air",
      "Wave"
    ],
    "prime_season": "Nov – Mar (The Cape Doctor SE Gale)",
    "water_type": "Cook Strait Roaring Forties Lows & Ocean Waves",
    "months": {
      "1": {
        "wind_prob": 90,
        "avg_kts": 26,
        "range": [
          20,
          38
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "The epicenter of world Big Air. Cape Doctor howling, massive kicker waves."
      },
      "2": {
        "wind_prob": 88,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 15,
        "air_temp": 27,
        "wetsuit": "4/3mm Steamer",
        "tip": "King of the Air vibes every afternoon in Blouberg and Kite Beach."
      },
      "3": {
        "wind_prob": 75,
        "avg_kts": 22,
        "range": [
          16,
          30
        ],
        "season": "good",
        "sea_temp": 15,
        "air_temp": 25,
        "wetsuit": "4/3mm Steamer",
        "tip": "Warm sunny days with solid afternoon winds and fun swells."
      },
      "4": {
        "wind_prob": 50,
        "avg_kts": 16,
        "range": [
          12,
          24
        ],
        "season": "shoulder",
        "sea_temp": 15,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Autumn sets in; big surf on west coast point breaks."
      },
      "5": {
        "wind_prob": 35,
        "avg_kts": 14,
        "range": [
          10,
          22
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm + Booties",
        "tip": "Off-season. Good for pure surfing and wine touring."
      },
      "6": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 14,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Winter storms with heavy NW winds and massive ocean swell."
      },
      "7": {
        "wind_prob": 30,
        "avg_kts": 14,
        "range": [
          10,
          24
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 17,
        "wetsuit": "4/3mm + Booties",
        "tip": "Cold winter conditions; occasional storm sessions."
      },
      "8": {
        "wind_prob": 38,
        "avg_kts": 15,
        "range": [
          11,
          23
        ],
        "season": "low",
        "sea_temp": 13,
        "air_temp": 18,
        "wetsuit": "4/3mm + Booties",
        "tip": "Spring slowly awakens with occasional SE thermal pulses."
      },
      "9": {
        "wind_prob": 52,
        "avg_kts": 18,
        "range": [
          13,
          27
        ],
        "season": "shoulder",
        "sea_temp": 14,
        "air_temp": 20,
        "wetsuit": "4/3mm Steamer",
        "tip": "Spring winds start firing in Langebaan and Table Bay."
      },
      "10": {
        "wind_prob": 70,
        "avg_kts": 22,
        "range": [
          16,
          32
        ],
        "season": "good",
        "sea_temp": 14,
        "air_temp": 22,
        "wetsuit": "4/3mm Steamer",
        "tip": "Season kick-off! Pros arrive, warm days and howling wind."
      },
      "11": {
        "wind_prob": 85,
        "avg_kts": 25,
        "range": [
          19,
          36
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 24,
        "wetsuit": "4/3mm Steamer",
        "tip": "Non-stop wind action. Pack small kites (7m, 8m, 9m)."
      },
      "12": {
        "wind_prob": 92,
        "avg_kts": 27,
        "range": [
          21,
          40
        ],
        "season": "peak",
        "sea_temp": 14,
        "air_temp": 26,
        "wetsuit": "4/3mm Steamer",
        "tip": "Nuclear Cape Doctor winds, huge beach buzz and late sunsets."
      }
    }
  }
]


def _load_custom_user_spots() -> list:
    """Load user-requested and auto-processed spots from persistent storage."""
    if not os.path.exists(USER_SPOTS_FILE):
        return []
    try:
        with open(USER_SPOTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[travel_db] Error loading custom user spots: {e}")
        return []

def _save_custom_user_spots(spots: list):
    """Save custom user spots to disk."""
    try:
        with open(USER_SPOTS_FILE, "w", encoding="utf-8") as f:
            json.dump(spots, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[travel_db] Error saving custom user spots: {e}")

def get_all_travel_spots() -> list:
    """Return all travel destinations (core curated spots + community requested spots)."""
    custom = _load_custom_user_spots()
    seen_ids = set()
    combined = []
    
    # Custom spots first so new requests are immediately discoverable
    for s in custom:
        sid = s.get("id")
        if sid and sid not in seen_ids:
            seen_ids.add(sid)
            combined.append(s)

    for s in CORE_TRAVEL_SPOTS:
        sid = s.get("id")
        if sid and sid not in seen_ids:
            seen_ids.add(sid)
            combined.append(s)

    # Sort primarily by Country, then by Spot Name
    combined.sort(key=lambda x: (x.get("country", "").lower(), x.get("name", "").lower()))
    return combined

def get_travel_countries_and_spots() -> dict:
    """
    Return spots grouped by country for clean 2-tier dropdown menus:
    {
      "Brazil": [ {id, name, short_name, flag, region}, ... ],
      "Dominican Republic": [ ... ]
    }
    """
    all_spots = get_all_travel_spots()
    countries = {}
    for s in all_spots:
        c = s.get("country") or "Other"
        if c not in countries:
            countries[c] = {
                "country": c,
                "country_code": s.get("country_code", "XX"),
                "flag": s.get("flag", "🌊"),
                "spots": []
            }
        countries[c]["spots"].append({
            "id": s.get("id"),
            "name": s.get("name"),
            "short_name": s.get("short_name"),
            "flag": s.get("flag"),
            "region": s.get("region"),
            "style_tags": s.get("style_tags", []),
            "prime_season": s.get("prime_season", "")
        })

    # Sort countries alphabetically
    sorted_countries = dict(sorted(countries.items(), key=lambda item: item[0].lower()))
    return sorted_countries

def get_spot_climatology(spot_id: str) -> dict:
    """Retrieve the full 12-month climatology profile for a specific spot."""
    if not spot_id:
        return {}
    spot_id = spot_id.strip().lower()
    for s in get_all_travel_spots():
        if s.get("id", "").lower() == spot_id:
            # Format months keys as ints
            s_copy = dict(s)
            m_dict = {}
            for k, v in s.get("months", {}).items():
                m_dict[int(k)] = v
            s_copy["months"] = m_dict
            return s_copy
    return {}

def explore_spots_by_month_and_style(month: int, style: str = "all") -> list:
    """
    Rank top spots worldwide for a given month, optionally filtered by style.
    Returns ranked list with reliability score, wind range, and travel verdict.
    """
    if month < 1 or month > 12:
        month = 1
    style = (style or "all").strip().lower()

    spots = get_all_travel_spots()
    ranked = []

    for s in spots:
        months_data = s.get("months", {})
        m_info = months_data.get(month) or months_data.get(str(month))
        if not m_info:
            continue

        style_tags = [t.lower() for t in s.get("style_tags", [])]
        if style != "all" and style not in style_tags:
            continue

        wind_prob = m_info.get("wind_prob", 0)
        avg_kts = m_info.get("avg_kts", 0)
        w_range = m_info.get("range", [14, 20])
        season = m_info.get("season", "good")

        score = wind_prob * 1.0 + (avg_kts * 0.5)

        ranked.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "short_name": s.get("short_name"),
            "country": s.get("country"),
            "country_code": s.get("country_code"),
            "flag": s.get("flag"),
            "region": s.get("region"),
            "style_tags": s.get("style_tags"),
            "prime_season": s.get("prime_season"),
            "water_type": s.get("water_type"),
            "month": month,
            "month_name": MONTH_NAMES[month - 1],
            "wind_prob": wind_prob,
            "avg_kts": avg_kts,
            "range": w_range,
            "season": season,
            "sea_temp": m_info.get("sea_temp"),
            "air_temp": m_info.get("air_temp"),
            "wetsuit": m_info.get("wetsuit"),
            "tip": m_info.get("tip"),
            "score": round(score, 1)
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked

def calculate_quiver_trip_recommendation(
    spot_id: str,
    month: int,
    rider_weight: float = 75.0,
    discipline: str = "Twintip",
    gear_inventory: list = None
) -> dict:
    """
    Calculate tailored quiver packing advice for a specific spot and month.
    Categorizes rider's gear into:
      - 'pack': Must-bring kites
      - 'leave_home': Kites unlikely to be used
      - 'gaps': Missing kite sizes recommended for this destination's wind profile.
    """
    spot = get_spot_climatology(spot_id)
    if not spot:
        # Default fallback to Cabarete
        spot = get_spot_climatology("cabarete")

    months_data = spot.get("months", {})
    m_info = months_data.get(month) or months_data.get(str(month)) or months_data.get(1)
    
    avg_kts = m_info.get("avg_kts", 18)
    w_min, w_max = m_info.get("range", [14, 22])
    wind_prob = m_info.get("wind_prob", 70)

    # Calculate optimal kite sizes for rider weight
    # Base 75kg twintip formula: optimal_size = 135 / wind_kts
    weight_factor = rider_weight / 75.0
    discipline_mult = 1.0
    disc_clean = (discipline or "twintip").lower()
    if "surf" in disc_clean or "wave" in disc_clean or "strapless" in disc_clean:
        discipline_mult = 0.82  # Surfboards need ~15-20% smaller kites
    elif "foil" in disc_clean:
        discipline_mult = 0.60  # Hydrofoils need ~40% smaller kites

    ideal_sweetspot_size = round((135.0 / max(10, avg_kts)) * weight_factor * discipline_mult, 1)
    ideal_highwind_size = round((135.0 / max(12, w_max)) * weight_factor * discipline_mult, 1)
    ideal_lightwind_size = round((135.0 / max(8, w_min)) * weight_factor * discipline_mult, 1)

    rec_min = min(ideal_highwind_size, ideal_sweetspot_size)
    rec_max = max(ideal_lightwind_size, ideal_sweetspot_size)

    pack_list = []
    leave_list = []
    gaps = []

    inventory = gear_inventory or []

    # Map inventory kites
    for item in inventory:
        try:
            size = float(item.get("size", 0))
            gear_type = item.get("type", "kite")
            gear_name = item.get("model") or item.get("name") or f"{size}m {gear_type.capitalize()}"

            # Check if within destination wind window (+/- 1.5m buffer)
            if (rec_min - 1.5) <= size <= (rec_max + 1.5):
                pack_list.append({
                    "id": item.get("id"),
                    "name": gear_name,
                    "size": size,
                    "type": gear_type,
                    "status": "pack",
                    "reason": f"Matches {w_min}-{w_max} kts expected wind at {spot.get('short_name', 'spot')}."
                })
            else:
                leave_list.append({
                    "id": item.get("id"),
                    "name": gear_name,
                    "size": size,
                    "type": gear_type,
                    "status": "leave_home",
                    "reason": f"Wind range unlikely needed ({'too large for strong breeze' if size > rec_max else 'too small for average conditions'})."
                })
        except Exception:
            continue

    # Gap detection: Check if rider is missing crucial sizes
    owned_sizes = [g.get("size") for g in pack_list]
    target_sizes = [round(ideal_highwind_size), round(ideal_sweetspot_size), round(ideal_lightwind_size)]
    target_sizes = sorted(list(set(target_sizes)))

    for ts in target_sizes:
        has_close = any(abs(owned - ts) <= 1.0 for owned in owned_sizes)
        if not has_close and ts >= 5:
            gaps.append({
                "size": ts,
                "urgency": "high" if abs(ts - ideal_sweetspot_size) <= 1.0 else "medium",
                "label": f"{ts}m Kite",
                "recommended_for": f"{avg_kts} kts {spot.get('short_name', 'spot')} sessions"
            })

    return {
        "spot": {
            "id": spot.get("id"),
            "name": spot.get("name"),
            "short_name": spot.get("short_name"),
            "country": spot.get("country"),
            "country_code": spot.get("country_code"),
            "flag": spot.get("flag"),
            "region": spot.get("region"),
            "water_type": spot.get("water_type"),
            "prime_season": spot.get("prime_season")
        },
        "month": month,
        "month_name": MONTH_NAMES[month - 1],
        "climate": m_info,
        "rider": {
            "weight_kg": rider_weight,
            "discipline": discipline
        },
        "ideal_quiver": {
            "sweetspot": ideal_sweetspot_size,
            "high_wind": ideal_highwind_size,
            "light_wind": ideal_lightwind_size,
            "recommended_range": f"{rec_min:.0f}m – {rec_max:.0f}m"
        },
        "quiver_advice": {
            "pack": pack_list,
            "leave_home": leave_list,
            "gaps": gaps
        }
    }

def slugify(text: str) -> str:
    """Create a clean url-friendly slug identifier."""
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "_", text)

def country_code_to_flag(code: str) -> str:
    """Convert 2-letter country code into flag emoji."""
    if not code or len(code) != 2:
        return "🌊"
    try:
        return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)
    except Exception:
        return "🌊"

def process_new_destination(query: str, user_name: str = "", user_email: str = "") -> dict:
    """
    Automated Cloud Engine:
    Takes any user destination query (e.g. 'Paracuru, Brazil' or 'Kite Beach Dubai'),
    geocodes the exact coordinates, pulls 12-month ECMWF ERA5 reanalysis data,
    computes wind probabilities, season labels, temperatures, and wetsuit requirements,
    and permanently registers the spot into user_travel_spots.json.
    """
    query = (query or "").strip()
    if not query:
        raise ValueError("Please provide a destination or spot name to request.")

    # 1. Geocode via Open-Meteo Geocoding API
    geo_query = query
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(geo_query)}&count=5&language=en&format=json"
    req = urllib.request.Request(geo_url, headers={"User-Agent": "HolyGust-KiteAssistant/2.0"})
    
    results = []
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            geo_data = json.loads(resp.read().decode("utf-8"))
            results = geo_data.get("results") or []
    except Exception as e:
        print(f"[travel_db] Geocoding primary failed for '{query}': {e}")

    # Fallback 1: if user wrote "Town, Country", try searching just "Town"
    if not results and "," in query:
        fallback_query = query.split(",")[0].strip()
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(fallback_query)}&count=5&language=en&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "HolyGust-KiteAssistant/2.0"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                geo_data = json.loads(resp.read().decode("utf-8"))
                results = geo_data.get("results") or []
        except Exception as e:
            print(f"[travel_db] Geocoding fallback 1 failed for '{fallback_query}': {e}")

    # Fallback 2: strip spot/beach keywords (e.g. "Kite Beach Dubai" -> "Dubai")
    if not results:
        cleaned = re.sub(r'(?i)\b(kite\s*beach|kitebeach|beach|playa|praia|lagoon|spot)\b', '', query).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ,')
        if cleaned and cleaned.lower() != query.lower():
            clean_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(cleaned)}&count=5&language=en&format=json"
            req_c = urllib.request.Request(clean_url, headers={"User-Agent": "HolyGust-KiteAssistant/2.0"})
            try:
                with urllib.request.urlopen(req_c, timeout=8) as resp:
                    geo_data = json.loads(resp.read().decode("utf-8"))
                    results = geo_data.get("results") or []
            except Exception as e:
                print(f"[travel_db] Geocoding fallback 2 failed for '{cleaned}': {e}")

    if not results:
        raise ValueError(f"Could not locate '{query}'. Please check spelling or specify the country (e.g. 'Paracuru, Brazil').")

    best = results[0]
    spot_name = best.get("name", query)
    country = best.get("country", "Global")
    country_code = (best.get("country_code") or "XX").upper()
    region = best.get("admin1") or best.get("admin2") or country
    lat = round(float(best.get("latitude")), 3)
    lon = round(float(best.get("longitude")), 3)
    flag = country_code_to_flag(country_code)

    # 2. Fetch or compute 12-month climatology
    months = {}
    archive_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&daily=windspeed_10m_max,windgusts_10m_max,temperature_2m_max&windspeed_unit=kn&timezone=auto"
    req_arch = urllib.request.Request(archive_url, headers={"User-Agent": "HolyGust-KiteAssistant/2.0"})
    
    use_reanalysis = False
    try:
        with urllib.request.urlopen(req_arch, timeout=10) as resp:
            arch_data = json.loads(resp.read().decode("utf-8"))
            daily = arch_data.get("daily", {})
            times = daily.get("time", [])
            winds = daily.get("windspeed_10m_max", [])
            temps = daily.get("temperature_2m_max", [])

            if len(times) >= 300:
                month_groups = {m: {"winds": [], "temps": []} for m in range(1, 13)}
                for t, w, temp in zip(times, winds, temps):
                    if w is not None and temp is not None:
                        m_num = int(t.split("-")[1])
                        month_groups[m_num]["winds"].append(w)
                        month_groups[m_num]["temps"].append(temp)

                for m_num in range(1, 13):
                    w_list = month_groups[m_num]["winds"]
                    t_list = month_groups[m_num]["temps"]
                    if w_list:
                        # Coastal venturi / thermal friction adjustment (+15%)
                        w_adj = [w * 1.15 for w in w_list]
                        avg_w = round(sum(w_adj) / len(w_adj))
                        prob = round((sum(1 for w in w_adj if w >= 14.0) / len(w_adj)) * 100)
                        prob = min(98, max(20, prob))
                        avg_w = max(13, min(32, avg_w))
                        r_min = max(10, int(avg_w * 0.75))
                        r_max = int(avg_w * 1.35)
                        avg_t = round(sum(t_list) / len(t_list)) if t_list else 24

                        # Sea temp estimation
                        abs_lat = abs(lat)
                        if abs_lat < 15:
                            sea_t = max(26, min(29, avg_t - 1))
                        elif abs_lat < 30:
                            sea_t = max(20, min(26, avg_t - 2))
                        elif abs_lat < 45:
                            sea_t = max(14, min(22, avg_t - 3))
                        else:
                            sea_t = max(8, min(17, avg_t - 4))

                        if prob >= 75:
                            season = "peak"
                        elif prob >= 55:
                            season = "good"
                        elif prob >= 35:
                            season = "shoulder"
                        else:
                            season = "low"

                        if sea_t >= 25:
                            wetsuit = "Boardshorts"
                        elif sea_t >= 20:
                            wetsuit = "Shorty 2mm"
                        elif sea_t >= 15:
                            wetsuit = "3/2mm Steamer"
                        else:
                            wetsuit = "4/3mm Steamer"

                        months[m_num] = {
                            "wind_prob": prob,
                            "avg_kts": avg_w,
                            "range": [r_min, r_max],
                            "season": season,
                            "sea_temp": sea_t,
                            "air_temp": avg_t,
                            "wetsuit": wetsuit,
                            "tip": f"Climatological wind averaging {avg_w} kts with {prob}% reliability."
                        }
                use_reanalysis = True
    except Exception as e:
        print(f"[travel_db] Reanalysis calculation failed, falling back to thermal model: {e}")

    if not use_reanalysis:
        # Fallback latitude-based trade wind / westerlies cycle
        is_southern = lat < 0
        for m_num in range(1, 13):
            month_idx = (m_num - 1 + (6 if is_southern else 0)) % 12
            base_prob = int(50 + 35 * abs(6 - month_idx) / 6.0)
            avg_w = int(15 + 8 * (base_prob / 100.0))
            sea_t = 26 if abs(lat) < 20 else (20 if abs(lat) < 35 else 14)
            months[m_num] = {
                "wind_prob": base_prob,
                "avg_kts": avg_w,
                "range": [max(12, int(avg_w * 0.75)), int(avg_w * 1.35)],
                "season": "peak" if base_prob >= 75 else ("good" if base_prob >= 50 else "shoulder"),
                "sea_temp": sea_t,
                "air_temp": 28 if abs(lat) < 20 else 22,
                "wetsuit": "Boardshorts" if sea_t >= 24 else ("3/2mm Steamer" if sea_t >= 15 else "4/3mm Steamer"),
                "tip": f"Consistent wind cycle averaging {avg_w} knots."
            }

    # Best season label
    best_months = [m for m, d in months.items() if d["season"] in ("peak", "good")]
    if len(best_months) >= 3:
        m_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        prime_season = f"{m_names[best_months[0]-1]} – {m_names[best_months[-1]-1]}"
    else:
        prime_season = "Year-Round Coastal Breeze"

    spot_id = slugify(f"{spot_name}_{country_code}")

    new_spot = {
        "id": spot_id,
        "name": f"{spot_name}, {country}",
        "short_name": spot_name,
        "country": country,
        "country_code": country_code,
        "flag": flag,
        "region": region,
        "lat": lat,
        "lon": lon,
        "style_tags": ["Freeride", "Big Air"],
        "prime_season": prime_season,
        "water_type": "Coastal Lagoon & Ocean Swell",
        "months": months,
        "custom": True,
        "requested_by": {
            "name": user_name,
            "email": user_email,
            "date": datetime.datetime.utcnow().isoformat()
        }
    }

    # Persist into user_travel_spots.json
    custom_spots = _load_custom_user_spots()
    # Replace existing or append
    custom_spots = [s for s in custom_spots if s.get("id") != spot_id]
    custom_spots.insert(0, new_spot)
    _save_custom_user_spots(custom_spots)

    return new_spot
