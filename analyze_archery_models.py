#!/usr/bin/env python3
"""
Analyze 11 OpenSim models for archery relevance.
Scores each model on muscle coverage and body structure detail.
"""

import json
import re
from collections import defaultdict

# Load data
with open('/home/z/my-project/download/all_muscles_v3.json') as f:
    muscle_data = json.load(f)

with open('/home/z/my-project/download/model_body_maps.json') as f:
    body_data = json.load(f)

# Define archery-critical muscle groups with search patterns
ARCHERY_MUSCLE_GROUPS = {
    "Trapezius": {
        "weight": 10,
        "patterns": [r"trap", r"trapez"],
    },
    "Rhomboids": {
        "weight": 9,
        "patterns": [r"rhomboid", r"rhomb"],
    },
    "Levator Scapulae": {
        "weight": 7,
        "patterns": [r"levator", r"lev_sc", r"levscap"],
    },
    "Serratus Anterior": {
        "weight": 8,
        "patterns": [r"serratus", r"serrat", r"serr_ant", r"serrant"],
    },
    "Deltoid (all)": {
        "weight": 10,
        "patterns": [r"delt", r"deltoid"],
    },
    "Deltoid (posterior)": {
        "weight": 10,
        "patterns": [r"delt.*post", r"post.*delt", r"delt2", r"delt_2", r"DELT2"],
    },
    "Supraspinatus": {
        "weight": 9,
        "patterns": [r"supraspin", r"suprasp", r"supra_spin", r"supspin"],
    },
    "Infraspinatus": {
        "weight": 9,
        "patterns": [r"infraspin", r"infrasp", r"infra_spin", r"infspin"],
    },
    "Subscapularis": {
        "weight": 8,
        "patterns": [r"subscap", r"sub_scap", r"subscapul"],
    },
    "Teres Minor": {
        "weight": 7,
        "patterns": [r"teres.*min", r"ter_min", r"termin", r"teres_min"],
    },
    "Latissimus Dorsi": {
        "weight": 10,
        "patterns": [r"latiss", r"lat_dors", r"latdors", r"lats", r"lat_"],
    },
    "Teres Major": {
        "weight": 9,
        "patterns": [r"teres.*maj", r"ter_maj", r"termaj", r"teres_maj"],
    },
    "Triceps Brachii": {
        "weight": 10,
        "patterns": [r"triceps", r"tric", r"tri_br", r"tribr"],
    },
    "Triceps (long head)": {
        "weight": 10,
        "patterns": [r"triceps.*long", r"tric.*long", r"TRIlong", r"tri_long", r"TRI1", r"tric1"],
    },
    "Biceps Brachii": {
        "weight": 8,
        "patterns": [r"biceps", r"bic_br", r"bicbr"],
    },
    "Flexor Carpi Radialis": {
        "weight": 8,
        "patterns": [r"flex.*carp.*rad", r"fcr", r"flcrad", r"fl_car_rad"],
    },
    "Flexor Carpi Ulnaris": {
        "weight": 8,
        "patterns": [r"flex.*carp.*uln", r"fcu", r"flculn", r"fl_car_uln"],
    },
    "Extensor Carpi Radialis": {
        "weight": 7,
        "patterns": [r"ext.*carp.*rad", r"ecr", r"ecrb", r"ecrl", r"excrad", r"ext_car_rad"],
    },
    "Extensor Carpi Ulnaris": {
        "weight": 7,
        "patterns": [r"ext.*carp.*uln", r"ecu", r"exculn", r"ext_car_uln"],
    },
    "Finger Flexors": {
        "weight": 9,
        "patterns": [r"flex.*dig", r"flex.*finger", r"fds", r"fdp", r"fl_dig", r"profund", r"sublim"],
    },
    "Finger Extensors": {
        "weight": 9,
        "patterns": [r"ext.*dig", r"ext.*finger", r"edc", r"ex_dig", r"extensor_dig"],
    },
    "Pronator Teres": {
        "weight": 6,
        "patterns": [r"pronator", r"pron.*ter", r"pron_ter", r"prontro"],
    },
    "Sternocleidomastoid": {
        "weight": 6,
        "patterns": [r"sternocleid", r"stern.*mast", r"scm", r"stern_mast"],
    },
    "Erector Spinae": {
        "weight": 8,
        "patterns": [r"erector", r"erect.*spin", r"iliocost", r"longiss", r"spinalis", r"LTpT", r"LTpL", r"E0_"],
    },
    "Obliques": {
        "weight": 7,
        "patterns": [r"oblique", r"obl", r"ext_obl", r"int_obl", r"internal_obl", r"external_obl"],
    },
    "Rectus Abdominis": {
        "weight": 7,
        "patterns": [r"rect.*abd", r"rect_abd", r"rectabd", r"rectus_abd"],
    },
    "Gluteus": {
        "weight": 7,
        "patterns": [r"glut", r"glute", r"gmax", r"gmed", r"gmin"],
    },
    "Quadriceps": {
        "weight": 6,
        "patterns": [r"quad", r"rect.*fem", r"vas.*lat", r"vas.*med", r"vas.*int", r"rec_fem", r"vas_lat", r"vas_med"],
    },
    "Hamstrings": {
        "weight": 6,
        "patterns": [r"hamstr", r"biceps.*fem", r"semi.*tend", r"semi.*memb", r"bflh", r"bfsh", r"semimem", r"semiten"],
    },
    "Pectoralis": {
        "weight": 7,
        "patterns": [r"pect", r"pectoral", r"pec_maj", r"pec_min"],
    },
}


