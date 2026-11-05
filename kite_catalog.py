"""
Comprehensive Kite Model, Brand, Material & Wind Range Catalog
Calibrated for realistic Twintip freeride planing and upwind performance (75kg reference rider).
Includes aerodynamic scaling and hydrodynamic waterstart/planing factors.
"""

KITE_CATALOG = {
    "Gong": {
        "Ayto": {
            "type": "5-Strut High-Performance Big Air / Booster",
            "material": "Aramid / Boom Airframe",
            "sizes": {
                6: {"min": 22, "sweet": (25, 36), "max": 42},
                7: {"min": 20, "sweet": (23, 33), "max": 40},
                8: {"min": 18, "sweet": (21, 30), "max": 37},
                9: {"min": 16, "sweet": (19, 27), "max": 34},
                10: {"min": 14, "sweet": (17, 25), "max": 32},
                11: {"min": 13, "sweet": (15, 23), "max": 30},
                12: {"min": 12, "sweet": (14, 21), "max": 27},
            }
        },
        "Vertigo": {
            "type": "3-Strut All-Round Freeride / Jumping",
            "material": "Dacron DP175LL",
            "sizes": {
                5: {"min": 24, "sweet": (27, 37), "max": 42},
                7: {"min": 20, "sweet": (23, 31), "max": 38},
                9: {"min": 16, "sweet": (19, 27), "max": 34},
                11: {"min": 13, "sweet": (15, 23), "max": 29},
                13: {"min": 11, "sweet": (13, 19), "max": 25},
            }
        },
        "Elips": {
            "type": "3-Strut Wave / Drift / Foil",
            "material": "Teijin T9669 Triple Ripstop",
            "sizes": {
                5: {"min": 24, "sweet": (27, 36), "max": 40},
                6: {"min": 21, "sweet": (24, 33), "max": 37},
                7: {"min": 19, "sweet": (22, 30), "max": 35},
                8: {"min": 17, "sweet": (20, 27), "max": 33},
                9: {"min": 15, "sweet": (18, 25), "max": 31},
                10: {"min": 13, "sweet": (16, 23), "max": 28},
            }
        },
        "Strutless": {
            "type": "0-Strut Ultra-Lightwind & Hydrofoil",
            "material": "Ultra-Light 2D Tech",
            "sizes": {
                7: {"min": 17, "sweet": (20, 28), "max": 33},
                9: {"min": 14, "sweet": (17, 24), "max": 29},
                11: {"min": 11.5, "sweet": (13.5, 20), "max": 25},
                13: {"min": 9.5, "sweet": (11.5, 17), "max": 22},
                15: {"min": 8.5, "sweet": (10, 15), "max": 20},
                17: {"min": 7.5, "sweet": (9, 13.5), "max": 18},
            }
        },
        "Freewave": {
            "type": "3-Strut Freeride / Wave Crossover",
            "material": "Standard Dacron",
            "sizes": {
                5: {"min": 24, "sweet": (27, 36), "max": 41},
                7: {"min": 20, "sweet": (23, 31), "max": 37},
                9: {"min": 16, "sweet": (19, 26), "max": 33},
                11: {"min": 13, "sweet": (15, 22), "max": 28},
            }
        }
    },
    "Duotone": {
        "Rebel SLS": {
            "type": "5-Strut High-Performance Big Air",
            "material": "Penta TX (SLS)",
            "sizes": {
                6: {"min": 22, "sweet": (26, 36), "max": 42},
                7: {"min": 20, "sweet": (23, 33), "max": 40},
                8: {"min": 18, "sweet": (21, 30), "max": 37},
                9: {"min": 16, "sweet": (19, 27), "max": 34},
                10: {"min": 14, "sweet": (17, 25), "max": 32},
                11: {"min": 13, "sweet": (15, 23), "max": 30},
                12: {"min": 12, "sweet": (14, 21), "max": 27},
                13: {"min": 11, "sweet": (13, 19), "max": 25},
                14: {"min": 10, "sweet": (12, 17), "max": 23},
            }
        },
        "Rebel D/LAB": {
            "type": "5-Strut Extreme Big Air / Aluula",
            "material": "Aluula Airframe (D/LAB)",
            "sizes": {
                7: {"min": 18, "sweet": (22, 33), "max": 40},
                8: {"min": 16, "sweet": (20, 31), "max": 38},
                9: {"min": 14.5, "sweet": (18, 28), "max": 35},
                10: {"min": 13, "sweet": (16, 25), "max": 33},
                11: {"min": 12, "sweet": (14, 23), "max": 30},
                12: {"min": 11, "sweet": (13, 21), "max": 28},
            }
        },
        "Evo": {
            "type": "3-Strut All-Round Freeride",
            "material": "Standard Dacron",
            "sizes": {
                7: {"min": 20, "sweet": (23, 31), "max": 38},
                8: {"min": 18, "sweet": (21, 29), "max": 36},
                9: {"min": 16, "sweet": (19, 27), "max": 34},
                10: {"min": 14, "sweet": (17, 25), "max": 32},
                11: {"min": 13, "sweet": (15, 23), "max": 29},
                12: {"min": 12, "sweet": (14, 21), "max": 27},
            }
        },
        "Evo SLS": {
            "type": "3-Strut All-Round Performance",
            "material": "Penta TX (SLS)",
            "sizes": {
                7: {"min": 19, "sweet": (22, 31), "max": 39},
                8: {"min": 17, "sweet": (20, 29), "max": 37},
                9: {"min": 15, "sweet": (18, 27), "max": 35},
                10: {"min": 13.5, "sweet": (16, 25), "max": 33},
                11: {"min": 12, "sweet": (14, 23), "max": 30},
                12: {"min": 11, "sweet": (13, 21), "max": 28},
            }
        },
        "Evo D/LAB": {
            "type": "3-Strut Ultimate Freeride / Aluula",
            "material": "Aluula Airframe (D/LAB)",
            "sizes": {
                7: {"min": 17, "sweet": (21, 31), "max": 39},
                8: {"min": 15, "sweet": (19, 29), "max": 37},
                9: {"min": 13.5, "sweet": (17, 27), "max": 35},
                10: {"min": 12, "sweet": (15, 25), "max": 33},
                11: {"min": 11, "sweet": (13, 22), "max": 30},
                12: {"min": 10, "sweet": (12, 20), "max": 28},
            }
        },
        "Dice SLS": {
            "type": "3-Strut Freestyle / C-Hybrid",
            "material": "Penta TX (SLS)",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 40},
                7: {"min": 20, "sweet": (23, 32), "max": 38},
                8: {"min": 18, "sweet": (21, 30), "max": 36},
                9: {"min": 16, "sweet": (19, 28), "max": 34},
                10: {"min": 14, "sweet": (17, 25), "max": 32},
                11: {"min": 13, "sweet": (15, 22), "max": 29},
                12: {"min": 12, "sweet": (14, 20), "max": 26},
            }
        },
        "Neo SLS": {
            "type": "3-Strut Wave / Strapless",
            "material": "Penta TX (SLS)",
            "sizes": {
                5: {"min": 25, "sweet": (28, 38), "max": 42},
                6: {"min": 22, "sweet": (25, 34), "max": 39},
                7: {"min": 19, "sweet": (22, 31), "max": 36},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 32},
                10: {"min": 13, "sweet": (16, 24), "max": 30},
                11: {"min": 12, "sweet": (14, 21), "max": 27},
                12: {"min": 11, "sweet": (13, 19), "max": 24},
            }
        },
        "Juice D/LAB": {
            "type": "3-Strut Light Wind Specialist",
            "material": "Aluula (D/LAB)",
            "sizes": {
                13: {"min": 9, "sweet": (11, 17), "max": 21},
                14: {"min": 8.5, "sweet": (10, 16), "max": 20},
                15: {"min": 8, "sweet": (9.5, 15), "max": 19},
                17: {"min": 7.5, "sweet": (9, 14), "max": 18},
            }
        }
    },
    "Harlem": {
        "Thrive V1": {
            "type": "3-Strut All-Round / Wave / Progression",
            "material": "Brainchild PRO Weld / Eco Fabric",
            "sizes": {
                5: {"min": 24, "sweet": (28, 38), "max": 42},
                6: {"min": 21, "sweet": (25, 35), "max": 40},
                7: {"min": 19, "sweet": (22, 32), "max": 38},
                8: {"min": 17, "sweet": (20, 30), "max": 36},
                9: {"min": 15, "sweet": (18, 27), "max": 34},
                10: {"min": 13.5, "sweet": (16, 25), "max": 32},
                11: {"min": 12.5, "sweet": (15, 23), "max": 29},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 27},
                13: {"min": 10.5, "sweet": (12.5, 19), "max": 24},
                15: {"min": 9.5, "sweet": (11, 17), "max": 22},
            }
        },
        "Thrive": {
            "type": "3-Strut All-Round / Wave / Progression",
            "material": "Brainchild PRO Weld",
            "sizes": {
                7: {"min": 19, "sweet": (22, 32), "max": 38},
                8: {"min": 17, "sweet": (20, 30), "max": 36},
                9: {"min": 15, "sweet": (18, 27), "max": 34},
                10: {"min": 13.5, "sweet": (16, 25), "max": 32},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 27},
            }
        },
        "Force": {
            "type": "3-Strut Big Air / Boop Machine",
            "material": "PRO Titanium / Brainchild",
            "sizes": {
                6: {"min": 21, "sweet": (25, 36), "max": 42},
                7: {"min": 18, "sweet": (22, 34), "max": 40},
                8: {"min": 16, "sweet": (20, 32), "max": 38},
                9: {"min": 14, "sweet": (18, 29), "max": 35},
                10: {"min": 12.5, "sweet": (16, 26), "max": 32},
                11: {"min": 11.5, "sweet": (14.5, 24), "max": 29},
                12: {"min": 10.5, "sweet": (13, 22), "max": 27},
            }
        },
        "Pace": {
            "type": "3-Strut Freeride / Progression",
            "material": "Brainchild Weld Tech",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 36},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 32},
                10: {"min": 13.5, "sweet": (16, 24), "max": 30},
                12: {"min": 11.5, "sweet": (13.5, 20), "max": 26},
                14: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        },
        "Light": {
            "type": "Light Wind Freeride / Foil",
            "material": "Ultra-light Brainchild Fabric",
            "sizes": {
                13: {"min": 9.5, "sweet": (11.5, 17), "max": 22},
                15: {"min": 8.5, "sweet": (10.5, 16), "max": 20},
                17: {"min": 8, "sweet": (9.5, 14.5), "max": 18},
            }
        }
    },
    "Core": {
        "XR8": {
            "type": "5-Strut Big Air / High Aspect",
            "material": "ExoTex 2 / CoreTex 2",
            "sizes": {
                6: {"min": 21, "sweet": (25, 36), "max": 41},
                7: {"min": 19, "sweet": (23, 33), "max": 39},
                8: {"min": 17, "sweet": (20, 30), "max": 36},
                9: {"min": 15, "sweet": (18, 27), "max": 33},
                10: {"min": 13.5, "sweet": (16, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15, 23), "max": 29},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 27},
                13.5: {"min": 10, "sweet": (12, 18), "max": 24},
                15: {"min": 9, "sweet": (11, 16), "max": 22},
                17: {"min": 8, "sweet": (10, 15), "max": 20},
            }
        },
        "XR Pro": {
            "type": "5-Strut Extreme Big Air / Aluula",
            "material": "Aluula Black Airframe",
            "sizes": {
                6: {"min": 20, "sweet": (24, 37), "max": 43},
                7: {"min": 18, "sweet": (22, 34), "max": 40},
                8: {"min": 16, "sweet": (19, 31), "max": 38},
                9: {"min": 14, "sweet": (17, 28), "max": 35},
                10: {"min": 12.5, "sweet": (15, 26), "max": 33},
                12: {"min": 10.5, "sweet": (13, 22), "max": 28},
            }
        },
        "Nexus 3": {
            "type": "3-Strut Universal Freeride/Wave",
            "material": "ExoTex 2",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 40},
                7: {"min": 19, "sweet": (22, 31), "max": 37},
                8: {"min": 17, "sweet": (20, 29), "max": 35},
                9: {"min": 15, "sweet": (18, 26), "max": 32},
                10: {"min": 13.5, "sweet": (16, 24), "max": 30},
                11: {"min": 12, "sweet": (14.5, 22), "max": 28},
                12: {"min": 11, "sweet": (13, 20), "max": 26},
            }
        },
        "Pace Pro": {
            "type": "3-Strut High-Performance Big Air",
            "material": "Aluula 3-Strut Airframe",
            "sizes": {
                6: {"min": 21, "sweet": (25, 37), "max": 43},
                7: {"min": 18.5, "sweet": (22, 34), "max": 40},
                8: {"min": 16.5, "sweet": (20, 31), "max": 38},
                9: {"min": 14.5, "sweet": (17.5, 28), "max": 35},
                10: {"min": 13, "sweet": (15.5, 25), "max": 32},
                12: {"min": 11, "sweet": (13, 22), "max": 28},
            }
        }
    },
    "North": {
        "Orbit": {
            "type": "5-Strut Big Air / Looper",
            "material": "N-HTYR / N-Force",
            "sizes": {
                6: {"min": 22, "sweet": (26, 38), "max": 43},
                7: {"min": 20, "sweet": (23, 34), "max": 40},
                8: {"min": 18, "sweet": (21, 32), "max": 38},
                9: {"min": 16, "sweet": (19, 29), "max": 35},
                10: {"min": 14, "sweet": (17, 26), "max": 32},
                11: {"min": 13, "sweet": (15, 24), "max": 29},
                12: {"min": 12, "sweet": (14, 22), "max": 27},
            }
        },
        "Orbit Pro": {
            "type": "5-Strut Competition Big Air",
            "material": "N-Max / Aluula Composite",
            "sizes": {
                7: {"min": 18.5, "sweet": (22, 34), "max": 41},
                8: {"min": 16.5, "sweet": (20, 32), "max": 39},
                9: {"min": 14.5, "sweet": (18, 29), "max": 36},
                10: {"min": 13, "sweet": (16, 26), "max": 33},
                11: {"min": 12, "sweet": (14.5, 24), "max": 30},
            }
        },
        "Reach": {
            "type": "3-Strut All-Round Freeride",
            "material": "N-HTYR Performance Dacron",
            "sizes": {
                6: {"min": 21, "sweet": (24, 32), "max": 36},
                7: {"min": 19, "sweet": (22, 29), "max": 34},
                8: {"min": 17, "sweet": (20, 27), "max": 32},
                9: {"min": 15, "sweet": (18, 25), "max": 30},
                10: {"min": 13.5, "sweet": (16, 23), "max": 28},
                11: {"min": 12, "sweet": (14.5, 21), "max": 26},
                12: {"min": 11, "sweet": (13, 19), "max": 24},
                13: {"min": 10, "sweet": (12, 17), "max": 22},
                15: {"min": 9, "sweet": (10.5, 15.5), "max": 20},
            }
        },
        "Carve": {
            "type": "3-Strut Wave / Strapless",
            "material": "Performance Dacron",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 40},
                7: {"min": 19, "sweet": (22, 31), "max": 37},
                8: {"min": 17, "sweet": (20, 29), "max": 35},
                9: {"min": 15, "sweet": (18, 26), "max": 32},
                10: {"min": 13, "sweet": (16, 24), "max": 29},
                11: {"min": 12, "sweet": (14, 21), "max": 26},
            }
        }
    },
    "Cabrinha": {
        "Switchblade": {
            "type": "5-Strut Freeride / Grunt & Lift",
            "material": "HTD Plus Dacron",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 39},
                7: {"min": 20, "sweet": (23, 31), "max": 36},
                8: {"min": 18, "sweet": (21, 29), "max": 34},
                9: {"min": 16, "sweet": (18.5, 26), "max": 31},
                10: {"min": 14, "sweet": (16.5, 24), "max": 29},
                11: {"min": 13, "sweet": (15, 22), "max": 27},
                12: {"min": 12, "sweet": (14, 20), "max": 25},
                14: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        },
        "Nitro Apex": {
            "type": "5-Strut Extreme Big Air",
            "material": "Ultra HT Material",
            "sizes": {
                7: {"min": 19, "sweet": (23, 34), "max": 40},
                8: {"min": 17, "sweet": (21, 32), "max": 38},
                9: {"min": 15, "sweet": (19, 29), "max": 35},
                10: {"min": 13.5, "sweet": (17, 26), "max": 32},
                12: {"min": 11.5, "sweet": (14, 22), "max": 28},
            }
        },
        "Moto X": {
            "type": "3-Strut All-Round Freeride",
            "material": "HTD Plus",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 36},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 31},
                10: {"min": 13.5, "sweet": (16, 24), "max": 29},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 26},
            }
        },
        "Drifter": {
            "type": "3-Strut Surf / Wave Drift",
            "material": "HTD Dacron",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 40},
                7: {"min": 19, "sweet": (22, 31), "max": 37},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 31},
                10: {"min": 13, "sweet": (16, 23), "max": 28},
                11: {"min": 12, "sweet": (14, 21), "max": 25},
            }
        }
    },
    "Ozone": {
        "Edge V11/V12": {
            "type": "5-Strut High Aspect Powerhouse",
            "material": "Teijin Dacron / Transverse Shaping",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 35},
                8: {"min": 17, "sweet": (20, 28), "max": 33},
                9: {"min": 15, "sweet": (18, 26), "max": 30},
                10: {"min": 13.5, "sweet": (16, 23), "max": 28},
                11: {"min": 12.5, "sweet": (15, 21), "max": 26},
                13: {"min": 10.5, "sweet": (13, 18), "max": 22},
            }
        },
        "Vortex": {
            "type": "3-Strut Big Air / Aluula",
            "material": "Aluula Airframe",
            "sizes": {
                7: {"min": 18, "sweet": (22, 34), "max": 40},
                8: {"min": 16, "sweet": (20, 32), "max": 38},
                9: {"min": 14, "sweet": (18, 29), "max": 35},
                10: {"min": 12.5, "sweet": (16, 26), "max": 32},
                11: {"min": 11.5, "sweet": (14, 23), "max": 29},
            }
        },
        "Enduro V4": {
            "type": "3-Strut Multi-Discipline Freeride",
            "material": "Teijin Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 36},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 31},
                10: {"min": 13.5, "sweet": (16, 24), "max": 29},
                11: {"min": 12, "sweet": (14.5, 22), "max": 27},
                12: {"min": 11, "sweet": (13, 20), "max": 25},
            }
        }
    },
    "F-One": {
        "Bandit (XVI/XVII)": {
            "type": "3-Strut Delta C-Shape All-Rounder",
            "material": "Teijin 130g Dacron",
            "sizes": {
                7: {"min": 20, "sweet": (24, 34), "max": 40},
                8: {"min": 18, "sweet": (21, 31), "max": 37},
                9: {"min": 16, "sweet": (19, 28), "max": 34},
                10: {"min": 14, "sweet": (17, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15, 23), "max": 28},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 26},
                14: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        },
        "Trigger": {
            "type": "5-Strut Big Air Booster",
            "material": "High Tenacity Polyester",
            "sizes": {
                7: {"min": 19, "sweet": (23, 34), "max": 40},
                8: {"min": 17, "sweet": (21, 32), "max": 38},
                9: {"min": 15, "sweet": (19, 29), "max": 35},
                10: {"min": 13.5, "sweet": (17, 26), "max": 32},
                11: {"min": 12, "sweet": (15, 24), "max": 29},
                12: {"min": 11, "sweet": (13.5, 22), "max": 27},
            }
        }
    },
    "Reedin": {
        "SuperModel HTF": {
            "type": "3-Strut Hybrid All-Round / Fast Looper",
            "material": "Hybrid Torsion Frame (HTF)",
            "sizes": {
                6: {"min": 22, "sweet": (26, 36), "max": 42},
                7: {"min": 20, "sweet": (23, 33), "max": 39},
                8: {"min": 18, "sweet": (21, 30), "max": 36},
                9: {"min": 16, "sweet": (19, 27), "max": 33},
                10: {"min": 14, "sweet": (17, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15, 23), "max": 28},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 26},
                14: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        }
    },
    "Naish": {
        "Pivot": {
            "type": "3-Strut All-Round Freeride / Big Air",
            "material": "Quad-Tex Ripstop",
            "sizes": {
                6: {"min": 23, "sweet": (26, 36), "max": 41},
                7: {"min": 20, "sweet": (23, 33), "max": 38},
                8: {"min": 18, "sweet": (21, 30), "max": 36},
                9: {"min": 16, "sweet": (19, 27), "max": 33},
                10: {"min": 14, "sweet": (17, 25), "max": 31},
                11: {"min": 13, "sweet": (15, 23), "max": 28},
                12: {"min": 12, "sweet": (14, 21), "max": 26},
                14: {"min": 10.5, "sweet": (12.5, 18), "max": 23},
            }
        },
        "Pivot Nvision": {
            "type": "3-Strut Big Air / Helium Aluula Frame",
            "material": "Aluula Airframe",
            "sizes": {
                7: {"min": 18, "sweet": (22, 34), "max": 40},
                8: {"min": 16, "sweet": (20, 32), "max": 38},
                9: {"min": 14, "sweet": (18, 29), "max": 35},
                10: {"min": 13, "sweet": (16, 26), "max": 32},
                12: {"min": 11, "sweet": (13.5, 22), "max": 28},
            }
        }
    },
    "Slingshot": {
        "Machine V2": {
            "type": "5-Strut Big Air Booster",
            "material": "Dacron / 4x4 Canopy Tech",
            "sizes": {
                7: {"min": 20, "sweet": (24, 34), "max": 40},
                8: {"min": 18, "sweet": (21, 32), "max": 37},
                9: {"min": 16, "sweet": (19, 29), "max": 34},
                10: {"min": 14, "sweet": (17, 26), "max": 32},
                11: {"min": 12.5, "sweet": (15, 23), "max": 29},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 26},
            }
        },
        "Code V1": {
            "type": "3-Strut Freeride / All-Round",
            "material": "FrameL lightweight Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 36},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 31},
                10: {"min": 13.5, "sweet": (16, 24), "max": 29},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 26},
            }
        }
    },
    "Eleveight": {
        "XS": {
            "type": "5-Strut Extreme Big Air",
            "material": "Teijin X4 Ripstop",
            "sizes": {
                7: {"min": 19, "sweet": (23, 34), "max": 40},
                8: {"min": 17, "sweet": (21, 32), "max": 38},
                9: {"min": 15, "sweet": (19, 29), "max": 35},
                10: {"min": 13.5, "sweet": (17, 26), "max": 32},
                12: {"min": 11.5, "sweet": (14, 22), "max": 27},
            }
        },
        "RS": {
            "type": "3-Strut All-Round Crossover Freeride",
            "material": "High Tenacity Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 36},
                8: {"min": 17, "sweet": (20, 28), "max": 34},
                9: {"min": 15, "sweet": (18, 26), "max": 31},
                10: {"min": 13.5, "sweet": (16, 24), "max": 29},
                12: {"min": 11.5, "sweet": (13.5, 21), "max": 26},
                14: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        }
    }
}


