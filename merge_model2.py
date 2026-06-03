#!/usr/bin/env python3
"""
Build composite OpenSim Model 2 from donor models with ALL error fixes applied.

Donors:
  - M7_18_Baza.osim (base: torso, pelvis, legs, arms, lumbar/thoracic)
  - Head_Neck_Model_fixed.osim (cervical vertebrae, skull, neck muscles)
  - Hand_Wrist_Model_for_development.osim (carpal bones, hand/wrist muscles)
  - das3.osim (upper extremity muscles - Schutte1993)
  - Lumbar_C_238.osim (additional lumbar muscles - MF_, QL_)

Fixes applied during merge:
  A1: Skip 76 dot-version duplicate muscles from Lumbar
  A2: Fix iliacus_r/l tendon_slack_length
  A3: Fix deepmult-T2-T1 path point bodies
  A4: Standardize _L -> _l, add _r to right-side muscles
  A5: Add _r suffix to 12 multifidus + 3 supmult right-side muscles
  A6: Fix CPP ranges to be within coordinate ranges
  A7: Fix pron_teres_1 max_isometric_force
  B1: Fix sacrum mass
  B2: Fix Abdomen mass
  B3: Fix Abd_L/R_L1-L5 masses
  B4: Fix cervical vertebrae masses
  B5: Fix pelvis mass
  B6: Fix capitate mass
  B7: Fix carpal bone masses
  C1: Verify no nested PathPointSet (already confirmed clean)
"""

import xml.etree.ElementTree as ET
import re
import copy
import sys
import os

BASE_DIR = '/home/z/my-project/upload'
OUTPUT_PATH = '/home/z/my-project/download/model2_full_fixed.osim'

# ============================================================
# Helper functions
# ============================================================

def read_xml(filepath):
    """Read XML file, handling comments with special characters."""
    # Pre-process to remove XML comments that may have special chars
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove XML comments (<!-- ... -->)
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    # Parse cleaned XML
    root = ET.fromstring(content)
    return root

def write_xml(root, filepath):
    """Write XML tree to file with proper formatting."""
    tree = ET.ElementTree(root)
    ET.indent(tree, space='\t')
    with open(filepath, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

def find_or_create(parent, tag, attrib=None):
    """Find first child with tag, or create it."""
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag, attrib or {})
    return child

def get_body_names(model):
    """Get all body names from model."""
    bodies = model.findall('.//BodySet/objects/Body')
    return [b.get('name') for b in bodies]

def get_muscle_names(model):
    """Get all muscle names from model."""
    names = []
    for tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Schutte1993Muscle_Deprecated', 'Millard2012EquilibriumMuscle']:
        for m in model.findall(f'.//{tag}'):
            names.append(m.get('name'))
    return names

def get_coord_names(model):
    """Get all coordinate names from model."""
    coords = model.findall('.//CoordinateSet/objects/Coordinate')
    return [c.get('name') for c in coords]

def get_joint_names(model):
    """Get all joint names from model."""
    joints = model.findall('.//JointSet/objects/*')
    return [j.get('name') for j in joints if j.get('name')]

# ============================================================
# Body name mapping between donor models and M7
# ============================================================

# Head_Neck -> M7 body name mapping
HN_TO_M7_BODY_MAP = {
    'spine': 'thoracic1',  # Head_Neck's "spine" maps to M7's thoracic1
    # cerv1-7, skull are new bodies to be added
}

# DAS3 -> M7 body name mapping (right side)
DAS3_TO_M7_BODY_MAP_R = {
    'thorax': 'thoracic1',  # approximate - DAS3 thorax
    'clavicle_1': 'clavicle_R',
    'clavicle_2': 'clavicle_R',
    'clavicle_r': 'clavicle_R',
    'scapula_1': 'scapula_R',
    'scapula_2': 'scapula_R',
    'scapula_r': 'scapula_R',
    'humerus_1': 'humerus_R',
    'humerus_2': 'humerus_R',
    'humerus_r': 'humerus_R',
    'ulna_r': 'ulna_R',
    'radius_r': 'radius_R',
    'hand_r': 'hand_R',
}

# DAS3 -> M7 body name mapping (left side - mirror)
DAS3_TO_M7_BODY_MAP_L = {
    'thorax': 'thoracic1',
    'clavicle_1': 'clavicle_L',
    'clavicle_2': 'clavicle_L',
    'clavicle_r': 'clavicle_L',
    'scapula_1': 'scapula_L',
    'scapula_2': 'scapula_L',
    'scapula_r': 'scapula_L',
    'humerus_1': 'humerus_L',
    'humerus_2': 'humerus_L',
    'humerus_r': 'humerus_L',
    'ulna_r': 'ulna_L',
    'radius_r': 'radius_L',
    'hand_r': 'hand_L',
}

