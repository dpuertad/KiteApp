"""
Comprehensive Kite Model, Brand, Material & Wind Range Catalog
Based on official manufacturer specifications for a 75kg rider on a twintip board.
"""

KITE_CATALOG = {
    "Duotone": {
        "Rebel": {
            "type": "5-Strut Big Air / High Aspect",
            "material": "Standard Dacron",
            "sizes": {
                6: {"min": 22, "sweet": (25, 34), "max": 41},
                7: {"min": 20, "sweet": (23, 32), "max": 39},
                8: {"min": 18, "sweet": (21, 30), "max": 37},
                9: {"min": 16, "sweet": (19, 27), "max": 34},
                10: {"min": 14, "sweet": (17, 25), "max": 32},
                11: {"min": 13, "sweet": (15, 22), "max": 29},
                12: {"min": 12, "sweet": (14, 20), "max": 26},
                13: {"min": 11, "sweet": (13, 19), "max": 24},
                14: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        },
        "Rebel SLS": {
            "type": "5-Strut Big Air / High Aspect",
            "material": "Penta TX (SLS - 15% lighter)",
            "sizes": {
                6: {"min": 21, "sweet": (24, 34), "max": 40},
                7: {"min": 19, "sweet": (22, 32), "max": 38},
                8: {"min": 17, "sweet": (20, 29), "max": 36},
                9: {"min": 15, "sweet": (18, 27), "max": 34},
                10: {"min": 13, "sweet": (16, 24), "max": 32},
                11: {"min": 12, "sweet": (14, 22), "max": 29},
                12: {"min": 11, "sweet": (13, 20), "max": 26},
                13: {"min": 10, "sweet": (12, 18), "max": 24},
                14: {"min": 9, "sweet": (11, 16), "max": 22},
            }
        },
        "Rebel D/LAB": {
            "type": "5-Strut Big Air / High Aspect",
            "material": "Aluula (D/LAB - 30% lighter)",
            "sizes": {
                7: {"min": 17, "sweet": (20, 31), "max": 38},
                8: {"min": 15, "sweet": (18, 28), "max": 36},
                9: {"min": 13.5, "sweet": (16, 26), "max": 34},
                10: {"min": 11.5, "sweet": (14, 23), "max": 32},
                11: {"min": 10.5, "sweet": (13, 21), "max": 29},
                12: {"min": 9.5, "sweet": (12, 19), "max": 26},
            }
        },
        "Evo": {
            "type": "3-Strut All-Round Freeride",
            "material": "Standard Dacron",
            "sizes": {
                7: {"min": 19, "sweet": (22, 30), "max": 38},
                8: {"min": 17, "sweet": (20, 28), "max": 36},
                9: {"min": 15, "sweet": (18, 26), "max": 34},
                10: {"min": 13, "sweet": (16, 24), "max": 32},
                11: {"min": 12, "sweet": (14, 22), "max": 29},
                12: {"min": 11, "sweet": (13, 20), "max": 27},
            }
        },
        "Evo SLS": {
            "type": "3-Strut All-Round Freeride",
            "material": "Penta TX (SLS)",
            "sizes": {
                7: {"min": 18, "sweet": (21, 30), "max": 38},
                8: {"min": 16, "sweet": (19, 28), "max": 36},
                9: {"min": 14, "sweet": (17, 26), "max": 34},
                10: {"min": 12, "sweet": (15, 24), "max": 32},
                11: {"min": 11, "sweet": (13, 21), "max": 29},
                12: {"min": 10, "sweet": (12, 19), "max": 27},
            }
        },
        "Evo D/LAB": {
            "type": "3-Strut All-Round Freeride",
            "material": "Aluula (D/LAB)",
            "sizes": {
                7: {"min": 16, "sweet": (19, 29), "max": 38},
                8: {"min": 14, "sweet": (17, 27), "max": 36},
                9: {"min": 12.5, "sweet": (15, 25), "max": 34},
                10: {"min": 10.5, "sweet": (13, 23), "max": 32},
                11: {"min": 9.5, "sweet": (12, 20), "max": 29},
                12: {"min": 8.5, "sweet": (11, 18), "max": 27},
            }
        },
        "Dice SLS": {
            "type": "3-Strut Freestyle / C-Hybrid",
            "material": "Penta TX (SLS)",
            "sizes": {
                6: {"min": 20, "sweet": (24, 33), "max": 39},
                7: {"min": 19, "sweet": (22, 31), "max": 37},
                8: {"min": 17, "sweet": (20, 29), "max": 35},
                9: {"min": 15, "sweet": (18, 27), "max": 33},
                10: {"min": 13, "sweet": (16, 24), "max": 31},
                11: {"min": 12, "sweet": (14, 21), "max": 28},
                12: {"min": 11, "sweet": (13, 19), "max": 25},
                13: {"min": 10, "sweet": (12, 17), "max": 22},
            }
        },
        "Neo SLS": {
            "type": "3-Strut Wave / Drift",
            "material": "Penta TX (SLS)",
            "sizes": {
                5: {"min": 24, "sweet": (27, 36), "max": 40},
                6: {"min": 20, "sweet": (23, 32), "max": 37},
                7: {"min": 18, "sweet": (21, 30), "max": 35},
                8: {"min": 16, "sweet": (19, 27), "max": 33},
                9: {"min": 14, "sweet": (17, 25), "max": 31},
                10: {"min": 12, "sweet": (15, 23), "max": 29},
                11: {"min": 11, "sweet": (13, 20), "max": 26},
                12: {"min": 10, "sweet": (12, 18), "max": 23},
            }
        },
        "Juice D/LAB": {
            "type": "3-Strut Light Wind Specialist",
            "material": "Aluula (D/LAB)",
            "sizes": {
                13: {"min": 7.5, "sweet": (9, 15), "max": 19},
                14: {"min": 7, "sweet": (8.5, 14), "max": 18},
                15: {"min": 6.5, "sweet": (8, 13), "max": 17},
                17: {"min": 6, "sweet": (7.5, 12), "max": 16},
            }
        }
    },
    "Core": {
        "XR8": {
            "type": "5-Strut Big Air / Delta Bow",
            "material": "ExoTex 2 / CoreTex 2",
            "sizes": {
                5: {"min": 22, "sweet": (26, 36), "max": 42},
                6: {"min": 20, "sweet": (24, 34), "max": 38},
                7: {"min": 17, "sweet": (21, 30), "max": 35},
                8: {"min": 15, "sweet": (19, 27), "max": 33},
                9: {"min": 13, "sweet": (16, 24), "max": 30},
                10: {"min": 12, "sweet": (15, 22), "max": 28},
                11: {"min": 11, "sweet": (13, 20), "max": 26},
                12: {"min": 10, "sweet": (12, 18), "max": 24},
                13.5: {"min": 9, "sweet": (11, 16), "max": 22},
                15: {"min": 8, "sweet": (10, 15), "max": 20},
                17: {"min": 7, "sweet": (9, 14), "max": 19},
            }
        },
        "XR Pro": {
            "type": "5-Strut Big Air Competition",
            "material": "Aluula Black",
            "sizes": {
                6: {"min": 19, "sweet": (23, 34), "max": 40},
                7: {"min": 16, "sweet": (20, 31), "max": 37},
                8: {"min": 14, "sweet": (18, 28), "max": 35},
                9: {"min": 12, "sweet": (15, 25), "max": 32},
                10: {"min": 11, "sweet": (14, 23), "max": 30},
                12: {"min": 9, "sweet": (11, 19), "max": 26},
            }
        },
        "Nexus 3": {
            "type": "3-Strut Universal Freeride/Wave",
            "material": "ExoTex 2",
            "sizes": {
                6: {"min": 21, "sweet": (24, 33), "max": 39},
                7: {"min": 18, "sweet": (21, 29), "max": 36},
                8: {"min": 16, "sweet": (19, 27), "max": 34},
                9: {"min": 14, "sweet": (17, 24), "max": 31},
                10: {"min": 12, "sweet": (15, 22), "max": 28},
                11: {"min": 11, "sweet": (13, 20), "max": 26},
                12: {"min": 10, "sweet": (12, 18), "max": 24},
            }
        },
        "Pace Pro": {
            "type": "3-Strut High-Performance Big Air",
            "material": "Aluula 3-Strut",
            "sizes": {
                6: {"min": 20, "sweet": (24, 35), "max": 41},
                7: {"min": 17, "sweet": (21, 32), "max": 38},
                8: {"min": 15, "sweet": (19, 29), "max": 36},
                9: {"min": 13, "sweet": (16, 26), "max": 33},
                10: {"min": 11.5, "sweet": (14, 24), "max": 30},
                12: {"min": 9.5, "sweet": (12, 20), "max": 26},
            }
        }
    },
    "North": {
        "Orbit": {
            "type": "5-Strut Big Air / Overpowered Looper",
            "material": "N-HTYR / N-Force",
            "sizes": {
                6: {"min": 20, "sweet": (25, 36), "max": 42},
                7: {"min": 18, "sweet": (22, 33), "max": 38},
                8: {"min": 16, "sweet": (20, 31), "max": 36},
                9: {"min": 14, "sweet": (18, 28), "max": 33},
                10: {"min": 12, "sweet": (16, 25), "max": 30},
                11: {"min": 11, "sweet": (14, 23), "max": 27},
                12: {"min": 10, "sweet": (13, 21), "max": 25},
            }
        },
        "Orbit Pro": {
            "type": "5-Strut Big Air / Aluula Struts",
            "material": "N-Max / Aluula Composite",
            "sizes": {
                7: {"min": 17, "sweet": (21, 33), "max": 39},
                8: {"min": 15, "sweet": (19, 31), "max": 37},
                9: {"min": 13, "sweet": (17, 28), "max": 34},
                10: {"min": 11, "sweet": (15, 25), "max": 31},
                11: {"min": 10, "sweet": (13, 23), "max": 28},
            }
        },
        "Reach": {
            "type": "3-Strut All-Round Freeride",
            "material": "N-HTYR Performance Dacron",
            "sizes": {
                5: {"min": 21, "sweet": (24, 32), "max": 37},
                6: {"min": 20, "sweet": (23, 30), "max": 34},
                7: {"min": 17, "sweet": (20, 27), "max": 32},
                8: {"min": 16, "sweet": (18, 25), "max": 30},
                9: {"min": 13, "sweet": (16, 23), "max": 28},
                10: {"min": 12, "sweet": (14, 21), "max": 26},
                11: {"min": 10, "sweet": (13, 20), "max": 25},
                12: {"min": 9, "sweet": (12, 18), "max": 23},
                13: {"min": 8, "sweet": (11, 16), "max": 20},
                15: {"min": 8, "sweet": (10, 15), "max": 20},
            }
        },
        "Carve": {
            "type": "3-Strut Wave / Strapless",
            "material": "Performance Dacron",
            "sizes": {
                6: {"min": 21, "sweet": (24, 32), "max": 38},
                7: {"min": 18, "sweet": (21, 29), "max": 35},
                8: {"min": 16, "sweet": (19, 27), "max": 33},
                9: {"min": 14, "sweet": (17, 24), "max": 30},
                10: {"min": 12, "sweet": (15, 22), "max": 27},
                11: {"min": 11, "sweet": (13, 20), "max": 25},
            }
        }
    },
    "Cabrinha": {
        "Switchblade": {
            "type": "5-Strut Big Air Freeride / Grunt",
            "material": "HTD Plus Dacron",
            "sizes": {
                6: {"min": 20, "sweet": (24, 31), "max": 35},
                7: {"min": 18, "sweet": (21, 28), "max": 32},
                8: {"min": 16, "sweet": (19, 26), "max": 30},
                9: {"min": 13, "sweet": (16, 23), "max": 27},
                10: {"min": 11, "sweet": (14, 21), "max": 25},
                11: {"min": 10, "sweet": (13, 19), "max": 23},
                12: {"min": 9, "sweet": (12, 18), "max": 21},
                14: {"min": 7, "sweet": (10, 15), "max": 19},
            }
        },
        "Nitro Apex": {
            "type": "5-Strut Extreme Big Air",
            "material": "Ultra HT Material",
            "sizes": {
                7: {"min": 18, "sweet": (22, 33), "max": 38},
                8: {"min": 16, "sweet": (20, 31), "max": 36},
                9: {"min": 14, "sweet": (18, 28), "max": 33},
                10: {"min": 12, "sweet": (15, 25), "max": 30},
                12: {"min": 10, "sweet": (13, 21), "max": 26},
            }
        },
        "Moto X": {
            "type": "3-Strut All-Round Freeride",
            "material": "HTD Plus",
            "sizes": {
                7: {"min": 18, "sweet": (21, 28), "max": 34},
                8: {"min": 16, "sweet": (19, 26), "max": 32},
                9: {"min": 14, "sweet": (17, 24), "max": 29},
                10: {"min": 12, "sweet": (15, 22), "max": 27},
                12: {"min": 10, "sweet": (12, 19), "max": 24},
            }
        }
    },
    "Ozone": {
        "Edge V11/V12": {
            "type": "5-Strut High Aspect Powerhouse",
            "material": "Teijin Dacron / Transverse Shaping",
            "sizes": {
                6: {"min": 17, "sweet": (21, 28), "max": 32},
                7: {"min": 16, "sweet": (19, 26), "max": 29},
                8: {"min": 15, "sweet": (18, 25), "max": 27},
                9: {"min": 14, "sweet": (17, 23), "max": 25},
                10: {"min": 12, "sweet": (15, 21), "max": 24},
                11: {"min": 11, "sweet": (14, 20), "max": 22},
                13: {"min": 9, "sweet": (12, 17), "max": 19},
            }
        },
        "Vortex": {
            "type": "3-Strut Big Air / Aluula",
            "material": "Aluula Airframe",
            "sizes": {
                7: {"min": 17, "sweet": (21, 32), "max": 38},
                8: {"min": 15, "sweet": (19, 30), "max": 36},
                9: {"min": 13, "sweet": (17, 27), "max": 33},
                10: {"min": 11, "sweet": (15, 24), "max": 30},
                11: {"min": 10, "sweet": (13, 22), "max": 27},
            }
        },
        "Enduro V4": {
            "type": "3-Strut Multi-Discipline Freeride",
            "material": "Teijin Dacron",
            "sizes": {
                7: {"min": 18, "sweet": (21, 28), "max": 34},
                8: {"min": 16, "sweet": (19, 26), "max": 32},
                9: {"min": 14, "sweet": (17, 24), "max": 29},
                10: {"min": 12, "sweet": (15, 22), "max": 27},
                11: {"min": 11, "sweet": (13, 20), "max": 25},
                12: {"min": 10, "sweet": (12, 18), "max": 23},
            }
        }
    },
    "F-One": {
        "Bandit (XVI/XVII)": {
            "type": "3-Strut Delta C-Shape All-Rounder",
            "material": "Teijin 130g Dacron",
            "sizes": {
                7: {"min": 25, "sweet": (27, 36), "max": 42},
                8: {"min": 20, "sweet": (23, 31), "max": 35},
                9: {"min": 16, "sweet": (19, 26), "max": 30},
                10: {"min": 12, "sweet": (15, 22), "max": 26},
                11: {"min": 11, "sweet": (14, 21), "max": 24},
                12: {"min": 10, "sweet": (13, 19), "max": 22},
                14: {"min": 8, "sweet": (11, 16), "max": 18},
            }
        },
        "Trigger": {
            "type": "5-Strut Big Air Booster",
            "material": "High Tenacity Polyester",
            "sizes": {
                7: {"min": 19, "sweet": (23, 33), "max": 39},
                8: {"min": 17, "sweet": (20, 31), "max": 36},
                9: {"min": 15, "sweet": (18, 28), "max": 33},
                10: {"min": 13, "sweet": (16, 25), "max": 30},
                11: {"min": 11, "sweet": (14, 23), "max": 27},
                12: {"min": 10, "sweet": (13, 21), "max": 25},
            }
        }
    },
    "Reedin": {
        "SuperModel HTF": {
            "type": "3-Strut Hybrid All-Round / Fast Looper",
            "material": "Hybrid Torsion Frame (HTF)",
            "sizes": {
                6: {"min": 23, "sweet": (26, 35), "max": 42},
                7: {"min": 20, "sweet": (24, 32), "max": 40},
                8: {"min": 18, "sweet": (21, 28), "max": 35},
                9: {"min": 15, "sweet": (18, 25), "max": 30},
                10: {"min": 12, "sweet": (15, 22), "max": 28},
                11: {"min": 11, "sweet": (14, 20), "max": 25},
                12: {"min": 10, "sweet": (12, 18), "max": 23},
                14: {"min": 8, "sweet": (10, 15), "max": 20},
            }
        }
    },
    "Naish": {
        "Pivot": {
            "type": "3-Strut All-Round Freeride / Big Air",
            "material": "Quad-Tex Ripstop",
            "sizes": {
                6: {"min": 24, "sweet": (27, 36), "max": 40},
                7: {"min": 20, "sweet": (23, 32), "max": 37},
                8: {"min": 17, "sweet": (20, 29), "max": 35},
                9: {"min": 15, "sweet": (18, 26), "max": 30},
                10: {"min": 14, "sweet": (16, 24), "max": 28},
                11: {"min": 13, "sweet": (15, 22), "max": 26},
                12: {"min": 12, "sweet": (14, 20), "max": 24},
                14: {"min": 11, "sweet": (13, 18), "max": 22},
            }
        },
        "Pivot Nvision": {
            "type": "3-Strut Big Air / Helium Aluula Frame",
            "material": "Aluula Airframe",
            "sizes": {
                7: {"min": 18, "sweet": (22, 33), "max": 38},
                8: {"min": 15, "sweet": (19, 31), "max": 36},
                9: {"min": 13, "sweet": (17, 28), "max": 32},
                10: {"min": 12, "sweet": (15, 25), "max": 29},
                12: {"min": 10, "sweet": (12, 21), "max": 25},
            }
        }
    },
    "Slingshot": {
        "Machine V2": {
            "type": "5-Strut Big Air",
            "material": "Dacron / 4x4 Canopy Tech",
            "sizes": {
                7: {"min": 19, "sweet": (23, 33), "max": 38},
                8: {"min": 17, "sweet": (20, 31), "max": 36},
                9: {"min": 15, "sweet": (18, 28), "max": 33},
                10: {"min": 13, "sweet": (16, 25), "max": 30},
                11: {"min": 11, "sweet": (14, 22), "max": 27},
                12: {"min": 10, "sweet": (13, 20), "max": 24},
            }
        },
        "Code V1": {
            "type": "3-Strut Freeride / All-Round",
            "material": "FrameL的基础轻量化",
            "sizes": {
                7: {"min": 18, "sweet": (21, 29), "max": 35},
                8: {"min": 16, "sweet": (19, 27), "max": 33},
                9: {"min": 14, "sweet": (17, 25), "max": 30},
                10: {"min": 12, "sweet": (15, 23), "max": 28},
                12: {"min": 10, "sweet": (12, 19), "max": 24},
            }
        }
    },
    "Harlem": {
        "Force": {
            "type": "3-Strut Big Air / Brainchild",
            "material": "PRO Titanium / Brainchild",
            "sizes": {
                7: {"min": 17, "sweet": (21, 33), "max": 38},
                8: {"min": 15, "sweet": (19, 31), "max": 36},
                9: {"min": 13, "sweet": (17, 28), "max": 33},
                10: {"min": 11, "sweet": (14, 24), "max": 30},
                12: {"min": 9.5, "sweet": (12, 20), "max": 26},
            }
        }
    }
}


def normalize_str(s: str) -> str:
    import re
    return re.sub(r"[\s\-_/]", "", s.lower())


def lookup_kite_specs(brand: str, model: str, size: float) -> dict:
    """
    Looks up exact manufacturer specifications for a kite.
    Falls back to closest model or heuristic if not explicitly found.
    """
    norm_b = normalize_str(brand)
    norm_m = normalize_str(model)

    for b_name, models in KITE_CATALOG.items():
        if normalize_str(b_name) == norm_b:
            for m_name, specs in models.items():
                if normalize_str(m_name) == norm_m:
                    sizes = specs["sizes"]
                    # exact size match
                    if size in sizes:
                        return {
                            "brand": b_name,
                            "model": m_name,
                            "size": size,
                            "type": specs["type"],
                            "material": specs["material"],
                            **sizes[size]
                        }
                    # find closest size
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
    baseline_min = round(135.0 / (size + 1.5), 1)
    baseline_max = round(baseline_min * 2.3, 1)
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
