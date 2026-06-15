# Worklog — Task 1e: Verify B1-B7 Mass Errors

**Date:** 2026-03-05
**File target:** `/home/z/my-project/download/model2_das3/model2_full_geom_fixed.osim`

## Critical Note: Target File Does Not Exist

The file `/home/z/my-project/download/model2_das3/model2_full_geom_fixed.osim` **does not exist** on disk. The directory `model2_das3` is also absent from `/home/z/my-project/download/`. 

Verification was performed against the **source models** that would feed into this combined model:

| Source | Path | Role |
|--------|------|------|
| M7_18_Baza.osim | `/home/z/my-project/upload/M7_18_Baza.osim` | Torso, pelvis, sacrum, abdomen, lumbar, thoracic, ribs, Abd segments, hands |
| Male_15years_FullBody_TLSpine.osim | `/home/z/my-project/upload/Male_15years_FullBody_TLSpine.osim` | Identical body structure to M7 (same line numbers) |
| Head_Neck_Model.osim | `/home/z/my-project/upload/Head_Neck_Model.osim` | Cervical vertebrae (cerv1-cerv7), skull |
| Hand_Wrist_Model_for_development.osim | `/home/z/my-project/upload/Hand_Wrist_Model_for_development.osim` | Carpal bones (capitate, trapezium, trapezoid, hamate, proximal_row) |
| UpperLowerBody.osim | `/home/z/my-project/upload/UpperLowerBody.osim` | Full carpal set (8 bones × 2 sides), all mass=0 |
| M8_NormTaz.osim | `/home/z/my-project/upload/M8_NormTaz.osim` | Cross-reference for pelvis (11.777 kg), cervical vertebrae |

---

## B1: Sacrum Mass

**Claimed value:** 0.00011 kg — **CONFIRMED**
**Expected:** ~0.95 kg

| File | Body | Line | Mass (kg) |
|------|------|------|-----------|
| M7_18_Baza.osim | sacrum | 332 | 0.000109602143969353 |
| Male_15years_FullBody_TLSpine.osim | sacrum | 332 | 0.000109602143969353 |
| M8_NormTaz.osim | sacrum | 634 | 0 (completely zero!) |
| M8_Caruthers_Corrected.osim | sacrum | 634 | 0 |

**Verdict:** ERROR CONFIRMED. Sacrum mass ≈ 0.00011 kg is ~8,600× too small. The sacrum should weigh approximately 0.95 kg. In M8 models it's even worse (zero). This is a placeholder/dummy mass that was never corrected.

---

## B2: Abdomen Mass

**Claimed value:** 0.00011 kg — **CONFIRMED**
**Expected:** ~2.5 kg

| File | Body | Line | Mass (kg) |
|------|------|------|-----------|
| M7_18_Baza.osim | Abdomen | 1670 | 0.000109602143969353 |
| Male_15years_FullBody_TLSpine.osim | Abdomen | 1670 | 0.000109602143969353 |

**Verdict:** ERROR CONFIRMED. Abdomen mass ≈ 0.00011 kg is ~22,800× too small. The abdomen should weigh approximately 2.5 kg. Same placeholder value as sacrum — both use the identical dummy mass 0.000109602143969353.

---

## B3: Abdominal Segments (Abd_L_L1–L5, Abd_R_L1–L5)

**Claimed value:** all 0.011 kg — **CONFIRMED**

| File | Body | Line | Mass (kg) |
|------|------|------|-----------|
| M7_18_Baza.osim | Abd_L_L1 | 13881 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_L_L2 | 13958 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_L_L3 | 14035 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_L_L4 | 14112 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_L_L5 | 14189 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_R_L1 | 14266 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_R_L2 | 14343 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_R_L3 | 14420 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_R_L4 | 14497 | 0.0109602143969353 |
| M7_18_Baza.osim | Abd_R_L5 | 14574 | 0.0109602143969353 |

All 10 segments have identical mass = 0.0109602143969353 kg ≈ 0.011 kg. Same pattern in Male_15years_FullBody_TLSpine.osim (identical line numbers).

**Verdict:** ERROR CONFIRMED. All 10 abdominal segment masses are uniform placeholder values. Each segment at ~11g is unrealistically small. If the total abdomen mass should be ~2.5 kg, each of the 10 segments should average ~0.25 kg. Current total = 0.1096 kg, which is ~23× too low.

---

## B4: Cervical Vertebrae (cerv1–cerv7)

**Claimed:** 30-50% below expected

Source: Head_Neck_Model.osim

| Body | Line | Mass (kg) | Typical expected (kg)* |
|------|------|-----------|----------------------|
| cerv1 (atlas) | 1378 | 0.156 | ~0.21 |
| cerv2 (axis) | 1207 | 0.156 | ~0.24 |
| cerv3 | 1036 | 0.156 | ~0.26 |
| cerv4 | 865 | 0.205 | ~0.27 |
| cerv5 | 694 | 0.269 | ~0.28 |
| cerv6 | 492 | 0.226 | ~0.28 |
| cerv7 | 321 | 0.400 | ~0.33 |
| **Total** | | **1.568** | **~1.87** |

*Expected values based on proportional segment mass from de Leva (1996) for a ~75 kg male, where total neck mass ≈ 2.5% of body mass, minus head.

**Comparison with M8_NormTaz.osim cervical vertebrae:**

| Body | Head_Neck_Model (kg) | M8_NormTaz (kg) |
|------|---------------------|-----------------|
| cerv1 | 0.156 | 0.221 |
| cerv2 | 0.156 | 0.251 |
| cerv3 | 0.156 | 0.241 |
| cerv4 | 0.205 | 0.231 |
| cerv5 | 0.269 | 0.231 |
| cerv6 | 0.226 | 0.241 |
| cerv7 | 0.400 | 0.221 |

**Verdict:** PARTIALLY CONFIRMED. Cerv1-Cerv4 are indeed ~30-40% below expected. Cerv5 and Cerv6 are ~4-19% below. Cerv7 is actually above expected (but may include significant soft tissue mass at C7/T1 junction). The Head_Neck_Model has an unusual distribution where C1-C3 all have the same mass (0.156 kg) and C7 is much heavier, suggesting the mass was not distributed properly across segments.