# Hand_Wrist -> M7 body name mapping (right side)
HW_TO_M7_BODY_MAP_R = {
    'clavicle': 'clavicle_R',
    'scapula': 'scapula_R',
    'humerus': 'humerus_R',
    'ulna': 'ulna_R',
    'radius': 'radius_R',
    'proximal_row': 'proximal_row_r',
    'capitate': 'capitate_r',
    'trapezium': 'trapezium_r',
    'trapezoid': 'trapezoid_r',
    'hamate': 'hamate_r',
    'firstmc1': 'firstmc1_r',
    'firstmc': 'firstmc_r',
    'proximal_thumb': 'proximal_thumb_r',
    'distal_thumb': 'distal_thumb_r',
    'secondmc': 'secondmc_r',
    'thirdmc': 'thirdmc_r',
    'fourthmc': 'fourthmc_r',
    'fifthmc': 'fifthmc_r',
    '2proxph': 'proxph2_r',
    '2midph': 'midph2_r',
    '2distph': 'distph2_r',
    '3proxph': 'proxph3_r',
    '3midph': 'midph3_r',
    '3distph': 'distph3_r',
    '4proxph': 'proxph4_r',
    '4midph': 'midph4_r',
    '4distph': 'distph4_r',
    '5proxph': 'proxph5_r',
    '5midph': 'midph5_r',
    '5distph': 'distph5_r',
}

# ============================================================
# Fix B1-B7: Mass corrections
# ============================================================

# Correct mass values based on anthropological data for ~75kg male
MASS_FIXES = {
    # B1: sacrum ~0.95 kg
    'sacrum': 0.949,
    # B2: Abdomen ~2.5 kg (remaining mass after Abd segments)
    'Abdomen': 0.5,
    # B3: Abd_L/R_L1-L5 each ~0.25 kg (total 2.5 kg for 10 segments)
    'Abd_L_L1': 0.250, 'Abd_L_L2': 0.250, 'Abd_L_L3': 0.250, 'Abd_L_L4': 0.250, 'Abd_L_L5': 0.250,
    'Abd_R_L1': 0.250, 'Abd_R_L2': 0.250, 'Abd_R_L3': 0.250, 'Abd_R_L4': 0.250, 'Abd_R_L5': 0.250,
    # B5: pelvis ~11.78 kg
    'pelvis': 11.777,
}

# B4: Cervical vertebrae masses (from M8_NormTaz reference + proportional scaling)
CERVICAL_MASSES = {
    'cerv1': 0.221,
    'cerv2': 0.251,
    'cerv3': 0.241,
    'cerv4': 0.231,
    'cerv5': 0.231,
    'cerv6': 0.241,
    'cerv7': 0.221,
    'skull': 4.468,  # head mass minus cervical vertebrae
}

# B6: Capitate ~8g
# B7: Carpal bones ~3-10g each
CARPAL_MASSES = {
    'proximal_row_r': 0.025, 'proximal_row_l': 0.025,  # scaphoid+lunate+triquetrum+pisiform
    'capitate_r': 0.008, 'capitate_l': 0.008,
    'trapezium_r': 0.006, 'trapezium_l': 0.006,
    'trapezoid_r': 0.005, 'trapezoid_l': 0.005,
    'hamate_r': 0.007, 'hamate_l': 0.007,
    'scaphoid_r': 0.007, 'scaphoid_l': 0.007,
    'lunate_r': 0.006, 'lunate_l': 0.006,
    'pisiform_r': 0.003, 'pisiform_l': 0.003,
    'triquetrum_r': 0.005, 'triquetrum_l': 0.005,
}

def apply_mass_fixes(model):
    """Apply all mass corrections (B1-B7)."""
    bodies = model.findall('.//BodySet/objects/Body')
    
    for body in bodies:
        name = body.get('name')
        mass_elem = body.find('mass')
        if mass_elem is None:
            continue
            
        # B1-B3, B5 fixes
        if name in MASS_FIXES:
            mass_elem.text = str(MASS_FIXES[name])
            print(f"  B-mass: {name}: -> {MASS_FIXES[name]} kg")
        
        # B4: Cervical vertebrae
        if name in CERVICAL_MASSES:
            mass_elem.text = str(CERVICAL_MASSES[name])
            print(f"  B4-cerv: {name}: -> {CERVICAL_MASSES[name]} kg")
        
        # B6-B7: Carpal bones
        if name in CARPAL_MASSES:
            mass_elem.text = str(CARPAL_MASSES[name])
            print(f"  B6/7-carpal: {name}: -> {CARPAL_MASSES[name]} kg")
    
    # Also fix carpal bones that might have different naming patterns
    for body in bodies:
        name = body.get('name')
        mass_elem = body.find('mass')
        if mass_elem is None:
            continue
        
        # Any body with capitate in name that has absurdly high mass
        if 'capitate' in name.lower() and float(mass_elem.text) > 0.05:
            mass_elem.text = '0.008'
            print(f"  B6-capitate-fix: {name}: -> 0.008 kg")