def find_matching_muscles(muscle_names, patterns):
    """Find all muscle names matching any of the given patterns."""
    matches = set()
    for name in muscle_names:
        name_lower = name.lower()
        for pattern in patterns:
            if re.search(pattern, name_lower):
                matches.add(name)
                break
    return matches


def analyze_model(model_name, muscles, bodies):
    """Analyze a single model for archery relevance."""
    muscle_names = [m["name"] for m in muscles]
    body_names = list(bodies.keys()) if bodies else []
    body_names_lower = [b.lower() for b in body_names]

    results = {
        "model": model_name,
        "total_muscles": len(muscles),
        "muscle_groups_found": {},
        "muscle_groups_missing": {},
        "groups_found_count": 0,
        "groups_total": len(ARCHERY_MUSCLE_GROUPS),
        "body_features": {},
        "weighted_score": 0,
        "max_weighted_score": 0,
        "muscle_names_sample": muscle_names[:5],  # for debugging
    }

    # Check each archery muscle group
    total_weighted = 0
    max_weighted = 0
    for group_name, group_info in ARCHERY_MUSCLE_GROUPS.items():
        matches = find_matching_muscles(muscle_names, group_info["patterns"])
        weight = group_info["weight"]
        max_weighted += weight

        if matches:
            results["muscle_groups_found"][group_name] = {
                "matches": sorted(list(matches)),
                "count": len(matches),
                "weight": weight
            }
            total_weighted += weight
        else:
            results["muscle_groups_missing"][group_name] = {
                "weight": weight,
            }

    results["groups_found_count"] = len(results["muscle_groups_found"])
    results["weighted_score"] = total_weighted
    results["max_weighted_score"] = max_weighted

    # Check body features
    bf = {}

    # Full body check
    has_lower = any("femur" in b.lower() for b in body_names)
    has_upper = any("humerus" in b.lower() for b in body_names)
    bf["full_body"] = has_lower and has_upper

    # Scapula as separate body
    scapula_bodies = [b for b in body_names if "scapula" in b.lower()]
    bf["separate_scapula"] = len(scapula_bodies) > 0
    bf["scapula_bilateral"] = len(scapula_bodies) >= 2
    bf["scapula_names"] = scapula_bodies

    # Hand detail
    hand_bodies = [b for b in body_names if "hand" in b.lower()]
    bf["hand_bodies"] = hand_bodies
    bf["has_hand"] = len(hand_bodies) > 0
    bf["hand_detail"] = len(hand_bodies)

    # Wrist/carpal detail
    wrist_bodies = [b for b in body_names if any(w in b.lower() for w in ["wrist", "carpal", "proximal_row", "distal_row"])]
    bf["wrist_bodies"] = wrist_bodies
    bf["wrist_detail"] = len(wrist_bodies)
    bf["has_wrist_detail"] = len(wrist_bodies) > 0

    # Spine detail
    spine_bodies = [b for b in body_names if any(v in b.lower() for v in ["lumbar", "thoracic", "cervical", "cerv"])]
    bf["spine_bodies"] = len(spine_bodies)
    bf["has_spine_detail"] = len(spine_bodies) > 5

    # Individual ribs
    rib_bodies = [b for b in body_names if "rib" in b.lower()]
    bf["rib_bodies"] = len(rib_bodies)

    # Head/neck detail
    head_bodies = [b for b in body_names if any(h in b.lower() for h in ["head", "skull", "neck", "jaw"])]
    bf["head_detail"] = len(head_bodies)
    bf["head_bodies"] = head_bodies

    # Patella
    has_patella = any("patella" in b.lower() for b in body_names)
    bf["has_patella"] = has_patella

    # Total body count
    bf["total_bodies"] = len(body_names)

    results["body_features"] = bf
    return results