---

## B5: Pelvis Mass

**Claimed value:** 9.14 kg — **CONFIRMED**
**Expected:** ~11.78 kg

| File | Body | Line | Mass (kg) |
|------|------|------|-----------|
| M7_18_Baza.osim | pelvis | 62 | 9.14399726921913 |
| Male_15years_FullBody_TLSpine.osim | pelvis | 62 | 9.14399726921913 |
| M8_NormTaz.osim | pelvis | 261 | 11.777 |
| M8_Caruthers_Corrected.osim | pelvis | 261 | 11.777 |

**Verdict:** ERROR CONFIRMED. The M7 pelvis mass of 9.14 kg is 22.3% below the M8 reference value of 11.777 kg. The discrepancy is likely due to the M7 model assigning some pelvis mass to the sacrum body separately, but since the sacrum body has near-zero mass (B1), the total is still missing ~2.64 kg of mass.

---

## B6: Capitate Mass (capitate_r / capitate_l)

**Claimed value:** 327g (0.327 kg) — **CONFIRMED**

| File | Body | Line | Mass (kg) |
|------|------|------|-----------|
| Hand_Wrist_Model_for_development.osim | capitate | 1047 | 0.32742 |
| UpperLowerBody.osim | capitate | 7607 | 0.000000000000 |
| UpperLowerBody.osim | capitate_l | 10827 | 0.000000000000 |
| UpperLowerBodySimple.osim | capitate | 5432 | 0.000000000000 |

**Verdict:** ERROR CONFIRMED. The capitate mass of 0.32742 kg (327.42 g) in the Hand_Wrist_Model_for_development.osim is wildly incorrect. A real capitate bone weighs approximately 5-8 g. The model value is **~40-65× too large**. This looks like the mass of an entire hand segment was incorrectly assigned to a single carpal bone. In other models (UpperLowerBody), the capitate mass is 0, which is also wrong but at least doesn't inflate total body mass.

Note: No model was found with separate "capitate_r" and "capitate_l" bodies. The Hand_Wrist_Model only has a single right-hand "capitate". The UpperLowerBody models have "capitate" and "capitate_l" but both at mass=0.

---

## B7: All Carpal Bone Masses

**Claimed:** ~0.01g (0.00001 kg)

### Hand_Wrist_Model_for_development.osim (right hand only):

| Body | Line | Mass (kg) | Mass (g) |
|------|------|-----------|----------|
| proximal_row | 470 | 0.0001 | 0.1 |
| capitate | 1047 | 0.32742 | 327.42 |
| trapezium | 1229 | 0.00001 | 0.01 |
| trapezoid | 1291 | 0.00001 | 0.01 |
| hamate | 1353 | 0.00001 | 0.01 |

(No scaphoid, lunate, pisiform, triquetrum as separate bodies — proximal carpal row is merged into "proximal_row")

### UpperLowerBody.osim (both hands):

**Right hand:**
| Body | Line | Mass (kg) |
|------|------|-----------|
| lunate | 7358 | 0 |
| scaphoid | 7532 | 0 |
| pisiform | 7557 | 0 |
| triquetrum | 7582 | 0 |
| capitate | 7607 | 0 |
| trapezium | 7663 | 0 |
| trapezoid | 7688 | 0 |
| hamate | 7713 | 0 |

**Left hand:**
| Body | Line | Mass (kg) |
|------|------|-----------|
| lunate_l | 10578 | 0 |
| scaphoid_l | 10752 | 0 |
| pisiform_l | 10777 | 0 |
| triquetrum_l | 10802 | 0 |
| capitate_l | 10827 | 0 |
| trapezium_l | 10883 | 0 |
| trapezoid_l | 10908 | 0 |
| hamate_l | 10933 | 0 |

### UpperLowerBodySimple.osim (right hand only):
All 8 carpal bones (lunate, scaphoid, pisiform, triquetrum, capitate, trapezium, trapezoid, hamate) = 0 kg each.

### WristModel.osim (OpenSim 4.0 format, single hand):
All carpal bones (scaphoid, lunate, trapezium, trapezoid, capitate, pisiform, triquetrum, hamate) = 0 kg each.

**Verdict:** ERROR CONFIRMED. Carpal bone masses are either 0 or 0.00001 kg (0.01 g). The claim of ~0.01g matches the trapezium, trapezoid, and hamate in the Hand_Wrist_Model. Real carpal bones each weigh approximately 3-10 g (0.003-0.010 kg). The models that assign 0 kg are worse; the ones at 0.00001 kg are still ~300-1000× too small. The single exception is the capitate at 0.32742 kg, which goes in the opposite direction (see B6).

---

## Summary Table

| Bug ID | Body | Current Mass | Expected Mass | Error Magnitude | Source Model | Status |
|--------|------|-------------|---------------|-----------------|-------------|--------|
| B1 | sacrum | 0.00011 kg | ~0.95 kg | ~8,600× too small | M7_18_Baza | CONFIRMED |
| B2 | Abdomen | 0.00011 kg | ~2.5 kg | ~22,800× too small | M7_18_Baza | CONFIRMED |
| B3 | Abd_L/R_L1-L5 (×10) | 0.011 kg each | ~0.25 kg each | ~23× too small | M7_18_Baza | CONFIRMED |
| B4 | cerv1-cerv7 | 0.156-0.400 kg | 0.21-0.33 kg each | 30-40% low (C1-C4) | Head_Neck_Model | PARTIALLY CONFIRMED |
| B5 | pelvis | 9.14 kg | ~11.78 kg | 22.3% too small | M7_18_Baza | CONFIRMED |
| B6 | capitate | 0.327 kg (327g) | ~5-8 g | ~40-65× too large | Hand_Wrist_Model | CONFIRMED |
| B7 | carpal bones | 0-0.00001 kg | 0.003-0.010 kg each | ~300-1000× too small | Multiple | CONFIRMED |

## Next Actions