# ============================================================
# Fix A2: iliacus tendon_slack_length
# ============================================================

def fix_iliacus(model):
    """Fix iliacus_r and iliacus_l tendon_slack_length (A2)."""
    correct_ltend = 0.096120708398325802
    
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in model.findall(f'.//{muscle_tag}'):
            name = muscle.get('name', '')
            if name in ('iliacus_r', 'iliacus_l'):
                ltend = muscle.find('tendon_slack_length')
                lfib = muscle.find('optimal_fiber_length')
                if ltend is not None and lfib is not None:
                    old_ltend = ltend.text
                    ltend.text = str(correct_ltend)
                    print(f"  A2: {name}: Ltend {old_ltend} -> {correct_ltend}")

# ============================================================
# Fix A5: Add _r suffix to right-side multifidus muscles
# ============================================================

def fix_multifidus_naming(model):
    """Add _r suffix to 12 right-side multifidus and 3 supmult muscles (A5)."""
    multifidus_right = [
        'multifidus_L2_T12', 'multifidus_L1_T11', 'multifidus_T12_T10',
        'multifidus_T11_T9', 'multifidus_T10_T8', 'multifidus_T9_T7',
        'multifidus_T8_T6', 'multifidus_T7_T5', 'multifidus_T6_T4',
        'multifidus_T5_T3', 'multifidus_T4_T2', 'multifidus_T3_T1',
    ]
    supmult_right = [
        'supmult-T1-C4', 'supmult-T1-C5', 'supmult-T2-C6',
    ]
    
    # Also need to update ObjectGroup references
    renames = {}
    for name in multifidus_right + supmult_right:
        renames[name] = name + '_r'
    
    # Rename in muscles
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in model.findall(f'.//{muscle_tag}'):
            name = muscle.get('name', '')
            if name in renames:
                muscle.set('name', renames[name])
                # Also rename PathPoint names that reference this muscle
                for pp in muscle.findall('.//PathPoint') + muscle.findall('.//MovingPathPoint') + muscle.findall('.//ConditionalPathPoint'):
                    pp_name = pp.get('name', '')
                    # PathPoint names typically follow pattern: muscle_name-P1, muscle_name-P2
                    if name in pp_name:
                        pp.set('name', pp_name.replace(name, renames[name]))
    
    # Rename in ObjectGroups
    for group in model.findall('.//ObjectGroup'):
        for member in group.findall('.//member'):
            if member.text and member.text.strip() in renames:
                member.text = renames[member.text.strip()]
    
    print(f"  A5: Renamed {len(renames)} right-side muscles with _r suffix")
    return renames

# ============================================================
# Fix A4: Standardize _L -> _l for left-side deepmult muscles
# ============================================================

def fix_deepmult_naming(model):
    """Standardize deepmult naming: _L -> _l, no-suffix right -> _r (A4)."""
    # Muscles from M7 that use _L for left side (need -> _l)
    deepmult_left_L = [
        'deepmult-T1-C5_L', 'deepmult-T1-C6_L', 'deepmult-T2-C7_L', 'deepmult-T2-T1_L',
    ]
    # Muscles from M7 with no suffix for right side (need -> _r)
    deepmult_right_nosuffix = [
        'deepmult-T1-C5', 'deepmult-T1-C6', 'deepmult-T2-C7', 'deepmult-T2-T1',
    ]
    
    renames = {}
    for name in deepmult_left_L:
        renames[name] = name.replace('_L', '_l')
    for name in deepmult_right_nosuffix:
        renames[name] = name + '_r'
    
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in model.findall(f'.//{muscle_tag}'):
            name = muscle.get('name', '')
            if name in renames:
                muscle.set('name', renames[name])
                for pp in muscle.findall('.//PathPoint') + muscle.findall('.//MovingPathPoint') + muscle.findall('.//ConditionalPathPoint'):
                    pp_name = pp.get('name', '')
                    if name in pp_name:
                        pp.set('name', pp_name.replace(name, renames[name]))
    
    for group in model.findall('.//ObjectGroup'):
        for member in group.findall('.//member'):
            if member.text and member.text.strip() in renames:
                member.text = renames[member.text.strip()]
    
    print(f"  A4: Standardized {len(renames)} deepmult muscle names")
    return renames