def compute_archery_score(results):
    """Compute a 0-100 archery relevance score."""
    # Component 1: Muscle coverage (weighted) - 60% of total score
    muscle_pct = results["weighted_score"] / results["max_weighted_score"] if results["max_weighted_score"] > 0 else 0
    muscle_score = muscle_pct * 60

    # Component 2: Body structure - 40% of total score
    bf = results["body_features"]
    body_score = 0

    # Full body (8 points)
    if bf.get("full_body"):
        body_score += 8

    # Separate scapula bilateral (8 points)
    if bf.get("scapula_bilateral"):
        body_score += 8
    elif bf.get("separate_scapula"):
        body_score += 4

    # Hand detail (6 points)
    hand_detail = bf.get("hand_detail", 0)
    body_score += min(6, hand_detail * 2)

    # Wrist detail (4 points)
    if bf.get("has_wrist_detail"):
        body_score += 4

    # Spine detail (6 points)
    spine = bf.get("spine_bodies", 0)
    body_score += min(6, spine * 0.3)

    # Head/neck (4 points)
    head = bf.get("head_detail", 0)
    body_score += min(4, head * 1.0)

    # Ribs (2 points)
    ribs = bf.get("rib_bodies", 0)
    body_score += min(2, ribs * 0.1)

    # Patella (2 points)
    if bf.get("has_patella"):
        body_score += 2

    total_score = muscle_score + body_score
    return round(min(100, total_score), 1)


# Run analysis
all_results = {}
model_names = ["M7", "M7_18", "M8", "M8_Corr", "M8_Norm", "M2", "M4", "M6", "M9", "Raj", "ULB"]

for model_name in model_names:
    muscles = muscle_data.get(model_name, [])
    bodies = body_data.get(model_name, {})
    results = analyze_model(model_name, muscles, bodies)
    results["archery_score"] = compute_archery_score(results)
    all_results[model_name] = results

# Sort by archery score
sorted_models = sorted(all_results.values(), key=lambda x: x["archery_score"], reverse=True)

# ===================== PRINT RESULTS =====================

print("=" * 130)
print("ARCHERY MODEL ANALYSIS - OpenSim Model Comparison for Archery Simulation")
print("=" * 130)

# ---------- 1. SUMMARY TABLE ----------
print("\n" + "=" * 130)
print("1. SUMMARY COMPARISON TABLE")
print("=" * 130)

header = f"{'Model':<10} {'#Muscles':>9} {'Groups':>12} {'Weighted':>12} {'Muscle%':>9} {'Body%':>8} {'ARCHERY':>8} {'RANK':>5}"
print(header)
print("-" * 130)

