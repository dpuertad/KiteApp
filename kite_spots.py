"""
Comprehensive Global Kiteboarding & Wingfoil Spots Database
Contains top international and regional kite spots with exact coordinates,
coastline orientations, preferred regional high-res meteorological models,
and coastal thermal venturi characteristics.
"""

import math

GLOBAL_KITE_SPOTS = [
    # --- BRAZIL (CEARÁ & NORTHEAST TRADES) ---
    {
        "id": "cumbuco",
        "name": "Cumbuco, Brazil",
        "short_name": "Cumbuco",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -3.6247,
        "lon": -38.7297,
        "timezone": "America/Fortaleza",
        "beach_angle": 40.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Thermal Venturi",
        "thermal_boost": 0.16,
        "aliases": ["cumbuco", "duro beach", "caucaia"]
    },
    {
        "id": "taiba",
        "name": "Taíba, Brazil",
        "short_name": "Taíba",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -3.5042,
        "lon": -38.8953,
        "timezone": "America/Fortaleza",
        "beach_angle": 35.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Thermal Boost",
        "thermal_boost": 0.18,
        "aliases": ["taiba", "lagoa da taiba", "secret spot taiba"]
    },
    {
        "id": "paracuru",
        "name": "Paracuru (Quebra Mar), Brazil",
        "short_name": "Paracuru",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -3.4078,
        "lon": -39.0142,
        "timezone": "America/Fortaleza",
        "beach_angle": 20.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Coastal Reef Boost",
        "thermal_boost": 0.18,
        "aliases": ["paracuru", "quebra mar"]
    },
    {
        "id": "lagoinha",
        "name": "Lagoinha, Brazil",
        "short_name": "Lagoinha",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -3.3458,
        "lon": -39.1417,
        "timezone": "America/Fortaleza",
        "beach_angle": 350.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Dune Accel",
        "thermal_boost": 0.16,
        "aliases": ["lagoinha", "paracuru lagoinha"]
    },
    {
        "id": "flecheiras",
        "name": "Flecheiras (Trairi), Brazil",
        "short_name": "Flecheiras",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -3.2208,
        "lon": -39.2612,
        "timezone": "America/Fortaleza",
        "beach_angle": 50.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Reef Pass Boost",
        "thermal_boost": 0.18,
        "aliases": ["flecheiras", "guajiru trairi", "trairi", "mundau", "mundaú"]
    },
    {
        "id": "moitas",
        "name": "Moitas (Rio Aracatiaçu), Brazil",
        "short_name": "Moitas",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -2.9965,
        "lon": -39.6893,
        "timezone": "America/Fortaleza",
        "beach_angle": 60.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Estuary Venturi",
        "thermal_boost": 0.20,
        "aliases": ["moitas", "rio aracatiacu", "aracatiacu", "moitas ceara", "praia de moitas"]
    },
    {
        "id": "icaraizinho",
        "name": "Icaraí de Amontada (Icaraizinho), Brazil",
        "short_name": "Icaraizinho",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -3.0232,
        "lon": -39.6433,
        "timezone": "America/Fortaleza",
        "beach_angle": 55.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Bay Venturi",
        "thermal_boost": 0.18,
        "aliases": ["icarai de amontada", "icaraizinho", "amontada", "canto das aguas"]
    },
    {
        "id": "guajiru",
        "name": "Ilha do Guajirú, Brazil",
        "short_name": "Ilha do Guajirú",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -2.9833,
        "lon": -40.1167,
        "timezone": "America/Fortaleza",
        "beach_angle": 350.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Lagoon Chimney",
        "thermal_boost": 0.20,
        "aliases": ["ilha do guajiru", "itarema", "guajiru flat"]
    },
    {
        "id": "prea",
        "name": "Preá, Brazil",
        "short_name": "Preá",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -2.8139,
        "lon": -40.4189,
        "timezone": "America/Fortaleza",
        "beach_angle": 340.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Prea Trade Venturi",
        "thermal_boost": 0.20,
        "aliases": ["prea", "praia do prea"]
    },
    {
        "id": "jericoacoara",
        "name": "Jericoacoara, Brazil",
        "short_name": "Jericoacoara",
        "country": "Brazil",
        "region": "Ceará",
        "flag": "🇧🇷",
        "lat": -2.7958,
        "lon": -40.5142,
        "timezone": "America/Fortaleza",
        "beach_angle": 320.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Sunset Dune Venturi",
        "thermal_boost": 0.22,
        "aliases": ["jeri", "jericoacoara", "duna do por do sol"]
    },
    {
        "id": "macapa",
        "name": "Macapá (Delta), Brazil",
        "short_name": "Macapá",
        "country": "Brazil",
        "region": "Piauí",
        "flag": "🇧🇷",
        "lat": -2.9031,
        "lon": -41.5361,
        "timezone": "America/Fortaleza",
        "beach_angle": 330.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Delta Thermal",
        "thermal_boost": 0.18,
        "aliases": ["macapa", "luis correia"]
    },
    {
        "id": "barra_grande",
        "name": "Barra Grande (Piauí), Brazil",
        "short_name": "Barra Grande",
        "country": "Brazil",
        "region": "Piauí",
        "flag": "🇧🇷",
        "lat": -2.9150,
        "lon": -41.4420,
        "timezone": "America/Fortaleza",
        "beach_angle": 340.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Flatwater Thermal",
        "thermal_boost": 0.18,
        "aliases": ["barra grande", "bg"]
    },
    {
        "id": "atins",
        "name": "Atins (Lençóis), Brazil",
        "short_name": "Atins",
        "country": "Brazil",
        "region": "Maranhão",
        "flag": "🇧🇷",
        "lat": -2.5714,
        "lon": -42.7483,
        "timezone": "America/Fortaleza",
        "beach_angle": 350.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Lençóis Heating",
        "thermal_boost": 0.18,
        "aliases": ["atins", "lencois maranhenses"]
    },
    {
        "id": "sao_miguel_gostoso",
        "name": "São Miguel do Gostoso, Brazil",
        "short_name": "SM Gostoso",
        "country": "Brazil",
        "region": "Rio Grande do Norte",
        "flag": "🇧🇷",
        "lat": -5.1239,
        "lon": -35.6364,
        "timezone": "America/Fortaleza",
        "beach_angle": 20.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Trade Accelerator",
        "thermal_boost": 0.15,
        "aliases": ["gostoso", "sao miguel do gostoso", "ponta do santo cristo"]
    },
    {
        "id": "pipa",
        "name": "Tibau do Sul / Pipa, Brazil",
        "short_name": "Pipa",
        "country": "Brazil",
        "region": "Rio Grande do Norte",
        "flag": "🇧🇷",
        "lat": -6.1833,
        "lon": -35.0833,
        "timezone": "America/Fortaleza",
        "beach_angle": 80.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km)",
        "thermal_boost": 0.12,
        "aliases": ["pipa", "tibau do sul", "madeiro"]
    },
    {
        "id": "florianopolis",
        "name": "Florianópolis (Campeche), Brazil",
        "short_name": "Florianópolis",
        "country": "Brazil",
        "region": "Santa Catarina",
        "flag": "🇧🇷",
        "lat": -27.6833,
        "lon": -48.4833,
        "timezone": "America/Sao_Paulo",
        "beach_angle": 110.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km)",
        "thermal_boost": 0.10,
        "aliases": ["florianopolis", "floripa", "campeche", "lagoa da conceicao"]
    },
    {
        "id": "ibiraquera",
        "name": "Barra de Ibiraquera, Brazil",
        "short_name": "Ibiraquera",
        "country": "Brazil",
        "region": "Santa Catarina",
        "flag": "🇧🇷",
        "lat": -28.1458,
        "lon": -48.6472,
        "timezone": "America/Sao_Paulo",
        "beach_angle": 100.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Frontal Wave",
        "thermal_boost": 0.10,
        "aliases": ["ibiraquera", "barra de ibiraquera", "imbituba"]
    },

    # --- SPAIN & CANARY ISLANDS ---
    {
        "id": "tarifa",
        "name": "Tarifa (Los Lances), Spain",
        "short_name": "Tarifa",
        "country": "Spain",
        "region": "Andalusia",
        "flag": "🇪🇸",
        "lat": 36.0143,
        "lon": -5.6044,
        "timezone": "Europe/Madrid",
        "beach_angle": 220.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU (7km) / ECMWF + Strait Venturi",
        "thermal_boost": 0.20,
        "aliases": ["tarifa", "los lances", "cadiz"]
    },
    {
        "id": "valdevaqueros",
        "name": "Tarifa (Valdevaqueros), Spain",
        "short_name": "Valdevaqueros",
        "country": "Spain",
        "region": "Andalusia",
        "flag": "🇪🇸",
        "lat": 36.0711,
        "lon": -5.6914,
        "timezone": "Europe/Madrid",
        "beach_angle": 230.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU (7km) + Dune Acceleration",
        "thermal_boost": 0.22,
        "aliases": ["valdevaqueros", "spin out", "tumbao"]
    },
    {
        "id": "sotavento",
        "name": "Sotavento (Fuerteventura), Spain",
        "short_name": "Sotavento",
        "country": "Spain",
        "region": "Canary Islands",
        "flag": "🇪🇸",
        "lat": 28.1256,
        "lon": -14.2694,
        "timezone": "Atlantic/Canary",
        "beach_angle": 110.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Valley Venturi",
        "thermal_boost": 0.20,
        "aliases": ["sotavento", "fuerteventura", "costa calma", "rene egli"]
    },
    {
        "id": "el_cotillo",
        "name": "El Cotillo (Fuerteventura), Spain",
        "short_name": "El Cotillo",
        "country": "Spain",
        "region": "Canary Islands",
        "flag": "🇪🇸",
        "lat": 28.6833,
        "lon": -14.0167,
        "timezone": "Atlantic/Canary",
        "beach_angle": 310.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Atlantic Swell",
        "thermal_boost": 0.12,
        "aliases": ["el cotillo", "cotillo lagoons"]
    },
    {
        "id": "pozo",
        "name": "Pozo Izquierdo (Gran Canaria), Spain",
        "short_name": "Pozo Izquierdo",
        "country": "Spain",
        "region": "Canary Islands",
        "flag": "🇪🇸",
        "lat": 27.8184,
        "lon": -15.4243,
        "timezone": "Atlantic/Canary",
        "beach_angle": 90.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Trade Venturi",
        "thermal_boost": 0.20,
        "aliases": ["pozo", "pozo izquierdo", "gran canaria"]
    },
    {
        "id": "el_medano",
        "name": "El Médano (Tenerife), Spain",
        "short_name": "El Médano",
        "country": "Spain",
        "region": "Canary Islands",
        "flag": "🇪🇸",
        "lat": 28.0458,
        "lon": -16.5361,
        "timezone": "Atlantic/Canary",
        "beach_angle": 140.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Teide Thermal",
        "thermal_boost": 0.18,
        "aliases": ["el medano", "medano", "tenerife"]
    },
    {
        "id": "famara",
        "name": "Famara (Lanzarote), Spain",
        "short_name": "Famara",
        "country": "Spain",
        "region": "Canary Islands",
        "flag": "🇪🇸",
        "lat": 29.1167,
        "lon": -13.5500,
        "timezone": "Atlantic/Canary",
        "beach_angle": 320.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Cliff Venturi",
        "thermal_boost": 0.15,
        "aliases": ["famara", "caleta de famara", "lanzarote"]
    },
    {
        "id": "delta_ebro",
        "name": "Delta del Ebro (Riumar), Spain",
        "short_name": "Delta del Ebro",
        "country": "Spain",
        "region": "Catalonia",
        "flag": "🇪🇸",
        "lat": 40.7247,
        "lon": 0.8431,
        "timezone": "Europe/Madrid",
        "beach_angle": 110.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU (7km) + Mestral Boost",
        "thermal_boost": 0.18,
        "aliases": ["delta de l'ebre", "riumar", "trabucador"]
    },
    {
        "id": "roses",
        "name": "Sant Pere Pescador (Bay of Roses), Spain",
        "short_name": "Bay of Roses",
        "country": "Spain",
        "region": "Catalonia",
        "flag": "🇪🇸",
        "lat": 42.1889,
        "lon": 3.1028,
        "timezone": "Europe/Madrid",
        "beach_angle": 80.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU (7km) + Garbí Thermal",
        "thermal_boost": 0.20,
        "aliases": ["roses", "sant pere pescador", "costa brava"]
    },

    # --- SWITZERLAND & ALPINE LAKES ---
    {
        "id": "silvaplana",
        "name": "Lake Silvaplana, Switzerland",
        "short_name": "Silvaplana",
        "country": "Switzerland",
        "region": "Graubünden / Engadin",
        "flag": "🇨🇭",
        "lat": 46.4592,
        "lon": 9.7917,
        "timezone": "Europe/Zurich",
        "beach_angle": 50.0,
        "preferred_model": "icon_d2",
        "model_label": "ICON-D2 (2km Swiss High-Res) + Maloja Thermal",
        "thermal_boost": 0.30,
        "aliases": ["silvaplana", "engadin", "st moritz", "maloja"]
    },
    {
        "id": "lake_uri",
        "name": "Flüelen (Lake Uri), Switzerland",
        "short_name": "Lake Uri",
        "country": "Switzerland",
        "region": "Uri / Lake Lucerne",
        "flag": "🇨🇭",
        "lat": 46.9039,
        "lon": 8.6258,
        "timezone": "Europe/Zurich",
        "beach_angle": 350.0,
        "preferred_model": "icon_d2",
        "model_label": "ICON-D2 (2km Swiss High-Res) + Föhn Thermal",
        "thermal_boost": 0.25,
        "aliases": ["lake uri", "urnersee", "fluelen", "isleten"]
    },
    {
        "id": "lake_neuchatel",
        "name": "Yvonand (Lake Neuchâtel), Switzerland",
        "short_name": "Lake Neuchâtel",
        "country": "Switzerland",
        "region": "Vaud / Neuchâtel",
        "flag": "🇨🇭",
        "lat": 46.8042,
        "lon": 6.7417,
        "timezone": "Europe/Zurich",
        "beach_angle": 310.0,
        "preferred_model": "icon_d2",
        "model_label": "ICON-D2 (2km High-Res) + Bise Boost",
        "thermal_boost": 0.15,
        "aliases": ["yvonand", "neuchatel", "portalban", "saint blaise"]
    },
    {
        "id": "garda",
        "name": "Torbole (Lake Garda), Italy",
        "short_name": "Lake Garda",
        "country": "Italy",
        "region": "Trentino / Alps",
        "flag": "🇮🇹",
        "lat": 45.8711,
        "lon": 10.8756,
        "timezone": "Europe/Rome",
        "beach_angle": 200.0,
        "preferred_model": "icon_d2",
        "model_label": "ICON-D2 (2km Alpine High-Res) + Ora Thermal",
        "thermal_boost": 0.25,
        "aliases": ["garda", "torbole", "malcesine", "riva del garda"]
    },
    {
        "id": "lake_como",
        "name": "Colico (Lake Como), Italy",
        "short_name": "Lake Como",
        "country": "Italy",
        "region": "Lombardy / Alps",
        "flag": "🇮🇹",
        "lat": 46.1333,
        "lon": 9.3667,
        "timezone": "Europe/Rome",
        "beach_angle": 190.0,
        "preferred_model": "icon_d2",
        "model_label": "ICON-D2 (2km Alpine High-Res) + Breva Thermal",
        "thermal_boost": 0.25,
        "aliases": ["como", "colico", "gera lario", "dervio"]
    },

    # --- FRANCE ---
    {
        "id": "leucate",
        "name": "Leucate / La Franqui, France",
        "short_name": "Leucate",
        "country": "France",
        "region": "Occitanie",
        "flag": "🇫🇷",
        "lat": 42.9094,
        "lon": 3.0278,
        "timezone": "Europe/Paris",
        "beach_angle": 110.0,
        "preferred_model": "best_match",
        "model_label": "AROME (1.5km French High-Res) + Tramontana",
        "thermal_boost": 0.18,
        "aliases": ["leucate", "la franqui", "plage des coussoules", "wesh center"]
    },
    {
        "id": "almanarre",
        "name": "Hyères (L'Almanarre), France",
        "short_name": "Hyères Almanarre",
        "country": "France",
        "region": "Provence-Alpes-Côte d'Azur",
        "flag": "🇫🇷",
        "lat": 43.0806,
        "lon": 6.1306,
        "timezone": "Europe/Paris",
        "beach_angle": 270.0,
        "preferred_model": "best_match",
        "model_label": "AROME (1.5km) + Mistral Acceleration",
        "thermal_boost": 0.20,
        "aliases": ["hyeres", "almanarre", "presqu'ile de giens"]
    },

    # --- EGYPT & MOROCCO ---
    {
        "id": "dakhla",
        "name": "Dakhla (Lagoon), Morocco",
        "short_name": "Dakhla",
        "country": "Morocco",
        "region": "Western Sahara",
        "flag": "🇲🇦",
        "lat": 23.7136,
        "lon": -15.9355,
        "timezone": "Africa/Casablanca",
        "beach_angle": 270.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Sahara Desert Thermal",
        "thermal_boost": 0.20,
        "aliases": ["dakhla", "pk25", "speed spot", "white dune", "dakhla attitude"]
    },
    {
        "id": "essaouira",
        "name": "Essaouira, Morocco",
        "short_name": "Essaouira",
        "country": "Morocco",
        "region": "Marrakech-Safi",
        "flag": "🇲🇦",
        "lat": 31.5125,
        "lon": -9.7700,
        "timezone": "Africa/Casablanca",
        "beach_angle": 280.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Alizé Trade",
        "thermal_boost": 0.18,
        "aliases": ["essaouira", "sidi kaouki", "moulay"]
    },
    {
        "id": "el_gouna",
        "name": "El Gouna (Mangroovy), Egypt",
        "short_name": "El Gouna",
        "country": "Egypt",
        "region": "Red Sea",
        "flag": "🇪🇬",
        "lat": 27.4042,
        "lon": 33.6825,
        "timezone": "Africa/Cairo",
        "beach_angle": 80.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Red Sea Channel",
        "thermal_boost": 0.18,
        "aliases": ["el gouna", "mangroovy", "red sea zone", "sliders"]
    },
    {
        "id": "soma_bay",
        "name": "Soma Bay, Egypt",
        "short_name": "Soma Bay",
        "country": "Egypt",
        "region": "Red Sea",
        "flag": "🇪🇬",
        "lat": 26.8500,
        "lon": 33.9833,
        "timezone": "Africa/Cairo",
        "beach_angle": 70.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Desert Thermal",
        "thermal_boost": 0.18,
        "aliases": ["soma bay", "safaga", "7bft"]
    },

    # --- GREECE & ITALY ---
    {
        "id": "prasonisi",
        "name": "Prasonisi (Rhodes), Greece",
        "short_name": "Prasonisi",
        "country": "Greece",
        "region": "Dodecanese",
        "flag": "🇬🇷",
        "lat": 35.8833,
        "lon": 27.7667,
        "timezone": "Europe/Athens",
        "beach_angle": 130.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU / ECMWF + Meltemi Channel",
        "thermal_boost": 0.20,
        "aliases": ["prasonisi", "rhodes", "rodos"]
    },
    {
        "id": "paros",
        "name": "Pounda (Paros), Greece",
        "short_name": "Paros Pounda",
        "country": "Greece",
        "region": "Cyclades",
        "flag": "🇬🇷",
        "lat": 37.0472,
        "lon": 25.1056,
        "timezone": "Europe/Athens",
        "beach_angle": 270.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU / ECMWF + Antiparos Strait",
        "thermal_boost": 0.22,
        "aliases": ["paros", "pounda", "antiparos"]
    },
    {
        "id": "lefkada",
        "name": "Milos / Agios Ioannis (Lefkada), Greece",
        "short_name": "Lefkada",
        "country": "Greece",
        "region": "Ionian Islands",
        "flag": "🇬🇷",
        "lat": 38.8333,
        "lon": 20.6833,
        "timezone": "Europe/Athens",
        "beach_angle": 310.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU / ECMWF + Ionian Thermal",
        "thermal_boost": 0.22,
        "aliases": ["lefkada", "agios ioannis", "milos beach"]
    },
    {
        "id": "stagnone",
        "name": "Lo Stagnone (Sicily), Italy",
        "short_name": "Lo Stagnone",
        "country": "Italy",
        "region": "Sicily",
        "flag": "🇮🇹",
        "lat": 37.8667,
        "lon": 12.4667,
        "timezone": "Europe/Rome",
        "beach_angle": 270.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU / ECMWF + Shallow Basin Thermal",
        "thermal_boost": 0.20,
        "aliases": ["stagnone", "marsala", "sicily", "birgi"]
    },
    {
        "id": "porto_pollo",
        "name": "Porto Pollo (Sardinia), Italy",
        "short_name": "Porto Pollo",
        "country": "Italy",
        "region": "Sardinia",
        "flag": "🇮🇹",
        "lat": 41.1944,
        "lon": 9.3194,
        "timezone": "Europe/Rome",
        "beach_angle": 330.0,
        "preferred_model": "icon_eu",
        "model_label": "ICON-EU / ECMWF + Bonifacio Strait Venturi",
        "thermal_boost": 0.22,
        "aliases": ["porto pollo", "sardinia", "palau"]
    },

    # --- SOUTH AFRICA ---
    {
        "id": "cape_town",
        "name": "Cape Town (Bloubergstrand), South Africa",
        "short_name": "Cape Town",
        "country": "South Africa",
        "region": "Western Cape",
        "flag": "🇿🇦",
        "lat": -33.8167,
        "lon": 18.4667,
        "timezone": "Africa/Johannesburg",
        "beach_angle": 260.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Cape Doctor Ridge Venturi",
        "thermal_boost": 0.22,
        "aliases": ["cape town", "blouberg", "bloubergstrand", "dolphin beach", "big bay", "kitebeach ct"]
    },
    {
        "id": "langebaan",
        "name": "Langebaan (Shark Bay), South Africa",
        "short_name": "Langebaan",
        "country": "South Africa",
        "region": "Western Cape",
        "flag": "🇿🇦",
        "lat": -33.0900,
        "lon": 18.0333,
        "timezone": "Africa/Johannesburg",
        "beach_angle": 240.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + West Coast Lagoon Thermal",
        "thermal_boost": 0.20,
        "aliases": ["langebaan", "shark bay", "main beach langebaan"]
    },

    # --- AMERICAS & CARIBBEAN ---
    {
        "id": "cabarete",
        "name": "Cabarete (Kite Beach), Dominican Republic",
        "short_name": "Cabarete",
        "country": "Dominican Republic",
        "region": "Puerto Plata",
        "flag": "🇩🇴",
        "lat": 19.7583,
        "lon": -70.4372,
        "timezone": "America/Santo_Domingo",
        "beach_angle": 20.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Atlantic Sea Breeze",
        "thermal_boost": 0.18,
        "aliases": ["cabarete", "kite beach cabarete", "bozo beach"]
    },
    {
        "id": "maui",
        "name": "Maui (Kanaha Beach), Hawaii",
        "short_name": "Maui (Kanaha)",
        "country": "United States",
        "region": "Hawaii",
        "flag": "🇺🇸",
        "lat": 20.8986,
        "lon": -156.4422,
        "timezone": "Pacific/Honolulu",
        "beach_angle": 20.0,
        "preferred_model": "best_match",
        "model_label": "GFS (13km) + Haleakala Valley Venturi",
        "thermal_boost": 0.22,
        "aliases": ["maui", "kanaha", "kite beach maui", "kahului"]
    },
    {
        "id": "hood_river",
        "name": "Hood River (The Gorge), USA",
        "short_name": "Hood River",
        "country": "United States",
        "region": "Oregon",
        "flag": "🇺🇸",
        "lat": 45.7139,
        "lon": -121.5083,
        "timezone": "America/Los_Angeles",
        "beach_angle": 0.0,
        "preferred_model": "best_match",
        "model_label": "HRRR (3km High-Res) + Gorge Pressure Venturi",
        "thermal_boost": 0.30,
        "aliases": ["hood river", "the gorge", "columbia river gorge", "event site"]
    },
    {
        "id": "la_ventana",
        "name": "La Ventana (Baja), Mexico",
        "short_name": "La Ventana",
        "country": "Mexico",
        "region": "Baja California Sur",
        "flag": "🇲🇽",
        "lat": 24.0531,
        "lon": -109.9989,
        "timezone": "America/Hermosillo",
        "beach_angle": 60.0,
        "preferred_model": "best_match",
        "model_label": "HRRR / GFS + Sea of Cortez Thermal",
        "thermal_boost": 0.25,
        "aliases": ["la ventana", "baja", "los barriles", "el sargento"]
    },
    {
        "id": "hatteras",
        "name": "Cape Hatteras (Kite Point), USA",
        "short_name": "Cape Hatteras",
        "country": "United States",
        "region": "North Carolina",
        "flag": "🇺🇸",
        "lat": 35.2500,
        "lon": -75.5333,
        "timezone": "America/New_York",
        "beach_angle": 120.0,
        "preferred_model": "best_match",
        "model_label": "HRRR (3km High-Res) + Pamlico Sound",
        "thermal_boost": 0.15,
        "aliases": ["hatteras", "outer banks", "obx", "waves", "rodanthe"]
    },
    {
        "id": "st_pete",
        "name": "St. Petersburg (Skyway), USA",
        "short_name": "St. Pete Skyway",
        "country": "United States",
        "region": "Florida",
        "flag": "🇺🇸",
        "lat": 27.6333,
        "lon": -82.6500,
        "timezone": "America/New_York",
        "beach_angle": 210.0,
        "preferred_model": "best_match",
        "model_label": "HRRR (3km High-Res) + Tampa Bay",
        "thermal_boost": 0.15,
        "aliases": ["st pete", "skyway", "tampa bay", "fort de soto"]
    },

    # --- ASIA & INDIAN OCEAN ---
    {
        "id": "le_morne",
        "name": "Le Morne (Kite Lagoon), Mauritius",
        "short_name": "Le Morne",
        "country": "Mauritius",
        "region": "Black River",
        "flag": "🇲🇺",
        "lat": -20.4500,
        "lon": 57.3167,
        "timezone": "Indian/Mauritius",
        "beach_angle": 240.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Brabant Mountain Venturi",
        "thermal_boost": 0.20,
        "aliases": ["le morne", "one eye", "kite lagoon", "mauritius"]
    },
    {
        "id": "kalpitiya",
        "name": "Kalpitiya Lagoon, Sri Lanka",
        "short_name": "Kalpitiya",
        "country": "Sri Lanka",
        "region": "North Western Province",
        "flag": "🇱🇰",
        "lat": 8.2333,
        "lon": 79.7667,
        "timezone": "Asia/Colombo",
        "beach_angle": 270.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Monsoon Venturi",
        "thermal_boost": 0.20,
        "aliases": ["kalpitiya", "sri lanka", "kappalady"]
    },
    {
        "id": "boracay",
        "name": "Boracay (Bulabog Beach), Philippines",
        "short_name": "Boracay",
        "country": "Philippines",
        "region": "Aklan",
        "flag": "🇵🇭",
        "lat": 11.9667,
        "lon": 121.9333,
        "timezone": "Asia/Manila",
        "beach_angle": 90.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Amihan Trade",
        "thermal_boost": 0.15,
        "aliases": ["boracay", "bulabog", "bulabog beach"]
    },
    {
        "id": "mui_ne",
        "name": "Mui Ne, Vietnam",
        "short_name": "Mui Ne",
        "country": "Vietnam",
        "region": "Bình Thuận",
        "flag": "🇻🇳",
        "lat": 10.9333,
        "lon": 108.2833,
        "timezone": "Asia/Ho_Chi_Minh",
        "beach_angle": 140.0,
        "preferred_model": "best_match",
        "model_label": "ECMWF (9km) + Coastal Sand Venturi",
        "thermal_boost": 0.18,
        "aliases": ["mui ne", "vietnam", "phan thiet"]
    }
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS points in kilometers."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 1)