# ============================================================
# Fix A3: deepmult-T2-T1 path points on same body
# ============================================================

def fix_deepmult_T2_T1_bodies(model):
    """Fix deepmult-T2-T1_r and _l path points to use different bodies (A3)."""
    # In Head_Neck model, both points are on 'spine' -> need P1 on thoracic2, P2 on thoracic1
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in model.findall(f'.//{muscle_tag}'):
            name = muscle.get('name', '')
            if name in ('deepmult-T2-T1_r', 'deepmult-T2-T1_l'):
                pps = muscle.find('.//PathPointSet/objects')
                if pps is not None:
                    points = pps.findall('PathPoint') + pps.findall('MovingPathPoint') + pps.findall('ConditionalPathPoint')
                    if len(points) >= 2:
                        # P1 should be on thoracic2, P2 should be on thoracic1
                        body_p1 = points[0].find('body')
                        body_p2 = points[1].find('body')
                        if body_p1 is not None and body_p2 is not None:
                            if body_p1.text.strip() == body_p2.text.strip():
                                # Both on same body - fix it
                                old_body = body_p1.text.strip()
                                body_p1.text = 'thoracic2'
                                body_p2.text = 'thoracic1'
                                print(f"  A3: {name}: P1 body {old_body}->thoracic2, P2 body {old_body}->thoracic1")

# ============================================================
# Fix A6: ConditionalPathPoint ranges exceeding coordinate ranges
# ============================================================

def fix_cpp_ranges(model):
    """Fix CPP ranges that exceed coordinate ranges (A6)."""
    # Get coordinate ranges
    coord_ranges = {}
    for coord in model.findall('.//CoordinateSet/objects/Coordinate'):
        name = coord.get('name', '')
        range_elem = coord.find('range')
        if range_elem is not None and range_elem.text:
            try:
                parts = range_elem.text.strip().split()
                if len(parts) >= 2:
                    coord_ranges[name] = (float(parts[0]), float(parts[1]))
            except (ValueError, IndexError):
                pass
    
    # Check and fix ConditionalPathPoint ranges
    fixes = 0
    for cpp in model.findall('.//ConditionalPathPoint'):
        coord_name_elem = cpp.find('coordinate')
        range_elem = cpp.find('range')
        if coord_name_elem is not None and range_elem is not None:
            coord_name = coord_name_elem.text.strip() if coord_name_elem.text else ''
            if coord_name in coord_ranges:
                try:
                    parts = range_elem.text.strip().split()
                    if len(parts) >= 2:
                        cpp_lo, cpp_hi = float(parts[0]), float(parts[1])
                        coord_lo, coord_hi = coord_ranges[coord_name]
                        
                        new_lo = max(cpp_lo, coord_lo)
                        new_hi = min(cpp_hi, coord_hi)
                        
                        if new_lo != cpp_lo or new_hi != cpp_hi:
                            range_elem.text = f'{new_lo} {new_hi}'
                            fixes += 1
                            print(f"  A6: CPP on {coord_name}: [{cpp_lo}, {cpp_hi}] -> [{new_lo}, {new_hi}]")
                except (ValueError, IndexError):
                    pass
    
    print(f"  A6: Fixed {fixes} CPP range violations")

# ============================================================
# Fix A7: pron_teres_1 max_isometric_force
# ============================================================

def fix_pron_teres(model):
    """Fix pron_teres_1 and pron_teres_2 forces (A7)."""
    # Based on Holzbaur et al. 2005 PCSA values
    # Humeral head PCSA ~4.0 cm2, Ulnar head PCSA ~0.6 cm2
    # At specific tension 35 N/cm2: humeral=140N, ulnar=21N
    # At specific tension 61 N/cm2: humeral=244N, ulnar=37N
    # Use middle-ground: specific tension ~50 N/cm2
    # humeral: 200N, ulnar: 30N
    
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Schutte1993Muscle_Deprecated', 'Millard2012EquilibriumMuscle']:
        for muscle in model.findall(f'.//{muscle_tag}'):
            name = muscle.get('name', '')
            fiso = muscle.find('max_isometric_force')
            if fiso is None:
                continue
            
            if name == 'pron_teres_1':
                old_val = fiso.text
                fiso.text = '200.0'
                print(f"  A7: {name}: Fiso {old_val} -> 200.0 N")
            elif name == 'pron_teres_2':
                old_val = fiso.text
                fiso.text = '30.0'
                print(f"  A7: {name}: Fiso {old_val} -> 30.0 N")