for rank, r in enumerate(sorted_models, 1):
    muscle_pct = round(r["weighted_score"] / r["max_weighted_score"] * 100, 1) if r["max_weighted_score"] else 0
    # Compute body component for display
    bf = r["body_features"]
    body_pts = 0
    if bf.get("full_body"): body_pts += 8
    if bf.get("scapula_bilateral"): body_pts += 8
    elif bf.get("separate_scapula"): body_pts += 4
    body_pts += min(6, bf.get("hand_detail", 0) * 2)
    if bf.get("has_wrist_detail"): body_pts += 4
    body_pts += min(6, bf.get("spine_bodies", 0) * 0.3)
    body_pts += min(4, bf.get("head_detail", 0) * 1.0)
    body_pts += min(2, bf.get("rib_bodies", 0) * 0.1)
    if bf.get("has_patella"): body_pts += 2
    body_pct = round(body_pts / 40 * 100, 1)

    row = f"{r['model']:<10} {r['total_muscles']:>9} {r['groups_found_count']:>5}/{r['groups_total']:<5} {r['weighted_score']:>5}/{r['max_weighted_score']:<5} {muscle_pct:>8.1f}% {body_pct:>6.1f}% {r['archery_score']:>7.1f} {rank:>5}"
    print(row)

# ---------- 2. MUSCLE GROUP PRESENCE MATRIX ----------
print("\n" + "=" * 130)
print("2. MUSCLE GROUP PRESENCE MATRIX")
print("=" * 130)

group_names = list(ARCHERY_MUSCLE_GROUPS.keys())
# Header
header = f"{'Muscle Group':<25}"
for mn in model_names:
    header += f" {mn:>7}"
print(header)
print("-" * 130)

for gn in group_names:
    row = f"{gn:<25}"
    for mn in model_names:
        r = all_results[mn]
        if gn in r["muscle_groups_found"]:
            count = r["muscle_groups_found"][gn]["count"]
            row += f" {'Y(' + str(count) + ')':>7}"
        else:
            row += f" {'---':>7}"
    print(row)

# ---------- 3. BODY STRUCTURE COMPARISON ----------
print("\n" + "=" * 130)
print("3. BODY STRUCTURE COMPARISON")
print("=" * 130)

features = [
    ("Full Body", "full_body", "bool"),
    ("Separate Scapula", "separate_scapula", "bool"),
    ("Bilateral Scapula", "scapula_bilateral", "bool"),
    ("Scapula Names", "scapula_names", "list"),
    ("Hand Bodies", "hand_bodies", "list"),
    ("Wrist/Carpal Detail", "wrist_bodies", "list"),
    ("Spine Vertebrae", "spine_bodies", "int"),
    ("Rib Bodies", "rib_bodies", "int"),
    ("Head/Neck Bodies", "head_detail", "int"),
    ("Has Patella", "has_patella", "bool"),
    ("Total Bodies", "total_bodies", "int"),
]

for feat_name, feat_key, feat_type in features:
    row = f"{feat_name:<25}"
    for mn in model_names:
        bf = all_results[mn]["body_features"]
        val = bf.get(feat_key, "N/A")
        if feat_type == "bool":
            row += f" {'Y' if val else 'N':>7}"
        elif feat_type == "int":
            row += f" {str(val):>7}"
        elif feat_type == "list":
            if isinstance(val, list):
                abbreviated = ", ".join(str(v) for v in val[:3])
                if len(val) > 3:
                    abbreviated += f"... +{len(val)-3}"
                row += f" {abbreviated:>7}"
            else:
                row += f" {str(val):>7}"
        else:
            row += f" {str(val):>7}"
    print(row)

# ---------- 4. MISSING CRITICAL MUSCLES ----------
print("\n" + "=" * 130)
print("4. MISSING CRITICAL MUSCLES (weight >= 9) - HIGHEST SCORED MODELS FIRST")
print("=" * 130)