def find_spots_near_gps(lat: float, lon: float, max_spots: int = 10) -> list:
    """
    Returns spots from the catalog sorted by distance from the rider's coordinates.
    Guarantees that spots around you are shown first.
    """
    ranked = []
    for spot in GLOBAL_KITE_SPOTS:
        dist = haversine_distance_km(lat, lon, spot["lat"], spot["lon"])
        s_copy = dict(spot)
        s_copy["distance_km"] = dist
        ranked.append(s_copy)

    ranked.sort(key=lambda s: s["distance_km"])
    return ranked[:max_spots]


def search_spots_catalog(query: str, max_results: int = 15) -> list:
    """Searches predefined kite spots across name, country, region, and aliases."""
    if not query:
        return GLOBAL_KITE_SPOTS[:max_results]
    
    q = query.strip().lower()
    matches = []
    for spot in GLOBAL_KITE_SPOTS:
        name_clean = spot["name"].lower()
        country_clean = spot["country"].lower()
        region_clean = spot["region"].lower()
        aliases = [a.lower() for a in spot.get("aliases", [])]

        score = 0
        if q == spot["id"]:
            score = 100
        elif q in name_clean:
            score = 80
        elif any(q in a for a in aliases):
            score = 70
        elif q in country_clean or q in region_clean:
            score = 50

        if score > 0:
            s_copy = dict(spot)
            s_copy["match_score"] = score
            matches.append(s_copy)

    matches.sort(key=lambda s: -s["match_score"])
    return matches[:max_results]