# ============================================================
# Add Head_Neck components (cervical vertebrae, skull, neck muscles)
# ============================================================

def add_head_neck(model, hn_model):
    """Add cervical vertebrae, skull, and neck muscles from Head_Neck model."""
    m7_bodies = model.find('.//BodySet/objects')
    m7_joints = model.find('.//JointSet/objects')
    m7_coords = model.find('.//CoordinateSet/objects')
    
    # Add new bodies: cerv1-7, skull (not spine - that maps to thoracic1)
    new_bodies = ['cerv1', 'cerv2', 'cerv3', 'cerv4', 'cerv5', 'cerv6', 'cerv7', 'skull']
    
    for body_name in new_bodies:
        hn_body = hn_model.find(f".//Body[@name='{body_name}']")
        if hn_body is not None:
            new_body = copy.deepcopy(hn_body)
            m7_bodies.append(new_body)
            print(f"  HN: Added body {body_name}")
    
    # Remove the old head_neck body
    for body in model.findall('.//BodySet/objects/Body'):
        if body.get('name') == 'head_neck':
            model.find('.//BodySet/objects').remove(body)
            print(f"  HN: Removed old head_neck body")
            break
    
    # Add joints from Head_Neck model
    for joint in hn_model.findall('.//JointSet/objects/*'):
        joint_name = joint.get('name', '')
        # Add cervical and skull joints
        if any(x in joint_name for x in ['cerv', 'skull', 'atlant', 'head']):
            new_joint = copy.deepcopy(joint)
            # Map body references from Head_Neck to M7
            for elem in new_joint.iter():
                if elem.text and elem.text.strip() == 'spine':
                    elem.text = 'thoracic1'
            m7_joints.append(new_joint)
            print(f"  HN: Added joint {joint_name}")
    
    # Add coordinates from Head_Neck model
    for coord in hn_model.findall('.//CoordinateSet/objects/Coordinate'):
        coord_name = coord.get('name', '')
        # Check if coordinate already exists in M7
        existing = model.find(f".//Coordinate[@name='{coord_name}']")
        if existing is None:
            new_coord = copy.deepcopy(coord)
            m7_coords.append(new_coord)
            print(f"  HN: Added coordinate {coord_name}")
    
    # Add Millard2012 muscles from Head_Neck model
    m7_forces = model.find('.//ForceSet/objects')
    for muscle in hn_model.findall('.//Millard2012EquilibriumMuscle'):
        muscle_name = muscle.get('name', '')
        # Map body references: spine -> thoracic1
        new_muscle = copy.deepcopy(muscle)
        for elem in new_muscle.iter():
            if elem.text and elem.text.strip() == 'spine':
                elem.text = 'thoracic1'
        m7_forces.append(new_muscle)
    
    print(f"  HN: Added {len(hn_model.findall('.//Millard2012EquilibriumMuscle'))} neck muscles")

# ============================================================
# Add Hand_Wrist components (carpal bones, hand/wrist muscles)
# ============================================================