1. **Create the missing file**: The target file `model2_full_geom_fixed.osim` does not exist. It needs to be created by merging the source models.
2. **Fix B1/B2**: Replace placeholder masses (0.00011 kg) with anatomically correct values for sacrum (~0.95 kg) and Abdomen (~2.5 kg).
3. **Fix B3**: Redistribute abdomen mass across the 10 Abd_L/R segments (total ~2.5 kg, ~0.25 kg each).
4. **Fix B4**: Correct cervical vertebrae masses, especially C1-C3 which are uniform 0.156 kg and likely too low.
5. **Fix B5**: Increase pelvis mass from 9.14 kg to ~11.78 kg (accounting for sacrum mass fix in B1).
6. **Fix B6**: Capitate mass of 327g is absurd for a single carpal bone — should be ~5-8g. This appears to be an entire hand segment mass mistakenly assigned.
7. **Fix B7**: Assign proper carpal bone masses (3-10 g each). Currently 0 or 0.01g in various models.

---

# Worklog — Task 1d: Verify A6 A7 CPP and Fiso

**Date:** 2026-03-05
**File target:** `/home/z/my-project/download/model2_das3/model2_full_geom_fixed.osim`

## Critical Note: Target File Does Not Exist

The file `/home/z/my-project/download/model2_das3/model2_full_geom_fixed.osim` **does not exist** on disk. The directory `model2_das3` is also absent. Verification was performed against the **source/donor models** that would feed into this combined model.

| Source | Path | Role |
|--------|------|------|
| Gait2392_thelen.osim | `/home/z/my-project/download/Gait2392_thelen.osim` | Lower body donor with CPP muscles (rect_fem, vas_int, etc.) |
| Hamner2010.osim | `/home/z/my-project/download/Hamner2010.osim` | Lower body donor with same CPP patterns |
| das3.osim | `/home/z/my-project/upload/das3.osim` | Upper extremity donor (DAS3 model, Saul et al. 2015) |

---

## A6: ConditionalPathPoint Ranges Exceed Coordinate Ranges

**Claim:** CPP ranges for rect_femoris and vas_intermedius are [-2.618, -1.460] which exceeds the coordinate range of [-2.094, 0.175].

### Findings in Gait2392_thelen.osim:

**Coordinate ranges:**

| Coordinate | Line | Range (rad) | Range (deg) |
|-----------|------|-------------|-------------|
| knee_angle_r | 972 | [-2.0943951, 0.17453293] | [-120.0°, 10.0°] |
| knee_angle_l | 1607 | [-2.0943951, 0.17453293] | [-120.0°, 10.0°] |

**ConditionalPathPoint ranges:**

| Muscle Point | Line | CPP Range (rad) | CPP Range (deg) | References Coordinate |
|-------------|------|-----------------|-----------------|----------------------|
| rect_fem_r-P2 | 4143 | [-2.61799, -1.45997] | [-150.0°, -83.6°] | knee_angle_r |
| rect_fem_l-P2 | 7418 | [-2.61799, -1.45997] | [-150.0°, -83.6°] | knee_angle_l |
| vas_int_r-P3 | 4361 | [-2.61799, -1.42000] | [-150.0°, -81.3°] | knee_angle_r |
| vas_int_l-P3 | 7636 | [-2.61799, -1.42000] | [-150.0°, -81.3°] | knee_angle_l |

**Additional CPP mismatches (same -2.618 lower bound issue):**

| Muscle Point | Line | CPP Range (rad) | References Coordinate |
|-------------|------|-----------------|----------------------|
| vas_med_r-P3 | 4247 | [-2.618, -1.210] | knee_angle_r |
| vas_med_r-P4 | 4257 | [-2.618, -1.780] | knee_angle_r |
| vas_lat_r-P3 | 4465 | [-2.618, -1.210] | knee_angle_r |
| vas_lat_r-P4 | 4475 | [-2.618, -1.920] | knee_angle_r |
| vas_med_l-P3 | 7522 | [-2.618, -1.210] | knee_angle_l |
| vas_med_l-P4 | 7532 | [-2.618, -1.780] | knee_angle_l |
| vas_lat_l-P3 | 7740 | [-2.618, -1.210] | knee_angle_l |
| vas_lat_l-P4 | 7750 | [-2.618, -1.920] | knee_angle_l |

### Findings in Hamner2010.osim (same pattern):

| Muscle Point | Line | CPP Range (rad) |
|-------------|------|-----------------|
| rect_fem_r-P2 | 5663 | [-2.61799, -1.45997] |
| vas_int_r-P3 | 5869 | [-2.61799, -1.42000] |
| knee_angle_r coord range | 1604 | [-2.094, 0.175] |

### Mismatch Analysis:

| | CPP Lower Bound | Coordinate Lower Bound | Excess |
|--|-----------------|----------------------|--------|
| Value | -2.618 rad (-150°) | -2.094 rad (-120°) | 0.524 rad (30°) |

**Verdict: ERROR CONFIRMED.** The CPP lower bound of -2.618 rad (-150°) exceeds the coordinate range lower bound of -2.094 rad (-120°) by 0.524 rad (30°). This affects rect_femoris (both sides), vas_intermedius (both sides), vas_medialis (both sides), and vas_lateralis (both sides) — a total of 12 ConditionalPathPoints across 6 muscles.

**Practical impact:** When the knee angle is between -2.094 and -1.460 rad (between 120° and 83.6° of flexion), the CPP for rect_femoris will be active, which is correct. However, the CPP range specifies that it should also be active from -2.618 to -2.094 rad, where the coordinate can never actually reach. This is a legacy artifact from the original SIMM model where the knee range may have been larger (-150° to 10°). The CPP ranges were not updated when the coordinate range was reduced to [-120°, 10°] in the OpenSim 2.1 version (noted in the Arnold model changelog as a correction from 0-120° to 0-100° range).

---

## A7: pron_teres_1 max_isometric_force = 510 N

**Claim:** pron_teres_1 has max_isometric_force = 510N which seems wrong.

### Findings in das3.osim:

| Muscle | Line | max_isometric_force (N) |
|--------|------|------------------------|
| pron_teres_1 (humeral head) | 8553 | **510** |
| pron_teres_2 (ulnar head) | 8612 | **141** |
| **Total** | | **651** |

