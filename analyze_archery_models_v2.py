#!/usr/bin/env python3
"""
Analyze 11 OpenSim models for archery relevance - CORRECTED version.
Fixed pattern matching for abbreviated OpenSim muscle naming conventions.
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
# CORRECTED: Added abbreviated OpenSim naming conventions (INFSP, SUPSP, TRIlong, etc.)
ARCHERY_MUSCLE_GROUPS = {
    # === UPPER BODY / SHOULDER GIRDLE ===
    "Trapezius": {
        "weight": 10,
        "patterns": [r"\btrap\b", r"trap_", r"trap_acr", r"trap_cl", r"trap_inf", r"trapez"],
    },
    "Rhomboids": {
        "weight": 9,
        "patterns": [r"\brhomb", r"rhomboid", r"\bRHM\b", r"\bRhm\b"],
    },
    "Levator Scapulae": {
        "weight": 7,
        "patterns": [r"levator.*scap", r"lev_scap", r"levscap", r"\blevscap\b"],
    },
    "Serratus Anterior": {
        "weight": 8,
        "patterns": [r"\bSerrAnt\b", r"serratus", r"\bserrat\b", r"serr_ant"],
    },

    # === SHOULDER ===
    "Deltoid (all)": {
        "weight": 10,
        "patterns": [r"\bDELT\d", r"\bdelt\d", r"\bdeltoid\b", r"delt_"],
    },
    "Deltoid (posterior)": {
        "weight": 10,
        "patterns": [r"\bDELT2\b", r"\bdelt2\b", r"delt.*post", r"post.*delt"],
    },
    "Supraspinatus": {
        "weight": 9,
        "patterns": [r"\bSUPSP\b", r"\bsupsp\b", r"\bsuprasp", r"supraspin", r"supra_spin"],
    },
    "Infraspinatus": {
        "weight": 9,
        "patterns": [r"\bINFSP\b", r"\binfsp\b", r"\binfrasp", r"infraspin", r"infra_spin"],
    },
    "Subscapularis": {
        "weight": 8,
        "patterns": [r"\bSUBSC\b", r"\bsubsc\b", r"\bsubscap", r"subscapul", r"sub_scap"],
    },
    "Teres Minor": {
        "weight": 7,
        "patterns": [r"\bTMIN\b", r"\btmin\b", r"teres.*min", r"ter_min", r"teres_min"],
    },

    # === BACK ===
    "Latissimus Dorsi": {
        "weight": 10,
        # Match LAT1/LAT2/LAT3 (M8/ULB convention) and LD_ (M7 convention)
        # Exclude false positives from vaslat, gaslat, TRIlat
        "patterns": [r"\bLAT\d\b", r"\blat\d\b", r"\bLD_", r"\bLD\b", r"\blatiss", r"\blat_dors"],
    },
    "Teres Major": {
        "weight": 9,
        "patterns": [r"\bTMAJ\b", r"\btmaj\b", r"teres.*maj", r"ter_maj", r"teres_maj"],
    },

    # === ARM ===
    "Triceps Brachii": {
        "weight": 10,
        # Match TRIlat, TRIlong, TRImed and also triceps/tri_br
        "patterns": [r"\bTRI(lat|long|med)\b", r"\btri(lat|long|med)\b", r"\btriceps\b", r"\btri_br\b", r"\btribr\b"],
    },
    "Triceps (long head)": {
        "weight": 10,
        "patterns": [r"\bTRIlong\b", r"\btri_long\b", r"\btrilong\b", r"triceps.*long"],
    },
    "Biceps Brachii": {
        "weight": 8,
        "patterns": [r"\bBIC(long|short)\b", r"\bbic(long|short)\b", r"\bbiceps\b", r"\bbic_br\b", r"\bbicbr\b"],
    },

    # === FOREARM/HAND ===
    "Flexor Carpi Radialis": {
        "weight": 8,
        "patterns": [r"\bFCR\b", r"\bfcr\b", r"flcrad", r"fl_car_rad", r"flex.*carp.*rad"],
    },
    "Flexor Carpi Ulnaris": {
        "weight": 8,
        "patterns": [r"\bFCU\b", r"\bfcu\b", r"flculn", r"fl_car_uln", r"flex.*carp.*uln"],
    },
    "Extensor Carpi Radialis": {
        "weight": 7,
        "patterns": [r"\bECR[BL]\b", r"\becr[bl]\b", r"\bECRB\b", r"\bECRL\b", r"excrad", r"ext.*carp.*rad"],
    },
    "Extensor Carpi Ulnaris": {
        "weight": 7,
        "patterns": [r"\bECU\b", r"\becu\b", r"exculn", r"ext.*carp.*uln"],
    },
    "Finger Flexors": {
        "weight": 9,
        "patterns": [r"\bFDP[I LRMR]?\b", r"\bFDS[I LRMR]?\b", r"\bfdp[i lrm]?\b", r"\bfds[i lrm]?\b", r"flex.*dig", r"profund", r"sublim"],
    },
    "Finger Extensors": {
        "weight": 9,
        "patterns": [r"\bEDC[I LRMR]?\b", r"\bedc[i lrm]?\b", r"\bEDM\b", r"\bedm\b", r"\bEIP\b", r"ext.*dig", r"extensor_dig"],
    },
    "Pronator Teres": {
        "weight": 6,
        "patterns": [r"\bPT\b", r"\bPT_\b", r"\bPTl\b", r"\bpron.*ter", r"pronator", r"pron_ter"],
    },

    # === NECK ===
    "Sternocleidomastoid": {
        "weight": 6,
        "patterns": [r"stern.*mast", r"stern_mast", r"cleid_mast", r"sternocleid", r"\bSCM\b"],
    },

    # === TRUNK/CORE ===
    "Erector Spinae": {
        "weight": 8,
        "patterns": [r"\bercspn\b", r"erector", r"iliocost", r"longiss", r"spinalis", r"\bLTpT\b", r"\bLTpL\b", r"\bE0_R\b"],
    },
    "Obliques": {
        "weight": 7,
        "patterns": [r"\bextobl\b", r"\bintobl\b", r"\bEO\d", r"\bIO\d", r"\boblique", r"ext_obl", r"int_obl", r"external_obl", r"internal_obl"],
    },
    "Rectus Abdominis": {
        "weight": 7,
        "patterns": [r"\brect_abd\b", r"rect.*abd", r"rectabd", r"rectus_abd"],
    },

    # === LOWER BODY ===
    "Gluteus": {
        "weight": 7,
        "patterns": [r"\bglmax\d", r"\bglmed\d", r"\bglmin\d", r"\bglut_", r"\bglut\.max", r"\bglute", r"\bgmax\d"],
    },
    "Quadriceps": {
        "weight": 6,
        "patterns": [r"\brecfem\b", r"\brect_fem\b", r"\bvas(lat|med|int)\b", r"\bvas_lat\b", r"\bvas_med\b", r"\bvas_int\b", r"\bquad", r"\bquadfem\b"],
    },
    "Hamstrings": {
        "weight": 6,
        "patterns": [r"\bbflh\b", r"\bbfsh\b", r"\bbifemlh\b", r"\bbifemsh\b", r"\bsemimem\b", r"\bsemiten\b", r"hamstr", r"biceps.*fem"],
    },
    "Pectoralis": {
        "weight": 7,
        "patterns": [r"\bPECM\d", r"\bpecm\d", r"\bpect\b", r"\bpect_", r"pectoral", r"pec_maj", r"pec_min"],
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
    }

    # Check each archery muscle group
    total_weighted = 0
    max_weighted = 0
    for group_name, group_info in ARCHERY_MUSCLE_GROUPS.items():
        matches = find_matching_muscles(muscle_names, group_info["patterns"])
        weight = group_info["weight"]
        max_weighted += weight

        if matches:
            # Filter out obvious false positives for Latissimus Dorsi
            if group_name == "Latissimus Dorsi":
                filtered = set()
                for m in matches:
                    m_lower = m.lower()
                    # Exclude vastus lateralis, gastrocnemius lateral, triceps lateral
                    if any(x in m_lower for x in ["vaslat", "vas_lat", "gaslat", "gas_lat", "trilat", "tri_lat"]):
                        continue
                    filtered.add(m)
                matches = filtered

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
print("ARCHERY MODEL ANALYSIS (CORRECTED) - OpenSim Model Comparison for Archery Simulation")
print("=" * 130)

# ---------- 1. SUMMARY TABLE ----------
print("\n" + "=" * 130)
print("1. SUMMARY COMPARISON TABLE (sorted by Archery Score)")
print("=" * 130)
print(f"{'Rank':<5} {'Model':<10} {'#Muscles':>9} {'Groups':>12} {'Weighted':>12} {'Muscle%':>9} {'BodyPts':>8} {'SCORE':>7}")
print("-" * 130)

for rank, r in enumerate(sorted_models, 1):
    muscle_pct = round(r["weighted_score"] / r["max_weighted_score"] * 100, 1) if r["max_weighted_score"] else 0
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

    row = f"{rank:<5} {r['model']:<10} {r['total_muscles']:>9} {r['groups_found_count']:>5}/{r['groups_total']:<5} {r['weighted_score']:>5}/{r['max_weighted_score']:<5} {muscle_pct:>8.1f}% {body_pts:>7.1f}/40 {r['archery_score']:>6.1f}"
    print(row)

# ---------- 2. MUSCLE GROUP PRESENCE MATRIX ----------
print("\n" + "=" * 130)
print("2. MUSCLE GROUP PRESENCE MATRIX (Y=Found, ---=Missing, numbers=match count)")
print("=" * 130)

group_names = list(ARCHERY_MUSCLE_GROUPS.keys())
header = f"{'Muscle Group':<25} {'Wt':>3}"
for mn in model_names:
    header += f" {mn:>7}"
print(header)
print("-" * 130)

for gn in group_names:
    weight = ARCHERY_MUSCLE_GROUPS[gn]["weight"]
    row = f"{gn:<25} {weight:>3}"
    for mn in model_names:
        r = all_results[mn]
        if gn in r["muscle_groups_found"]:
            count = r["muscle_groups_found"][gn]["count"]
            row += f" {'Y'+str(count):>7}"
        else:
            row += f" {'---':>7}"
    print(row)

# ---------- 3. BODY STRUCTURE COMPARISON ----------
print("\n" + "=" * 130)
print("3. BODY STRUCTURE COMPARISON")
print("=" * 130)

print(f"{'Feature':<25}", end="")
for mn in model_names:
    print(f" {mn:>10}", end="")
print()
print("-" * 130)

feature_rows = [
    ("Full Body", lambda bf: "Y" if bf.get("full_body") else "N"),
    ("Separate Scapula", lambda bf: "Y" if bf.get("separate_scapula") else "N"),
    ("Bilateral Scapula", lambda bf: "Y" if bf.get("scapula_bilateral") else "N"),
    ("Hand Bodies (#)", lambda bf: str(bf.get("hand_detail", 0))),
    ("Wrist/Carpal Detail", lambda bf: "Y" if bf.get("has_wrist_detail") else "N"),
    ("Spine Vertebrae (#)", lambda bf: str(bf.get("spine_bodies", 0))),
    ("Rib Bodies (#)", lambda bf: str(bf.get("rib_bodies", 0))),
    ("Head/Neck Bodies (#)", lambda bf: str(bf.get("head_detail", 0))),
    ("Has Patella", lambda bf: "Y" if bf.get("has_patella") else "N"),
    ("Total Bodies (#)", lambda bf: str(bf.get("total_bodies", 0))),
]

for feat_name, feat_fn in feature_rows:
    row = f"{feat_name:<25}"
    for mn in model_names:
        bf = all_results[mn]["body_features"]
        row += f" {feat_fn(bf):>10}"
    print(row)

# ---------- 4. DETAILED MATCHES FOR TOP MODELS ----------
print("\n" + "=" * 130)
print("4. DETAILED MUSCLE MATCHES FOR TOP 5 MODELS")
print("=" * 130)

for r in sorted_models[:5]:
    print(f"\n{'='*90}")
    print(f"  {r['model']} - Total: {r['total_muscles']} muscles | Archery Score: {r['archery_score']}/100 | Groups: {r['groups_found_count']}/{r['groups_total']}")
    print(f"{'='*90}")
    for gn in sorted(r["muscle_groups_found"].keys()):
        info = r["muscle_groups_found"][gn]
        matches_str = ", ".join(info["matches"][:8])
        if len(info["matches"]) > 8:
            matches_str += f" ... +{len(info['matches'])-8} more"
        print(f"    {gn:<25} w={info['weight']:>2} ({info['count']:>2} mus): {matches_str}")

    if r["muscle_groups_missing"]:
        print(f"\n    MISSING ({len(r['muscle_groups_missing'])} groups):")
        for gn, info in sorted(r["muscle_groups_missing"].items(), key=lambda x: -x[1]["weight"]):
            print(f"      - {gn} (weight: {info['weight']})")

# ---------- 5. COMPLEMENTARY ANALYSIS ----------
print("\n" + "=" * 130)
print("5. COMPLEMENTARY ANALYSIS - Which models best complement each other")
print("=" * 130)

# For top 3 models, show which missing groups could be filled by other models
for r in sorted_models[:3]:
    missing = set(r["muscle_groups_missing"].keys())
    print(f"\n  {r['model']} is missing: {', '.join(sorted(missing))}")
    for other_r in sorted_models:
        if other_r["model"] == r["model"]:
            continue
        other_found = set(other_r["muscle_groups_found"].keys())
        can_fill = missing & other_found
        if can_fill:
            print(f"    -> {other_r['model']} has these: {', '.join(sorted(can_fill))}")

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
print(f"    Wrist/Carpal Detail: {'Yes' if bf.get('has_wrist_detail') else 'No'}")

if second:
    print(f"\n  ALTERNATIVE: {second['model']} (Score: {second['archery_score']})")
    second_only = set(second["muscle_groups_found"].keys()) - set(best["muscle_groups_found"].keys())
    best_only = set(best["muscle_groups_found"].keys()) - set(second["muscle_groups_found"].keys())
    if second_only:
        print(f"    Groups in {second['model']} but not {best['model']}: {', '.join(second_only)}")
    if best_only:
        print(f"    Groups in {best['model']} but not {second['model']}: {', '.join(best_only)}")

if third:
    print(f"\n  THIRD OPTION: {third['model']} (Score: {third['archery_score']})")

# Hybrid recommendation
print(f"\n  HYBRID STRATEGY RECOMMENDATION:")
# Find which model complements the best one most
best_missing = set(best["muscle_groups_missing"].keys())
best_complement = None
best_complement_fill = 0
for r in sorted_models[1:]:
    can_fill = len(best_missing & set(r["muscle_groups_found"].keys()))
    if can_fill > best_complement_fill:
        best_complement_fill = can_fill
        best_complement = r

if best_complement:
    can_fill = best_missing & set(best_complement["muscle_groups_found"].keys())
    print(f"    Best complement to {best['model']}: {best_complement['model']}")
    print(f"    Can fill {best_complement_fill} missing groups: {', '.join(sorted(can_fill))}")
    combined_score = best['weighted_score'] + sum(ARCHERY_MUSCLE_GROUPS[g]["weight"] for g in can_fill)
    print(f"    Combined weighted score: {combined_score}/{best['max_weighted_score']} ({round(combined_score/best['max_weighted_score']*100,1)}%)")

# Save detailed results to JSON
output_path = '/home/z/my-project/download/archery_model_analysis.json'
with open(output_path, 'w') as f:
    serializable = {}
    for mn, r in all_results.items():
        sr = dict(r)
        sr["body_features"] = dict(r["body_features"])
        for key, val in sr["body_features"].items():
            if isinstance(val, set):
                sr["body_features"][key] = list(val)
        serializable[mn] = sr
    json.dump(serializable, f, indent=2, default=str)

print(f"\n\nDetailed results saved to: {output_path}")