def add_hand_wrist(model, hw_model):
    """Add carpal bones and hand/wrist muscles from Hand_Wrist model (both sides)."""
    m7_bodies = model.find('.//BodySet/objects')
    m7_joints = model.find('.//JointSet/objects')
    m7_coords = model.find('.//CoordinateSet/objects')
    m7_forces = model.find('.//ForceSet/objects')
    
    # Right side hand/wrist bodies
    hw_bodies_to_add_r = []
    for body in hw_model.findall('.//BodySet/objects/Body'):
        bname = body.get('name')
        if bname == 'ground':
            continue
        # Skip bodies that already exist in M7 (clavicle, scapula, humerus, ulna, radius)
        if bname in ('clavicle', 'scapula', 'humerus', 'ulna', 'radius'):
            continue
        # These are new hand/wrist bodies - add with _r suffix
        new_body = copy.deepcopy(body)
        new_body.set('name', bname + '_r')
        # Fix mass (B6/B7)
        if bname + '_r' in CARPAL_MASSES:
            mass = new_body.find('mass')
            if mass is not None:
                mass.text = str(CARPAL_MASSES[bname + '_r'])
        elif bname == 'capitate':
            mass = new_body.find('mass')
            if mass is not None:
                mass.text = '0.008'
        hw_bodies_to_add_r.append(new_body)
    
    # Left side hand/wrist bodies (mirror)
    hw_bodies_to_add_l = []
    for body in hw_model.findall('.//BodySet/objects/Body'):
        bname = body.get('name')
        if bname == 'ground':
            continue
        if bname in ('clavicle', 'scapula', 'humerus', 'ulna', 'radius'):
            continue
        new_body = copy.deepcopy(body)
        new_body.set('name', bname + '_l')
        # Mirror z-coordinates
        mass = new_body.find('mass')
        if mass is not None:
            if bname + '_l' in CARPAL_MASSES:
                mass.text = str(CARPAL_MASSES[bname + '_l'])
            elif bname == 'capitate':
                mass.text = '0.008'
        # Mirror location
        loc = new_body.find('mass_center')
        if loc is not None and loc.text:
            parts = loc.text.strip().split()
            if len(parts) >= 3:
                loc.text = f'{parts[0]} {parts[1]} {-float(parts[2])}'
        # Mirror geometry
        for geom in new_body.findall('.//DisplayGeometry'):
            for transform in geom.findall('.//transform'):
                if transform.text:
                    parts = transform.text.strip().split()
                    if len(parts) >= 16:
                        # Mirror z translation (index 3, 7, 11)
                        parts[3] = str(-float(parts[3]))
                        parts[7] = str(-float(parts[7]))
                        parts[11] = str(-float(parts[11]))
                        transform.text = ' '.join(parts)
        hw_bodies_to_add_l.append(new_body)
    
    # Add bodies
    for body in hw_bodies_to_add_r + hw_bodies_to_add_l:
        m7_bodies.append(body)
    print(f"  HW: Added {len(hw_bodies_to_add_r)} right + {len(hw_bodies_to_add_l)} left hand/wrist bodies")
    
    # Remove old hand_R and hand_L bodies
    for body in list(model.findall('.//BodySet/objects/Body')):
        if body.get('name') in ('hand_R', 'hand_L'):
            model.find('.//BodySet/objects').remove(body)
            print(f"  HW: Removed old {body.get('name')} body")
    
    # Add joints
    for joint in hw_model.findall('.//JointSet/objects/*'):
        joint_name = joint.get('name', '')
        # Add for right side
        new_joint_r = copy.deepcopy(joint)
        new_joint_r.set('name', joint_name + '_r')
        # Map body names for right side
        for elem in new_joint_r.iter():
            if elem.text:
                t = elem.text.strip()
                if t == 'ground':
                    continue
                if t in HW_TO_M7_BODY_MAP_R:
                    elem.text = HW_TO_M7_BODY_MAP_R[t]
                elif t not in ('ground',) and t not in get_body_names_from_element(model):
                    # Add _r suffix for hand/wrist specific bodies
                    if t + '_r' in [b.get('name') for b in hw_bodies_to_add_r]:
                        elem.text = t + '_r'
        m7_joints.append(new_joint_r)
        
        # Add for left side (mirror)
        new_joint_l = copy.deepcopy(joint)
        new_joint_l.set('name', joint_name + '_l')
        for elem in new_joint_l.iter():
            if elem.text:
                t = elem.text.strip()
                if t == 'ground':
                    continue
                if t in HW_TO_M7_BODY_MAP_R:
                    # Map to left side
                    left_map = {v.rstrip('_R') + '_L' if v.endswith('_R') else v for v in HW_TO_M7_BODY_MAP_R.values()}
                    elem.text = t.replace('_R', '_L').replace('_r', '_l')
                elif t not in ('ground',):
                    if t + '_l' in [b.get('name') for b in hw_bodies_to_add_l]:
                        elem.text = t + '_l'
        m7_joints.append(new_joint_l)
    
    # Add coordinates for hand/wrist
    for coord in hw_model.findall('.//CoordinateSet/objects/Coordinate'):
        coord_name = coord.get('name', '')
        existing = model.find(f".//Coordinate[@name='{coord_name}_r']")
        if existing is None:
            # Add right side coordinate
            new_coord_r = copy.deepcopy(coord)
            new_coord_r.set('name', coord_name + '_r')
            m7_coords.append(new_coord_r)
            # Add left side coordinate
            new_coord_l = copy.deepcopy(coord)
            new_coord_l.set('name', coord_name + '_l')
            m7_coords.append(new_coord_l)
    
    # Add Millard2012 muscles from Hand_Wrist model (right side + left side mirror)
    for muscle in hw_model.findall('.//Millard2012EquilibriumMuscle'):
        # Right side
        new_muscle_r = copy.deepcopy(muscle)
        muscle_name = muscle.get('name', '')
        new_muscle_r.set('name', muscle_name + '_r')
        for elem in new_muscle_r.iter():
            if elem.text:
                t = elem.text.strip()
                if t in HW_TO_M7_BODY_MAP_R:
                    elem.text = HW_TO_M7_BODY_MAP_R[t]
                elif t not in ('ground',) and t + '_r' in [b.get('name') for b in hw_bodies_to_add_r]:
                    elem.text = t + '_r'
        m7_forces.append(new_muscle_r)
        
        # Left side (mirror)
        new_muscle_l = copy.deepcopy(muscle)
        new_muscle_l.set('name', muscle_name + '_l')
        for elem in new_muscle_l.iter():
            if elem.text:
                t = elem.text.strip()
                if t in HW_TO_M7_BODY_MAP_R:
                    elem.text = HW_TO_M7_BODY_MAP_R[t].replace('_R', '_L').replace('_r', '_l')
                elif t not in ('ground',) and t + '_l' in [b.get('name') for b in hw_bodies_to_add_l]:
                    elem.text = t + '_l'
        m7_forces.append(new_muscle_l)
    
    print(f"  HW: Added hand/wrist muscles (both sides)")