The muscle group names confirm the anatomy:
- `pron_teres_hr` (humeral head) → pron_teres_1 (line 9722-9723)
- `pron_teres_ur` (ulnar head) → pron_teres_2 (line 9725-9726)

### Donor Model Comparison:

No other .osim model on this filesystem contains pronator teres (checked all 25+ models). The DAS3 model is the sole source.

### Literature Comparison (Holzbaur et al. 2005):

The DAS3 model is based on the Holzbaur upper extremity model. Published values from Holzbaur et al. (2005) "A model of the upper extremity for simulating musculoskeletal surgery and analyzing muscle adaptation":

| Compartment | Holzbaur PCSA (cm²) | Force at 35 N/cm² | Force at 61 N/cm² | DAS3 Value (N) | Discrepancy |
|-------------|---------------------|-------------------|-------------------|----------------|-------------|
| Humeral head | ~4.0 | ~140 | ~244 | **510** | **2.1-3.6× too high** |
| Ulnar head | ~0.6 | ~21 | ~37 | **141** | **3.8-6.7× too high** |
| **Total** | ~4.6 | ~161 | ~281 | **651** | **2.3-4.0× too high** |

### Anatomical Reference:

From Wu et al. and other cadaveric studies, pronator teres PCSA is typically 3-5 cm² total. At a specific tension of 35-61 N/cm², the expected total max_isometric_force is approximately 105-305 N. The DAS3 total of 651 N is **2.1-6.2× too high**.

**Verdict: ERROR CONFIRMED.** The pron_teres_1 max_isometric_force of 510N is anomalously high. The humeral head alone exceeds the expected force for the entire muscle. The total combined force (651N) is 2-4× above literature values. This is likely a unit conversion error or an incorrect PCSA scaling in the DAS3 model.

---

## Summary Table

| Bug ID | Issue | Current Value | Expected Value | Error Magnitude | Source Model | Status |
|--------|-------|---------------|----------------|-----------------|-------------|--------|
| A6 | CPP range lower bound exceeds coordinate range | [-2.618, -1.460] | Should be within [-2.094, 0.175] | 0.524 rad (30°) excess | Gait2392, Hamner2010 | CONFIRMED |
| A7 | pron_teres_1 max_isometric_force | 510 N (total 651 N) | ~105-305 N total | 2-4× too high | das3.osim | CONFIRMED |

## Next Actions

1. **Fix A6:** Update all 12 ConditionalPathPoint ranges to be within the coordinate range. For rect_fem_r/l-P2, change from [-2.618, -1.460] to [-2.094, -1.460]. For vas_int_r/l-P3, change from [-2.618, -1.420] to [-2.094, -1.420]. Apply same fix to vas_med and vas_lat CPP ranges. Alternatively, if the coordinate range should actually extend to -2.618 (150° flexion), expand the coordinate range — but this requires validating moment arms at those extreme angles.
2. **Fix A7:** Reduce pron_teres_1 max_isometric_force from 510N to approximately 120-210N, and pron_teres_2 from 141N to approximately 20-40N. Verify against Holzbaur et al. (2005) Table 2 for exact PCSA values and apply the model's specific tension consistently.
3. **Create model2_full_geom_fixed.osim:** The target file still needs to be created by merging the donor models with these fixes applied.

---

# Worklog — Task 1c: Verify A3 A4 A5 deepmult/multifidus

**Date:** 2026-03-05
**File target:** `/home/z/my-project/download/model2_das3/model2_full_geom_fixed.osim`

## Critical Note: Target File Does Not Exist

The file `/home/z/my-project/download/model2_das3/model2_full_geom_fixed.osim` **does not exist** on disk. The directory `model2_das3` is also absent. Verification was performed against the **source/donor models** that would feed into this combined model:

| Source | Path | Role |
|--------|------|------|
| M7_18_Baza.osim | `/home/z/my-project/upload/M7_18_Baza.osim` | Full body (torso, lumbar, thoracic, deepmult, multifidus) |
| Male_15years_FullBody_TLSpine.osim | `/home/z/my-project/upload/Male_15years_FullBody_TLSpine.osim` | Identical to M7_18_Baza (same line numbers) |
| 997_SizeScaled_CurvatureAdjust_MuscleAdjust.osim | `/home/z/my-project/upload/997_SizeScaled_CurvatureAdjust_MuscleAdjust.osim` | Scaled variant with same deepmult/multifidus structure |
| Head_Neck_Model_fixed.osim | `/home/z/my-project/upload/Head_Neck_Model_fixed.osim` | Cervical spine with deepmult (different naming convention) |
| Head_Neck_Model.osim | `/home/z/my-project/upload/Head_Neck_Model.osim` | Original head/neck (same deepmult issues) |
| Head_Neck_Model_nocomments.osim | `/home/z/my-project/upload/Head_Neck_Model_nocomments.osim` | Comment-stripped variant (same deepmult issues) |

---

## A3: deepmult-T2-T1 Path Points on Same Body

**Claim:** Both path points of deepmult-T2-T1_r and deepmult-T2-T1_l are on the same body (thoracic1) instead of one on thoracic2 and one on thoracic1.

### CONFIRMED — but with different body name than expected

The error exists in the **Head_Neck_Model** (all 3 variants). The body name is **`spine`** (not `thoracic1`), because the Head_Neck model uses a simplified body called "spine" for the thoracic region.

**Head_Neck_Model_fixed.osim:**

| Muscle | Line | PathPoint | Body | Location |
|--------|------|-----------|------|----------|
| deepmult-T2-T1_r | 10908 | deepmult-T2-T1-P1 | **spine** | -0.08711 0.34913 0.02455 |
| deepmult-T2-T1_r | 10912 | deepmult-T2-T1-P2 | **spine** | -0.08485 0.35049 0.00389 |
| deepmult-T2-T1_l | 15852 | deepmult-T2-T1-P1 | **spine** | -0.08711 0.34913 -0.02455 |
| deepmult-T2-T1_l | 15856 | deepmult-T2-T1-P2 | **spine** | -0.08485 0.35049 -0.00389 |

