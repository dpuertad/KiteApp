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
                6: {"min": 23, "sweet": (27, 38), "max": 44},
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
            }
        },
        "Vertigo": {
            "type": "3-Strut All-Round Freeride / Jumping",
            "material": "Dacron DP175LL",
            "sizes": {
                5: {"min": 24, "sweet": (27, 37), "max": 42},
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 38},
                9: {"min": 15, "sweet": (18.5, 27), "max": 34},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 29},
                13: {"min": 10.5, "sweet": (13.5, 20), "max": 25},
            }
        },
        "Elips": {
            "type": "3-Strut Wave / Drift / Foil",
            "material": "Teijin T9669 Triple Ripstop",
            "sizes": {
                5: {"min": 23, "sweet": (26.5, 37), "max": 41},
                6: {"min": 20, "sweet": (23.5, 33), "max": 38},
                7: {"min": 18, "sweet": (21, 30), "max": 36},
                8: {"min": 16, "sweet": (19, 27.5), "max": 34},
                9: {"min": 14, "sweet": (17, 25), "max": 32},
                10: {"min": 12.5, "sweet": (15, 22.5), "max": 29},
            }
        },
        "Strutless": {
            "type": "0-Strut Ultra-Lightwind & Hydrofoil",
            "material": "Ultra-Light 2D Tech",
            "sizes": {
                7: {"min": 15, "sweet": (18, 26), "max": 31},
                9: {"min": 12.5, "sweet": (15, 22), "max": 27},
                11: {"min": 10.5, "sweet": (13, 19), "max": 24},
                13: {"min": 9, "sweet": (11, 16.5), "max": 21},
                15: {"min": 8, "sweet": (9.5, 14.5), "max": 19},
                17: {"min": 7, "sweet": (8.5, 13), "max": 17},
            }
        },
        "Freewave": {
            "type": "3-Strut Freeride / Wave Crossover",
            "material": "Standard Dacron",
            "sizes": {
                5: {"min": 24, "sweet": (27, 36), "max": 41},
                7: {"min": 19, "sweet": (22.5, 31), "max": 37},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 33},
                11: {"min": 12.5, "sweet": (15.5, 22.5), "max": 28},
            }
        }
    },
    "Duotone": {
        "Rebel SLS": {
            "type": "5-Strut High-Performance Big Air",
            "material": "Penta TX (SLS)",
            "sizes": {
                6: {"min": 23, "sweet": (27, 38), "max": 44},
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
                13: {"min": 12, "sweet": (15.0, 21.5), "max": 26},
                14: {"min": 11.5, "sweet": (14.0, 20.0), "max": 24},
            }
        },
        "Rebel D/LAB": {
            "type": "5-Strut Extreme Big Air / Aluula",
            "material": "Aluula Airframe (D/LAB)",
            "sizes": {
                7: {"min": 19.5, "sweet": (23.5, 35), "max": 42},
                8: {"min": 17.5, "sweet": (21.5, 33), "max": 40},
                9: {"min": 15.5, "sweet": (19.5, 30), "max": 37},
                10: {"min": 14, "sweet": (17.5, 27.5), "max": 34},
                11: {"min": 12.5, "sweet": (16.0, 25.5), "max": 31},
                12: {"min": 11.5, "sweet": (15.0, 24.0), "max": 29},
            }
        },
        "Evo": {
            "type": "3-Strut All-Round Freeride",
            "material": "Standard Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 38},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 36},
                9: {"min": 15, "sweet": (18.5, 27), "max": 34},
                10: {"min": 13.5, "sweet": (17, 25), "max": 32},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 29},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 27},
            }
        },
        "Evo SLS": {
            "type": "3-Strut All-Round Performance",
            "material": "Penta TX (SLS)",
            "sizes": {
                7: {"min": 18.5, "sweet": (22, 32), "max": 39},
                8: {"min": 16.5, "sweet": (20, 30), "max": 37},
                9: {"min": 14.5, "sweet": (18, 27.5), "max": 35},
                10: {"min": 13, "sweet": (16.5, 25.5), "max": 33},
                11: {"min": 12, "sweet": (15.0, 23.5), "max": 30},
                12: {"min": 11, "sweet": (14.0, 22.0), "max": 28},
            }
        },
        "Evo D/LAB": {
            "type": "3-Strut Ultimate Freeride / Aluula",
            "material": "Aluula Airframe (D/LAB)",
            "sizes": {
                7: {"min": 17.5, "sweet": (21, 32), "max": 40},
                8: {"min": 15.5, "sweet": (19, 30), "max": 38},
                9: {"min": 13.5, "sweet": (17, 28), "max": 36},
                10: {"min": 12, "sweet": (15.5, 26), "max": 34},
                11: {"min": 11, "sweet": (14.0, 24), "max": 31},
                12: {"min": 10, "sweet": (13.0, 22), "max": 29},
            }
        },
        "Dice SLS": {
            "type": "3-Strut Freestyle / C-Hybrid",
            "material": "Penta TX (SLS)",
            "sizes": {
                6: {"min": 23, "sweet": (26.5, 36), "max": 42},
                7: {"min": 20, "sweet": (23.5, 33), "max": 39},
                8: {"min": 18, "sweet": (21.5, 31), "max": 37},
                9: {"min": 16, "sweet": (19.5, 29), "max": 35},
                10: {"min": 14.5, "sweet": (17.5, 26.5), "max": 33},
                11: {"min": 13, "sweet": (16.0, 24), "max": 30},
                12: {"min": 12, "sweet": (15.0, 22), "max": 27},
            }
        },
        "Neo SLS": {
            "type": "3-Strut Wave / Strapless",
            "material": "Penta TX (SLS)",
            "sizes": {
                5: {"min": 23, "sweet": (26.5, 37), "max": 41},
                6: {"min": 20, "sweet": (23.5, 33), "max": 38},
                7: {"min": 18, "sweet": (21, 30), "max": 36},
                8: {"min": 16, "sweet": (19, 27.5), "max": 34},
                9: {"min": 14, "sweet": (17, 25), "max": 32},
                10: {"min": 12.5, "sweet": (15, 22.5), "max": 29},
                11: {"min": 11.5, "sweet": (14, 20.5), "max": 26},
                12: {"min": 10.5, "sweet": (13, 19), "max": 24},
            }
        },
        "Juice D/LAB": {
            "type": "3-Strut Light Wind Specialist",
            "material": "Aluula (D/LAB)",
            "sizes": {
                11: {"min": 10.5, "sweet": (13.5, 19.5), "max": 24},
                13: {"min": 9.5, "sweet": (12.0, 17.5), "max": 22},
                14: {"min": 9.0, "sweet": (11.0, 16.5), "max": 21},
                15: {"min": 8.0, "sweet": (10.0, 15.5), "max": 20},
                17: {"min": 7.5, "sweet": (9.0, 14.5), "max": 18},
            }
        }
    },
    "Harlem": {
        "Force": {
            "type": "5-Strut Extreme Big Air Powerhouse (Lorenzo Casati Weapon)",
            "material": "Brainchild PRO Weld / Stiff Rigid Frame",
            "sizes": {
                6: {"min": 22, "sweet": (26, 38), "max": 44},
                7: {"min": 19.5, "sweet": (23.5, 35), "max": 42},
                8: {"min": 17.5, "sweet": (21.5, 33), "max": 40},
                9: {"min": 15.5, "sweet": (19.5, 30), "max": 37},
                10: {"min": 14, "sweet": (17.5, 27.5), "max": 34},
                11: {"min": 12.5, "sweet": (16, 25.5), "max": 31},
                12: {"min": 11.5, "sweet": (14.5, 23.5), "max": 29},
            }
        },
        "Thrive": {
            "type": "3-Strut All-Round / Big Air / Loop (Hadlow & Grösel)",
            "material": "Brainchild PRO Weld / Twincross FlyLite",
            "sizes": {
                6: {"min": 21, "sweet": (24.5, 33), "max": 39},
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 37},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 35},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 33},
                10: {"min": 13.5, "sweet": (17, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 28},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 26},
                13: {"min": 10.5, "sweet": (13.5, 20), "max": 24},
                15: {"min": 9.5, "sweet": (11.5, 17.5), "max": 21},
            }
        },
        "Thrive V2": {
            "type": "3-Strut Next-Gen ProWeld All-Rounder",
            "material": "Brainchild PRO Weld",
            "sizes": {
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 37},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 35},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 33},
                10: {"min": 13.5, "sweet": (17, 25), "max": 31},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 26},
            }
        },
        "Light": {
            "type": "1-Strut Light Wind & Hydrofoil Specialist",
            "material": "Ultra-light Brainchild Fabric",
            "sizes": {
                13: {"min": 9.5, "sweet": (11.5, 17), "max": 22},
                15: {"min": 8.5, "sweet": (10.5, 16), "max": 20},
                17: {"min": 8, "sweet": (9.5, 14.5), "max": 18},
            }
        },
        "Go": {
            "type": "3-Strut Freeride / Progression",
            "material": "Reinforced Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 36},
                9: {"min": 15, "sweet": (18, 26), "max": 32},
                12: {"min": 11.5, "sweet": (14, 21), "max": 26},
            }
        },
        "Lead": {
            "type": "3-Strut Wave / Drift",
            "material": "Brainchild Weld Tech",
            "sizes": {
                6: {"min": 20, "sweet": (23.5, 33), "max": 38},
                7: {"min": 18, "sweet": (21, 30), "max": 36},
                8: {"min": 16, "sweet": (19, 27.5), "max": 34},
                9: {"min": 14, "sweet": (17, 25), "max": 32},
            }
        },
        "Sir": {
            "type": "5-Strut Classic Big Air / High Wind",
            "material": "High Tenacity Dacron",
            "sizes": {
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                11: {"min": 13.5, "sweet": (17, 24.5), "max": 30},
            }
        }
    },
    "Core": {
        "XR8": {
            "type": "5-Strut Big Air / High Aspect",
            "material": "ExoTex 2 / CoreTex 2",
            "sizes": {
                6: {"min": 23, "sweet": (27, 38), "max": 44},
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
                13.5: {"min": 11.5, "sweet": (14.5, 21), "max": 25},
                15: {"min": 9.5, "sweet": (11.5, 17.5), "max": 21},
                17: {"min": 8, "sweet": (9.5, 15), "max": 18},
            }
        },
        "XR Pro": {
            "type": "5-Strut Extreme Big Air / Aluula",
            "material": "Aluula Black Airframe",
            "sizes": {
                6: {"min": 22, "sweet": (26, 38), "max": 44},
                7: {"min": 19.5, "sweet": (23.5, 35), "max": 42},
                8: {"min": 17.5, "sweet": (21.5, 33), "max": 40},
                9: {"min": 15.5, "sweet": (19.5, 30), "max": 37},
                10: {"min": 14, "sweet": (17.5, 27.5), "max": 34},
                12: {"min": 11.5, "sweet": (15.0, 24.0), "max": 29},
            }
        },
        "Nexus 3": {
            "type": "3-Strut Universal Freeride/Wave",
            "material": "ExoTex 2",
            "sizes": {
                6: {"min": 21, "sweet": (24.5, 33), "max": 39},
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 37},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 35},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 33},
                10: {"min": 13.5, "sweet": (17, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 28},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 26},
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
                6: {"min": 23, "sweet": (27, 38), "max": 44},
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
            }
        },
        "Orbit Pro": {
            "type": "5-Strut Competition Big Air",
            "material": "N-Max / Aluula Composite",
            "sizes": {
                7: {"min": 19.5, "sweet": (23.5, 35), "max": 42},
                8: {"min": 17.5, "sweet": (21.5, 33), "max": 40},
                9: {"min": 15.5, "sweet": (19.5, 30), "max": 37},
                10: {"min": 14, "sweet": (17.5, 27.5), "max": 34},
                11: {"min": 12.5, "sweet": (16.0, 25.5), "max": 31},
            }
        },
        "Reach": {
            "type": "3-Strut All-Round Freeride",
            "material": "N-HTYR Performance Dacron",
            "sizes": {
                6: {"min": 21, "sweet": (24.5, 33), "max": 38},
                7: {"min": 19, "sweet": (22.5, 31), "max": 36},
                8: {"min": 17, "sweet": (20.5, 29), "max": 34},
                9: {"min": 15, "sweet": (18.5, 27), "max": 32},
                10: {"min": 13.5, "sweet": (17, 25), "max": 30},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 28},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 26},
                13: {"min": 10.5, "sweet": (13.5, 20), "max": 24},
                15: {"min": 9.5, "sweet": (11.5, 17.5), "max": 21},
            }
        },
        "Carve": {
            "type": "3-Strut Wave / Strapless",
            "material": "Performance Dacron",
            "sizes": {
                6: {"min": 20, "sweet": (23.5, 33), "max": 38},
                7: {"min": 18, "sweet": (21, 30), "max": 36},
                8: {"min": 16, "sweet": (19, 27.5), "max": 34},
                9: {"min": 14, "sweet": (17, 25), "max": 32},
                10: {"min": 12.5, "sweet": (15, 22.5), "max": 29},
                11: {"min": 11.5, "sweet": (14, 20.5), "max": 26},
            }
        }
    },
    "Cabrinha": {
        "Switchblade": {
            "type": "5-Strut Freeride / Grunt & Lift",
            "material": "HTD Plus Dacron",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 39},
                7: {"min": 19.5, "sweet": (23, 33), "max": 39},
                8: {"min": 17.5, "sweet": (21, 31), "max": 37},
                9: {"min": 15.5, "sweet": (19, 28), "max": 34},
                10: {"min": 14, "sweet": (17.5, 26), "max": 32},
                11: {"min": 13, "sweet": (16.0, 23.5), "max": 29},
                12: {"min": 12, "sweet": (14.5, 21.5), "max": 27},
                14: {"min": 10, "sweet": (12.5, 18), "max": 23},
            }
        },
        "Nitro Apex": {
            "type": "5-Strut Extreme Big Air",
            "material": "Ultra HT Material",
            "sizes": {
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
            }
        },
        "Contra": {
            "type": "3-Strut / 1-Strut Light Wind Specialist",
            "material": "HTD Plus Light",
            "sizes": {
                11: {"min": 10.5, "sweet": (13.5, 19.5), "max": 24},
                13: {"min": 9.5, "sweet": (12.0, 17.5), "max": 22},
                15: {"min": 8.0, "sweet": (10.0, 15.5), "max": 20},
                17: {"min": 7.5, "sweet": (9.0, 14.5), "max": 18},
            }
        },
        "Moto X": {
            "type": "3-Strut All-Round Freeride",
            "material": "HTD Plus",
            "sizes": {
                7: {"min": 19, "sweet": (22.5, 30.5), "max": 36},
                8: {"min": 17, "sweet": (20.5, 28.5), "max": 34},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 31},
                10: {"min": 13.5, "sweet": (16.5, 24.5), "max": 29},
                12: {"min": 11.5, "sweet": (14.0, 21.5), "max": 26},
            }
        },
        "Drifter": {
            "type": "3-Strut Surf / Wave Drift",
            "material": "HTD Dacron",
            "sizes": {
                6: {"min": 20, "sweet": (23.5, 33), "max": 38},
                7: {"min": 18, "sweet": (21, 30), "max": 36},
                8: {"min": 16, "sweet": (19, 27.5), "max": 34},
                9: {"min": 14, "sweet": (17, 25), "max": 32},
                10: {"min": 12.5, "sweet": (15, 22.5), "max": 29},
                11: {"min": 11.5, "sweet": (14, 20.5), "max": 26},
            }
        }
    },
    "Ozone": {
        "Edge V11/V12": {
            "type": "5-Strut High Aspect Powerhouse",
            "material": "Teijin Dacron / Transverse Shaping",
            "sizes": {
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                13: {"min": 11.5, "sweet": (14.5, 21), "max": 25},
            }
        },
        "Zephyr V8": {
            "type": "17m Light Wind Powerhouse",
            "material": "Teijin Dacron Lightweight",
            "sizes": {
                17: {"min": 7.5, "sweet": (9.0, 14.5), "max": 18},
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
                7: {"min": 19, "sweet": (22.5, 30.5), "max": 36},
                8: {"min": 17, "sweet": (20.5, 28.5), "max": 34},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 31},
                10: {"min": 13.5, "sweet": (16.5, 24.5), "max": 29},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 28},
                12: {"min": 11.5, "sweet": (14.0, 21.5), "max": 26},
            }
        }
    },
    "F-One": {
        "Bandit (XVI/XVII)": {
            "type": "3-Strut Delta C-Shape All-Rounder",
            "material": "Teijin 130g Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 38},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 36},
                9: {"min": 15, "sweet": (18.5, 27), "max": 34},
                10: {"min": 13.5, "sweet": (17, 25), "max": 32},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 29},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 27},
                14: {"min": 10, "sweet": (12.5, 18), "max": 23},
            }
        },
        "Trigger": {
            "type": "5-Strut Big Air Booster",
            "material": "High Tenacity Polyester",
            "sizes": {
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
            }
        }
    },
    "Reedin": {
        "SuperModel HTF": {
            "type": "3-Strut Hybrid All-Round / Fast Looper",
            "material": "Hybrid Torsion Frame (HTF)",
            "sizes": {
                6: {"min": 21, "sweet": (24.5, 33), "max": 39},
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 37},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 35},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 33},
                10: {"min": 13.5, "sweet": (17, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 28},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 26},
                14: {"min": 10, "sweet": (12.5, 18), "max": 23},
            }
        }
    },
    "Naish": {
        "Pivot": {
            "type": "3-Strut All-Round Freeride / Big Air",
            "material": "Quad-Tex Ripstop",
            "sizes": {
                6: {"min": 21, "sweet": (24.5, 33), "max": 39},
                7: {"min": 19, "sweet": (22.5, 31.5), "max": 37},
                8: {"min": 17, "sweet": (20.5, 29.5), "max": 35},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 33},
                10: {"min": 13.5, "sweet": (17, 25), "max": 31},
                11: {"min": 12.5, "sweet": (15.5, 23), "max": 28},
                12: {"min": 11.5, "sweet": (14.5, 21.5), "max": 26},
                14: {"min": 10, "sweet": (12.5, 18), "max": 23},
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
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                11: {"min": 13.5, "sweet": (17.0, 24.5), "max": 30},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
            }
        },
        "Code V1": {
            "type": "3-Strut Freeride / All-Round",
            "material": "FrameL lightweight Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22.5, 30.5), "max": 36},
                8: {"min": 17, "sweet": (20.5, 28.5), "max": 34},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 31},
                10: {"min": 13.5, "sweet": (16.5, 24.5), "max": 29},
                12: {"min": 11.5, "sweet": (14.0, 21.5), "max": 26},
            }
        }
    },
    "Eleveight": {
        "XS": {
            "type": "5-Strut Extreme Big Air",
            "material": "Teijin X4 Ripstop",
            "sizes": {
                7: {"min": 20.5, "sweet": (24.5, 35), "max": 41},
                8: {"min": 18.5, "sweet": (22.5, 32), "max": 38},
                9: {"min": 16.5, "sweet": (20.5, 29), "max": 35},
                10: {"min": 15, "sweet": (18.5, 26.5), "max": 32},
                12: {"min": 12.5, "sweet": (16.0, 23.0), "max": 28},
            }
        },
        "RS": {
            "type": "3-Strut All-Round Crossover Freeride",
            "material": "High Tenacity Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22.5, 30.5), "max": 36},
                8: {"min": 17, "sweet": (20.5, 28.5), "max": 34},
                9: {"min": 15, "sweet": (18.5, 26.5), "max": 31},
                10: {"min": 13.5, "sweet": (16.5, 24.5), "max": 29},
                12: {"min": 11.5, "sweet": (14.0, 21.5), "max": 26},
                14: {"min": 10, "sweet": (12.5, 18), "max": 23},
            }
        }
    },
    "Flysurfer": {
        "Soul 3": {
            "type": "Ram-Air All-Round Foil Kite",
            "material": "TX-Light Closed-Cell Foil",
            "sizes": {
                8: {"min": 11.5, "sweet": (13.5, 22), "max": 27},
                10: {"min": 9.5, "sweet": (11.5, 19), "max": 24},
                12: {"min": 8.0, "sweet": (10.0, 16.5), "max": 21},
                15: {"min": 7.0, "sweet": (8.5, 14.5), "max": 18},
                18: {"min": 6.0, "sweet": (7.5, 13), "max": 16},
                21: {"min": 5.5, "sweet": (7.0, 12), "max": 15},
            }
        },
        "Sonic 4": {
            "type": "High-Performance Race / Freeride Foil Kite",
            "material": "TX-Light High-Performance Foil",
            "sizes": {
                9: {"min": 10.5, "sweet": (12.5, 20), "max": 25},
                12: {"min": 8.0, "sweet": (10.0, 16.5), "max": 21},
                15: {"min": 7.0, "sweet": (8.5, 14.5), "max": 18},
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