for r in sorted_models[:5]:
    missing_critical = {k: v for k, v in r["muscle_groups_missing"].items() if v["weight"] >= 9}
    print(f"\n  {r['model']} (Score: {r['archery_score']}) - Missing critical groups:")
    if missing_critical:
        for gn, info in missing_critical.items():
            print(f"    - {gn} (weight: {info['weight']})")
    else:
        print(f"    None! All critical muscle groups present.")

# ---------- 5. DETAILED MUSCLE MATCHES FOR TOP 3 ----------
print("\n" + "=" * 130)
print("5. DETAILED MUSCLE MATCHES FOR TOP 3 MODELS")
print("=" * 130)

for r in sorted_models[:3]:
    print(f"\n{'='*80}")
    print(f"  {r['model']} - Total muscles: {r['total_muscles']}, Archery Score: {r['archery_score']}")
    print(f"{'='*80}")
    for gn in sorted(r["muscle_groups_found"].keys()):
        info = r["muscle_groups_found"][gn]
        matches_str = ", ".join(info["matches"][:6])
        if len(info["matches"]) > 6:
            matches_str += f"... +{len(info['matches'])-6} more"
        print(f"    {gn:<25} ({info['count']:>2} muscles): {matches_str}")

    if r["muscle_groups_missing"]:
        print(f"\n    MISSING GROUPS:")
        for gn, info in r["muscle_groups_missing"].items():
            print(f"      - {gn} (weight: {info['weight']})")

# ---------- 6. RECOMMENDATION ----------
print("\n" + "=" * 130)
print("6. RECOMMENDATION")
print("=" * 130)

best = sorted_models[0]
second = sorted_models[1] if len(sorted_models) > 1 else None
third = sorted_models[2] if len(sorted_models) > 2 else None

print(f"\n  PRIMARY RECOMMENDATION: {best['model']}")
print(f"    Archery Score: {best['archery_score']}/100")
print(f"    Total Muscles: {best['total_muscles']}")
print(f"    Archery Groups Found: {best['groups_found_count']}/{best['groups_total']}")
print(f"    Weighted Muscle Score: {best['weighted_score']}/{best['max_weighted_score']}")
bf = best["body_features"]
print(f"    Full Body: {'Yes' if bf.get('full_body') else 'No'}")
print(f"    Bilateral Scapula: {'Yes' if bf.get('scapula_bilateral') else 'No'}")
print(f"    Hand Detail: {bf.get('hand_detail', 0)} hand bodies")
print(f"    Spine Detail: {bf.get('spine_bodies', 0)} vertebral bodies")
print(f"    Wrist Detail: {'Yes' if bf.get('has_wrist_detail') else 'No'}")

if second:
    print(f"\n  ALTERNATIVE: {second['model']} (Score: {second['archery_score']})")
    # Note what it has that best doesn't
    second_only = set(second["muscle_groups_found"].keys()) - set(best["muscle_groups_found"].keys())
    best_only = set(best["muscle_groups_found"].keys()) - set(second["muscle_groups_found"].keys())
    if second_only:
        print(f"    Groups in {second['model']} but not {best['model']}: {', '.join(second_only)}")
    if best_only:
        print(f"    Groups in {best['model']} but not {second['model']}: {', '.join(best_only)}")

if third:
    print(f"\n  THIRD OPTION: {third['model']} (Score: {third['archery_score']})")

# Save detailed results to JSON
output_path = '/home/z/my-project/download/archery_model_analysis.json'
with open(output_path, 'w') as f:
    # Convert sets to lists for JSON serialization
    serializable = {}
    for mn, r in all_results.items():
        sr = dict(r)
        sr["body_features"] = dict(r["body_features"])
        # Convert lists in body features
        for key, val in sr["body_features"].items():
            if isinstance(val, (set, list)):
                sr["body_features"][key] = list(val) if isinstance(val, set) else val
        serializable[mn] = sr
    json.dump(serializable, f, indent=2, default=str)

print(f"\n\nDetailed results saved to: {output_path}")