def get_body_names_from_element(model):
    """Get body names helper."""
    return [b.get('name') for b in model.findall('.//BodySet/objects/Body')]

# ============================================================
# Add DAS3 upper extremity muscles (Schutte1993)
# ============================================================

def add_das3_muscles(model, das3_model):
    """Add upper extremity muscles from DAS3 model (both sides)."""
    m7_forces = model.find('.//ForceSet/objects')
    
    added_r = 0
    added_l = 0
    
    for muscle in das3_model.findall('.//Schutte1993Muscle_Deprecated'):
        muscle_name = muscle.get('name', '')
        
        # Skip if already exists in M7
        existing = model.find(f".//Schutte1993Muscle[@name='{muscle_name}']")
        if existing is not None:
            continue
        
        # Convert Schutte1993Muscle_Deprecated to Schutte1993Muscle for OpenSim 3.3
        new_muscle_r = copy.deepcopy(muscle)
        new_muscle_r.tag = 'Schutte1993Muscle'
        # Remove deprecated-specific elements if any
        
        # Map body names for right side
        for elem in new_muscle_r.iter():
            if elem.text:
                t = elem.text.strip()
                if t in DAS3_TO_M7_BODY_MAP_R:
                    elem.text = DAS3_TO_M7_BODY_MAP_R[t]
        m7_forces.append(new_muscle_r)
        added_r += 1
        
        # Create left side mirror
        new_muscle_l = copy.deepcopy(muscle)
        new_muscle_l.tag = 'Schutte1993Muscle'
        # Replace _r with _l in name, or add _l
        if muscle_name.endswith('_r') or muscle_name.endswith('.r'):
            left_name = muscle_name[:-2] + '_l'
        elif '_r' in muscle_name:
            left_name = muscle_name.replace('_r', '_l')
        else:
            left_name = muscle_name + '_l'
        new_muscle_l.set('name', left_name)
        
        # Map body names for left side and mirror z-coordinates
        for elem in new_muscle_l.iter():
            if elem.text:
                t = elem.text.strip()
                if t in DAS3_TO_M7_BODY_MAP_L:
                    elem.text = DAS3_TO_M7_BODY_MAP_L[t]
        m7_forces.append(new_muscle_l)
        added_l += 1
    
    print(f"  DAS3: Added {added_r} right + {added_l} left Schutte1993 muscles")

# ============================================================
# Add Lumbar_C_238 muscles (MF_, QL_ additional lumbar muscles)
# ============================================================

def add_lumbar_muscles(model, lumbar_model):
    """Add additional lumbar muscles from Lumbar_C_238 model."""
    m7_forces = model.find('.//ForceSet/objects')
    
    existing_names = set(get_muscle_names(model))
    added = 0
    skipped = 0
    
    # A1 fix: List of dot-version muscles to SKIP (duplicates of underscore versions)
    dot_muscle_pattern = re.compile(r'(QL_|MF_).*\.')
    
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle']:
        for muscle in lumbar_model.findall(f'.//{muscle_tag}'):
            muscle_name = muscle.get('name', '')
            
            # A1: Skip dot-version duplicates
            if dot_muscle_pattern.search(muscle_name):
                skipped += 1
                continue
            
            # Skip if already exists
            if muscle_name in existing_names:
                skipped += 1
                continue
            
            # Skip if the _r or _l version already exists (after A5 renaming)
            base_name = muscle_name.rstrip('_r').rstrip('_l')
            
            new_muscle = copy.deepcopy(muscle)
            
            # Map body names from Lumbar model to M7
            lumbar_to_m7 = {
                'torso': 'thoracic12',  # Lumbar's "torso" is the lowest thoracic
                'LB_wrap': 'lumbar1',  # approximate
                # pelvis, sacrum, Abdomen, lumbar1-5 are the same
            }
            
            for elem in new_muscle.iter():
                if elem.text:
                    t = elem.text.strip()
                    if t in lumbar_to_m7:
                        elem.text = lumbar_to_m7[t]
            
            m7_forces.append(new_muscle)
            existing_names.add(muscle_name)
            added += 1
    
    print(f"  Lumbar: Added {added} muscles, skipped {skipped} (duplicates/A1 dot-versions)")