def normalize_str(s: str) -> str:
    import re
    return re.sub(r"[\s\-_/]", "", s.lower())


def lookup_kite_specs(brand: str, model: str, size: float) -> dict:
    """
    Looks up realistic manufacturer specifications for a kite.
    Falls back to closest model or heuristic if not explicitly found.
    """
    norm_b = normalize_str(brand)
    norm_m = normalize_str(model)

    for b_name, models in KITE_CATALOG.items():
        if normalize_str(b_name) == norm_b:
            for m_name, specs in models.items():
                if normalize_str(m_name) == norm_m or normalize_str(m_name) in norm_m or norm_m in normalize_str(m_name):
                    sizes = specs["sizes"]
                    if size in sizes:
                        return {
                            "brand": b_name,
                            "model": m_name,
                            "size": size,
                            "type": specs["type"],
                            "material": specs["material"],
                            **sizes[size]
                        }
                    closest_s = min(sizes.keys(), key=lambda s: abs(s - size))
                    scale = (closest_s / size) if size > 0 else 1.0
                    ref = sizes[closest_s]
                    return {
                        "brand": b_name,
                        "model": m_name,
                        "size": size,
                        "type": specs["type"],
                        "material": specs["material"],
                        "min": round(ref["min"] * scale, 1),
                        "sweet": (round(ref["sweet"][0] * scale, 1), round(ref["sweet"][1] * scale, 1)),
                        "max": round(ref["max"] * scale, 1)
                    }

    # Heuristic fallback for unknown brand/model (standard 3-strut freeride baseline)
    baseline_min = round(145.0 / (size + 1.2), 1)
    baseline_max = round(baseline_min * 2.2, 1)
    sweet_low = round(baseline_min * 1.25, 1)
    sweet_high = round(baseline_min * 1.75, 1)
    return {
        "brand": brand,
        "model": model,
        "size": size,
        "type": "General All-Rounder",
        "material": "Standard",
        "min": baseline_min,
        "sweet": (sweet_low, sweet_high),
        "max": baseline_max
    }