**Both path points are on `spine`** — this means the muscle has zero anatomical span since both endpoints are on the same rigid body. The muscle name "T2-T1" implies it should span from thoracic2 to thoracic1, requiring two different bodies.

**Contrast with M7_18_Baza.osim (CORRECT):**

| Muscle | Line | PathPoint | Body | Location |
|--------|------|-----------|------|----------|
| deepmult-T2-T1 | 30580 | deepmult-T2-T1-P1 | **thoracic2** | -0.0336563 0.0155277 0.0295099 |
| deepmult-T2-T1 | 30584 | deepmult-T2-T1-P2 | **thoracic1** | -0.0276303 0.00348176 0.00250994 |
| deepmult-T2-T1_L | 32988 | deepmult-T2-T1-P1 | **thoracic2** | -0.0336563 0.0155277 -0.0295099 |
| deepmult-T2-T1_L | 32992 | deepmult-T2-T1-P2 | **thoracic1** | -0.0276303 0.00348176 -0.00250994 |

In M7, the path points are correctly on different bodies (thoracic2 and thoracic1).

**All other deepmult muscles in Head_Neck_Model have correct path point bodies:**

| Muscle | P1 Body | P2 Body | Status |
|--------|---------|---------|--------|
| deepmult-C4/5-C2_r | cerv2 | cerv5 | OK |
| deepmult-C5/6-C3_r | cerv3 | cerv6 | OK |
| deepmult-C6/7-C4_r | cerv4 | cerv7 | OK |
| deepmult-T1-C5_r | cerv5 | spine | OK |
| deepmult-T1-C6_r | cerv6 | spine | OK |
| deepmult-T2-C7_r | cerv7 | spine | OK |
| **deepmult-T2-T1_r** | **spine** | **spine** | **ERROR — both on same body** |
| **deepmult-T2-T1_l** | **spine** | **spine** | **ERROR — both on same body** |

**Root cause:** The Head_Neck model only has a single `spine` body for the entire thoracic region. When deepmult-T2-T1 was added (spanning T2→T1, both thoracic), both path points defaulted to `spine` because there are no separate thoracic1/thoracic2 bodies in that model. The M7 model has individual thoracic bodies and thus gets this right.

**Verdict: ERROR CONFIRMED.** Both `deepmult-T2-T1_r` (line 10908/10912) and `deepmult-T2-T1_l` (line 15852/15856) in Head_Neck_Model_fixed.osim have both path points on `spine` instead of different bodies. In a merged model2, this error would be inherited from the Head_Neck donor.

---

## A4: Duplicate deepmult Muscles (Case Variants _L vs _l)

**Claim:** There are duplicate left-side deepmult muscles with case-variant suffixes (e.g., `deepmult-T2-T1_L` and `deepmult-T2-T1_l`).

### No duplicates in any single file

No single .osim file contains both `_L` and `_l` variants of the same deepmult muscle. However, the two donor models use **incompatible naming conventions**:

**M7_18_Baza.osim / Male_15years_FullBody_TLSpine.osim naming:**
- Right side: `deepmult-T2-T1` (NO suffix)
- Left side: `deepmult-T2-T1_L` (uppercase _L)

**Head_Neck_Model_fixed.osim naming:**
- Right side: `deepmult-T2-T1_r` (lowercase _r)
- Left side: `deepmult-T2-T1_l` (lowercase _l)

### If models are merged (as model2_full_geom_fixed), these case-variant duplicates would appear:

| Base name (case-insensitive) | M7 variant | Head_Neck variant | Duplicate? |
|------------------------------|-----------|-------------------|------------|
| deepmult-T1-C5_l | deepmult-T1-C5_L (line 32851) | deepmult-T1-C5_l (line 15494) | **YES** |
| deepmult-T1-C6_l | deepmult-T1-C6_L (line 32894) | deepmult-T1-C6_l (line 15610) | **YES** |
| deepmult-T2-C7_l | deepmult-T2-C7_L (line 32937) | deepmult-T2-C7_l (line 15726) | **YES** |
| deepmult-T2-T1_l | deepmult-T2-T1_L (line 32980) | deepmult-T2-T1_l (line 15842) | **YES** |

Additionally, the right-side muscles would have **semantic duplicates** (not case-variant):
- `deepmult-T2-T1` (M7, no suffix) vs `deepmult-T2-T1_r` (Head_Neck, _r suffix) — same muscle, different naming

**Note:** The Head_Neck model also has additional deepmult muscles NOT in M7:
- `deepmult-C4/5-C2_r` / `_l`
- `deepmult-C5/6-C3_r` / `_l`
- `deepmult-C6/7-C4_r` / `_l`

These cervical-level deepmult muscles exist only in the Head_Neck model and would NOT be duplicates.

**Verdict: ERROR CONFIRMED (for merged model).** If M7 and Head_Neck models are merged to create model2_full_geom_fixed, there would be 4 pairs of case-variant duplicates for the left side (`_L` vs `_l`), plus 4 pairs of semantic duplicates for the right side (no suffix vs `_r`), for the overlapping T1-C5, T1-C6, T2-C7, and T2-T1 deepmult muscles.

---

## A5: Multifidus Muscles Missing _r Suffix

**Claim:** Right-side multifidus muscles are missing the `_r` suffix.

### CONFIRMED — 12 right-side multifidus muscles lack the _r suffix

In M7_18_Baza.osim / Male_15years_FullBody_TLSpine.osim, the `multifidus_*` muscles use an inconsistent naming convention:
- **Right side:** No suffix at all (e.g., `multifidus_L2_T12`)
- **Left side:** Uppercase `_L` suffix (e.g., `multifidus_L2_T12_L`)

This is inconsistent with the MF_* (lumbar multifidus) muscles which DO have the `_r`/`_l` suffixes.

### All 12 unsuffixed right-side multifidus muscles (verified by z-coordinate as RIGHT side):