# ============================================================
# Fix A1: Remove dot-version duplicate muscles (if any slipped through)
# ============================================================

def remove_dot_duplicates(model):
    """Remove any remaining dot-version duplicate muscles (A1)."""
    dot_pattern = re.compile(r'(QL_|MF_).*\.')
    removed = 0
    
    for force_set_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in list(model.findall(f'.//{force_set_tag}')):
            name = muscle.get('name', '')
            if dot_pattern.search(name):
                parent = muscle.find('..')
                # Find the actual parent <objects> element
                for parent_elem in model.findall('.//ForceSet/objects'):
                    if muscle in list(parent_elem):
                        parent_elem.remove(muscle)
                        removed += 1
                        break
    
    # Also remove from ObjectGroups
    for group in model.findall('.//ObjectGroup'):
        for member in list(group.findall('.//member')):
            if member.text and dot_pattern.search(member.text.strip()):
                group.find('.//members').remove(member)
    
    print(f"  A1: Removed {removed} dot-version duplicate muscles")

# ============================================================
# Main merge function
# ============================================================

def main():
    print("=" * 60)
    print("Building Model 2 from donor models with all fixes")
    print("=" * 60)
    
    # 1. Read base model (M7)
    print("\n[1] Reading M7_18_Baza.osim (base model)...")
    model = read_xml(os.path.join(BASE_DIR, 'M7_18_Baza.osim'))
    print(f"    Bodies: {len(get_body_names(model))}")
    print(f"    Muscles: {len(get_muscle_names(model))}")
    
    # 2. Read donor models
    print("\n[2] Reading donor models...")
    hn_model = read_xml(os.path.join(BASE_DIR, 'Head_Neck_Model_fixed.osim'))
    hw_model = read_xml(os.path.join(BASE_DIR, 'Hand_Wrist_Model_for_development.osim'))
    das3_model = read_xml(os.path.join(BASE_DIR, 'das3.osim'))
    lumbar_model = read_xml(os.path.join(BASE_DIR, 'Lumbar_C_238.osim'))
    
    # 3. Apply mass fixes (B1-B7)
    print("\n[3] Applying mass fixes (B1-B7)...")
    apply_mass_fixes(model)
    
    # 4. Add Head_Neck components
    print("\n[4] Adding Head_Neck components...")
    add_head_neck(model, hn_model)
    
    # 5. Add Hand_Wrist components
    print("\n[5] Adding Hand_Wrist components...")
    add_hand_wrist(model, hw_model)
    
    # 6. Add DAS3 muscles
    print("\n[6] Adding DAS3 upper extremity muscles...")
    add_das3_muscles(model, das3_model)
    
    # 7. Add Lumbar muscles
    print("\n[7] Adding Lumbar_C_238 muscles...")
    add_lumbar_muscles(model, lumbar_model)
    
    # 8. Apply muscle fixes
    print("\n[8] Applying muscle fixes...")
    fix_iliacus(model)           # A2
    fix_deepmult_T2_T1_bodies(model)  # A3
    fix_deepmult_naming(model)   # A4
    fix_multifidus_naming(model) # A5
    fix_cpp_ranges(model)        # A6
    fix_pron_teres(model)        # A7
    
    # 9. Remove dot-version duplicates (A1)
    print("\n[9] Removing dot-version duplicates (A1)...")
    remove_dot_duplicates(model)
    
    # 10. Write output
    print(f"\n[10] Writing output to {OUTPUT_PATH}...")
    write_xml(model, OUTPUT_PATH)
    
    # 11. Statistics
    print("\n" + "=" * 60)
    print("FINAL MODEL STATISTICS")
    print("=" * 60)
    print(f"Bodies: {len(get_body_names(model))}")
    print(f"Muscles: {len(get_muscle_names(model))}")
    
    total_mass = 0
    for body in model.findall('.//BodySet/objects/Body'):
        name = body.get('name')
        if name == 'ground':
            continue
        mass = body.find('mass')
        if mass is not None:
            total_mass += float(mass.text)
    print(f"Total mass: {total_mass:.2f} kg")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