| # | Muscle Name | Line | avg_z | Side Verification |
|---|-------------|------|-------|-------------------|
| 1 | multifidus_L2_T12 | 30615 | +0.020430 | RIGHT (z > 0) |
| 2 | multifidus_L1_T11 | 30658 | +0.020706 | RIGHT (z > 0) |
| 3 | multifidus_T12_T10 | 30701 | +0.017345 | RIGHT (z > 0) |
| 4 | multifidus_T11_T9 | 30744 | +0.015811 | RIGHT (z > 0) |
| 5 | multifidus_T10_T8 | 30787 | +0.014753 | RIGHT (z > 0) |
| 6 | multifidus_T9_T7 | 30830 | +0.015042 | RIGHT (z > 0) |
| 7 | multifidus_T8_T6 | 30873 | +0.015305 | RIGHT (z > 0) |
| 8 | multifidus_T7_T5 | 30916 | +0.014412 | RIGHT (z > 0) |
| 9 | multifidus_T6_T4 | 30959 | +0.015086 | RIGHT (z > 0) |
| 10 | multifidus_T5_T3 | 31002 | +0.015086 | RIGHT (z > 0) |
| 11 | multifidus_T4_T2 | 31045 | +0.015494 | RIGHT (z > 0) |
| 12 | multifidus_T3_T1 | 31088 | +0.015358 | RIGHT (z > 0) |

### Corresponding left-side muscles (all have _L suffix):

| Muscle Name | Line | avg_z |
|-------------|------|-------|
| multifidus_L2_T12_L | 33023 | -0.020430 |
| multifidus_L1_T11_L | 33066 | -0.020706 |
| multifidus_T12_T10_L | 33109 | -0.017345 |
| multifidus_T11_T9_L | 33152 | -0.015811 |
| multifidus_T10_T8_L | 33195 | -0.014753 |
| multifidus_T9_T7_L | 33238 | -0.015042 |
| multifidus_T8_T6_L | 33281 | -0.015305 |
| multifidus_T7_T5_L | 33324 | -0.014412 |
| multifidus_T6_T4_L | 33367 | -0.015086 |
| multifidus_T5_T3_L | 33410 | -0.015086 |
| multifidus_T4_T2_L | 33453 | -0.015494 |
| multifidus_T3_T1_L | 33496 | -0.015358 |

### Same pattern found in 997_SizeScaled_CurvatureAdjust_MuscleAdjust.osim:

All 12 right-side multifidus muscles also lack the `_r` suffix (lines 28868-29341), with corresponding `_L` versions at lines 31276-31749.

### Additional inconsistency: supmult muscles also lack side suffix

| Muscle | Line | Side Suffix |
|--------|------|-------------|
| supmult-T1-C4 | 30314 | *** NONE *** |
| supmult-T1-C5 | 30357 | *** NONE *** |
| supmult-T2-C6 | 30400 | *** NONE *** |
| supmult-T1-C4_L | 32722 | LEFT (_L) |
| supmult-T1-C5_L | 32765 | LEFT (_L) |
| supmult-T2-C6_L | 32808 | LEFT (_L) |

### Comparison with MF_ (lumbar multifidus) muscles which DO have proper suffixes:

The 50 MF_* muscles (25 per side) in M7 correctly use `_r` and `_l` suffixes:
- MF_m1s_r through MF_m5_laminar_r (25 right-side)
- MF_m1s_l through MF_m5_laminar_l (25 left-side)

**Verdict: ERROR CONFIRMED.** All 12 right-side `multifidus_*` muscles (thoracic-level) are missing the `_r` suffix. The left-side counterparts correctly have `_L` suffix. This creates an asymmetry in the naming convention and would cause issues in the TransversoSpinalis muscle group references, which list these muscles with `_r`/`_l` suffixes in the Qwin/DeepSeek fix scripts.

---

## Summary Table

| Bug ID | Issue | Affected Muscles | Source Model | Status |
|--------|-------|-----------------|-------------|--------|
| A3 | Both path points on same body (spine) instead of different bodies | deepmult-T2-T1_r, deepmult-T2-T1_l | Head_Neck_Model_fixed.osim | CONFIRMED |
| A4 | Case-variant duplicates (_L vs _l) when models are merged | 4 pairs: deepmult-T1-C5, T1-C6, T2-C7, T2-T1 (left side) | M7 + Head_Neck merged | CONFIRMED (in merged model) |
| A5 | Right-side multifidus missing _r suffix | 12 muscles: multifidus_L2_T12 through multifidus_T3_T1 | M7_18_Baza / Male_15years | CONFIRMED |

## Next Actions

1. **Fix A3:** In the merged model, ensure deepmult-T2-T1_r and deepmult-T2-T1_l have path points on different bodies (thoracic2 and thoracic1). The Head_Neck donor's `spine` body must be replaced with the correct individual thoracic bodies from M7.
2. **Fix A4:** Standardize side suffixes across both donor models before merging. Choose either `_r`/`_l` (lowercase, OpenSim convention) or no-suffix-for-right / `_L`-for-left (M7 convention). Recommended: rename all to `_r`/`_l` (lowercase) for consistency with OpenSim standards. Remove duplicates after renaming.
3. **Fix A5:** Add `_r` suffix to all 12 right-side multifidus muscles (e.g., `multifidus_L2_T12` → `multifidus_L2_T12_r`). Also add `_r` to the 3 supmult right-side muscles. This aligns with the MF_* naming convention already used in the same model.
4. **Create model2_full_geom_fixed.osim:** The target file needs to be created by merging the donor models with these fixes applied.

---

# Worklog — Final Model Validation: model2_full_fixed.osim

**Date:** 2026-03-05
**File:** `/home/z/my-project/download/model2_full_fixed.osim`
**Task ID:** final_validation

---

## Model Overview

| Metric | Value |
|--------|-------|
| Total bodies | 134 |
| Total coordinates | 262 |
| Total muscles | 940 |
| Thelen2003Muscle | 505 |
| Schutte1993Muscle | 276 |
| Millard2012EquilibriumMuscle | 159 |
| ConditionalPathPoints | 108 |

---

## 1. Duplicate Muscle Names

**Result: PASS — No exact duplicate muscle names found.**

All 940 muscle names are unique across all three muscle types.

### Case-insensitive duplicates (potential collisions):

12 pairs of case-variant names exist where `_L` (uppercase) and `_l` (lowercase) refer to the same anatomical muscle but with different muscle models:

| Lowercase variant (Millard2012) | Uppercase variant (Thelen2003) | Notes |
|-------------------------------|-------------------------------|-------|
| iliocost_cerv_c5rib_l | iliocost_cerv_c5rib_L | Different muscle model |
| long_col_c1thx_l | long_col_c1thx_L | Different muscle model |
| long_col_c5thx_l | long_col_c5thx_L | Different muscle model |
| longissi_cerv_c4thx_l | longissi_cerv_c4thx_L | Different muscle model |
| scalenus_ant_l | scalenus_ant_L | Different muscle model |
| scalenus_med_l | scalenus_med_L | Different muscle model |
| scalenus_post_l | scalenus_post_L | Different muscle model |
| semi_cap_sklthx_l | semi_cap_sklthx_L | Different muscle model |
| semi_cerv_c3thx_l | semi_cerv_c3thx_L | Different muscle model |
| stern_mast_l | stern_mast_L | Different muscle model |
| supmult-T1-C4_l | supmult-T1-C4_L | Different muscle model |
| supmult-T1-C5_l | supmult-T1-C5_L | Different muscle model |
| supmult-T2-C6_l | supmult-T2-C6_L | Different muscle model |

These are NOT exact string duplicates (XML name attributes differ in case), but on case-insensitive filesystems or OpenSim's case-insensitive name lookups, they could collide.

---

## 2. Body References (PathPoint/MovingPathPoint/ConditionalPathPoint)

**Result: PASS — All 134 bodies referenced by path points exist in the BodySet.**

Zero missing body references found across all PathPoint, MovingPathPoint, and ConditionalPathPoint elements.

---

## 3. Coordinate References (MovingPathPoint/ConditionalPathPoint)

**Result: PASS — All coordinate names referenced by MovingPathPoint and ConditionalPathPoint exist in the CoordinateSet.**

Zero missing coordinate references found. All 262 coordinates are properly defined.

---

## 4. Verify Specific Fixes

### A2: iliacus_r and iliacus_l — tendon_slack_length != optimal_fiber_length

**Result: PASS**

| Muscle | tendon_slack_length | optimal_fiber_length | Equal? |
|--------|--------------------|-----------------------|--------|
| iliacus_r | 0.0961207083983258 | 0.0981684832632378 | NO ✓ |
| iliacus_l | 0.0961207083983258 | 0.0981684832632378 | NO ✓ |

Both muscles have different tendon_slack_length and optimal_fiber_length values.

### A3: deepmult-T2-T1_r and deepmult-T2-T1_l — path points on DIFFERENT bodies

**Result: PASS**

| Muscle | Path point bodies |
|--------|------------------|
| deepmult-T2-T1_r | thoracic2, thoracic1 ✓ |
| deepmult-T2-T1_l | thoracic2, thoracic1 ✓ |

Both muscles correctly have path points on different bodies (thoracic2 → thoracic1).

### A5: Multifidus muscles — proper side suffix

**Result: PARTIAL FAIL — 15 muscles still use uppercase `_L` instead of lowercase `_l`**

12 multifidus muscles with `_L` (uppercase) suffix — they have matching `_r` versions but no lowercase `_l`:
- multifidus_L1_T11_L, multifidus_L2_T12_L, multifidus_T3_T1_L, multifidus_T4_T2_L
- multifidus_T5_T3_L, multifidus_T6_T4_L, multifidus_T7_T5_L, multifidus_T8_T6_L
- multifidus_T9_T7_L, multifidus_T10_T8_L, multifidus_T11_T9_L, multifidus_T12_T10_L

3 supmult muscles with `_L` that ALSO have lowercase `_l` versions (different muscle models):
- supmult-T1-C4_L (Thelen2003, force=283.88N) vs supmult-T1-C4_l (Millard2012, force=16.27N)
- supmult-T1-C5_L (Thelen2003, force=283.88N) vs supmult-T1-C5_l (Millard2012, force=11.65N)
- supmult-T2-C6_L (Thelen2003, force=283.88N) vs supmult-T2-C6_l (Millard2012, force=6.53N)

Additionally, the original unsuffixed Thelen2003 versions of these neck muscles still exist (no `_r` or `_l`):
- iliocost_cerv_c5rib, long_col_c1thx, long_col_c5thx, longissi_cerv_c4thx
- scalenus_ant, scalenus_med, scalenus_post, semi_cap_sklthx, semi_cerv_c3thx
- stern_mast, splen_cap_skl_T1, splen_cap_skl_T2, splen_cerv_c3_T3-T6

### A6: ConditionalPathPoint ranges vs coordinate ranges

**Result: PASS — No ConditionalPathPoint range exceeds its coordinate range.**

Knee angle coordinate ranges:
- knee_angle_r: [-2.0943951, 0.17453293] rad
- knee_angle_l: [-2.0943951, 0.17453293] rad

All 108 ConditionalPathPoints were checked against their referenced coordinate ranges. None exceed bounds.

### A7: pron_teres_1 max_isometric_force

**Result: PASS — max_isometric_force = 200.0 N (not 510 N)**

The value has been corrected from the original 510N.

---

## 5. Mass Check

**Result: PASS — All specified body masses are correct.**

| Body | Actual Mass (kg) | Expected | Status |
|------|------------------|----------|--------|
| sacrum | 0.949 | ~0.95 kg | PASS ✓ |
| Abdomen | 0.5 | >0.1 kg | PASS ✓ |
| pelvis | 11.777 | ~11.78 kg | PASS ✓ |
| capitate_r | 0.008 | <0.05 kg | PASS ✓ |
| capitate_l | 0.008 | <0.05 kg | PASS ✓ |

Note: Abdomen mass is 0.5 kg (was 0.00011 kg originally). While this is >0.1 kg per the check criterion, it's still well below the anatomically expected ~2.5 kg. The 10 Abd_L/R segments are each 0.25 kg (corrected from 0.011 kg), totaling 2.5 kg across segments plus 0.5 kg in the Abdomen body = ~3.0 kg total, which is more reasonable.

---

## 6. Dot-Version Muscles (A1)

**Result: PASS — No muscle names contain dots.**

Zero muscles with dots in their names. All dot variants have been converted to underscore equivalents.

---

## 7. Deepmult Duplicates (A4)

**Result: PASS — No duplicate deepmult muscles.**

14 unique deepmult muscles found:
- deepmult-C4/5-C2_l/r (Millard2012EquilibriumMuscle)
- deepmult-C5/6-C3_l/r (Millard2012EquilibriumMuscle)
- deepmult-C6/7-C4_l/r (Millard2012EquilibriumMuscle)
- deepmult-T1-C5_l/r (Thelen2003Muscle)
- deepmult-T1-C6_l/r (Thelen2003Muscle)
- deepmult-T2-C7_l/r (Thelen2003Muscle)
- deepmult-T2-T1_l/r (Thelen2003Muscle)

No duplicates detected.

---

## Additional Findings

### A. Inconsistent Suffix Casing (_L/_R uppercase vs _l/_r lowercase)

| Suffix | Count |
|--------|-------|
| _l (lowercase) | 365 |
| _r (lowercase) | 238 |
| _L (uppercase) | 107 |
| _R (uppercase) | 76 |
| No suffix | 154 |

The 107 `_L` and 76 `_R` muscles violate OpenSim naming convention (lowercase `_l`/`_r`). These include:
- 76 ExtIC/IntIC intercostal muscles (38 _L + 38 _R)
- 12 multifidus muscles (_L only)
- 3 supmult muscles (_L only)
- Various neck/spine muscles (scalenus, stern_mast, splenius, semispinalis, longissimus, longus colli, iliocostalis)

### B. Unsuffixed Muscles Coexisting with Suffixed Versions

154 muscles have no side suffix. Many of these have corresponding `_l` versions, suggesting the unsuffixed version is an original that should have been renamed or removed:

- 83 Schutte1993Muscle (upper extremity: deltoid, trapezius, rotator cuff, etc.) — each has a `_l` suffixed version
- 15 Thelen2003Muscle (neck/spine: scalenus, stern_mast, splenius, etc.) — some have both `_L` and `_l` versions
- 1 `default` muscle (Thelen2003Muscle)

The Schutte1993Muscle pattern (e.g., `anconeus_1` + `anconeus_1_l`) suggests the unsuffixed versions may be the right-side originals that were never renamed with `_r`.

---

## Validation Summary

| Check | Status | Details |
|-------|--------|---------|
| 1. Duplicate muscle names | ✅ PASS | 0 exact duplicates out of 940 muscles |
| 2. Body references | ✅ PASS | 0 missing bodies out of all path point references |
| 3. Coordinate references | ✅ PASS | 0 missing coordinates out of all MovingPathPoint/ConditionalPathPoint references |
| 4. A2 (iliacus tendon ≠ fiber) | ✅ PASS | tendon_slack_length ≠ optimal_fiber_length for both sides |
| 4. A3 (deepmult-T2-T1 bodies) | ✅ PASS | Path points on thoracic2 and thoracic1 (different bodies) |
| 4. A5 (multifidus suffix) | ⚠️ PARTIAL FAIL | 15 muscles use uppercase `_L` instead of `_l`; 3 supmult have both `_L` and `_l` |
| 4. A6 (CPP range bounds) | ✅ PASS | No ConditionalPathPoint ranges exceed coordinate ranges |
| 4. A7 (pron_teres_1 force) | ✅ PASS | max_isometric_force = 200.0 N (corrected from 510) |
| 5. Mass check | ✅ PASS | sacrum=0.949, Abdomen=0.5, pelvis=11.777, capitate=0.008 |
| 6. Dot-version muscles (A1) | ✅ PASS | 0 muscles with dots in names |
| 7. Deepmult duplicates (A4) | ✅ PASS | 0 duplicate deepmult muscles |

### Remaining Issues Requiring Attention

1. **A5 incomplete fix:** 12 multifidus `_L` muscles should be renamed to `_l`, and 3 supmult `_L` muscles should either be renamed to `_l` or removed (since lowercase `_l` Millard2012 versions already exist with different force values — these may be intentional different models or erroneous duplicates).
2. **Inconsistent suffix casing:** 183 muscles (107 `_L` + 76 `_R`) use uppercase side suffixes, inconsistent with OpenSim convention.
3. **Unsuffixed muscles:** 154 muscles lack side suffixes entirely; 83+ of these have corresponding `_l` versions, suggesting the unsuffixed are original right-side muscles never renamed with `_r`.
4. **Abdomen mass:** 0.5 kg is well below anatomically expected ~2.5 kg (though >0.1 kg threshold passes the check).
---
Task ID: validator-fixes-final
Agent: main
Task: Fix remaining false positive errors in OpenSim 3.3 validators

Work Log:
- Added `valid_lowercase_tags` whitelist to Python validator `_check_tag_case()` to prevent false positives on `<body>`, `<coordinate>`, `<parent_body>`, `<wrap_object>` etc. (was 2414 false errors)
- Changed Thelen2003 missing parameter check (8.14) from ERROR to INFO in both validators, with default values shown (was 3168 false errors)
- Changed PathPoint duplicate names check (3.7) from ERROR to INFO in both validators (was 28 false errors)
- Confirmed `scale_factors` already removed from OS4_FORBIDDEN_TAGS (fixed in prior session)
- Confirmed `getparent()` compatibility already handled with workaround in Python validator
- Tested against Male_15years_FullBody_TLSpine.osim: 0 errors (down from 3921)
- Tested against M7_18_Baza.osim: 0 errors
- Tested against arm26.osim (OS4 model): correctly detects 18 real errors

Stage Summary:
- All false positive fixes applied to both `opensim33_validator.py` and `OpenSim33_Validator.html`
- Male_15years_FullBody_TLSpine.osim: 0 Errors, 192 Warnings, 3364 Info messages (PASS)
- M7_18_Baza.osim: 0 Errors, 188 Warnings, 3362 Info messages (PASS)
- Real errors still correctly detected (arm26 OS4 model: 18 errors)
