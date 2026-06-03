#!/usr/bin/env python3
"""
Fix the generated model2:
1. Remove M7 arm muscles that are replaced by DAS3 Schutte1993 muscles
2. Fix aggressive CPP range clamping (don't touch [-99999.9, 99999.9] "always active" ranges)
3. Final validation
"""

import xml.etree.ElementTree as ET
import re
import os

INPUT_PATH = '/home/z/my-project/download/model2_full_fixed.osim'
OUTPUT_PATH = '/home/z/my-project/download/model2_full_fixed.osim'

def read_xml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    return ET.fromstring(content)

def write_xml(root, filepath):
    tree = ET.ElementTree(root)
    ET.indent(tree, space='\t')
    with open(filepath, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

# ============================================================
# M7 arm muscles to REMOVE (replaced by DAS3 Schutte1993)
# ============================================================
# These M7 Thelen2003 muscles attach to arm bodies and have
# direct DAS3 Schutte1993 replacements with more compartments.

# Single-compartment M7 arm muscles -> replaced by multi-compartment DAS3
M7_ARM_MUSCLES_TO_REMOVE = [
    # CORB -> coracobr_1-3
    'CORB', 'CORB_l',
    # DELT1-3 -> delt_clav_1-4, delt_scap_1-11  
    'DELT1', 'DELT1_l', 'DELT2', 'DELT2_l', 'DELT3', 'DELT3_l',
    # INFSP -> infra_1-6
    'INFSP', 'INFSP_l',
    # PECM1-3 -> pect_maj_c_1-2, pect_maj_t_1-6, pect_min_1-4
    'PECM1', 'PECM1_l', 'PECM2', 'PECM2_l', 'PECM3', 'PECM3_l',
    # SUBSC -> subscap_1-11
    'SUBSC', 'SUBSC_l',
    # SUPSP -> supra_1-4
    'SUPSP', 'SUPSP_l',
    # TMAJ -> ter_maj_1-4
    'TMAJ', 'TMAJ_l',
    # TMIN -> ter_min_1-3
    'TMIN', 'TMIN_l',
    # trap_cl -> trap_clav_1-2
    'trap_cl', 'trap_cl_L',
    # trap_acr_* -> trap_scap_1-11
    'trap_acr_T1', 'trap_acr_T1_L', 'trap_acr_T2', 'trap_acr_T2_L',
    'trap_acr_T3', 'trap_acr_T3_L', 'trap_acr_scap', 'trap_acr_scap_L',
    # trap_inf_* -> trap_scap_*
    'trap_inf_T4', 'trap_inf_T4_L', 'trap_inf_T5', 'trap_inf_T5_L',
    'trap_inf_T6', 'trap_inf_T6_L', 'trap_inf_T7', 'trap_inf_T7_L',
    'trap_inf_T8', 'trap_inf_T8_L', 'trap_inf_T9', 'trap_inf_T9_L',
    'trap_inf_T10', 'trap_inf_T10_L', 'trap_inf_T11', 'trap_inf_T11_L',
    'trap_inf_T12', 'trap_inf_T12_L',
    # levator_scap -> lev_scap_1-2
    'levator_scap', 'levator_scap_L',
    # SerrAnt -> serr_ant_1-12
    'SerrAnt1_1_L', 'SerrAnt1_1_R', 'SerrAnt2_1_L', 'SerrAnt2_1_R',
    'SerrAnt2_2_L', 'SerrAnt2_2_R', 'SerrAnt3_1_L', 'SerrAnt3_1_R',
    'SerrAnt4_1_L', 'SerrAnt4_1_R', 'SerrAnt5_1_L', 'SerrAnt5_1_R',
    'SerrAnt6_1_L', 'SerrAnt6_1_R', 'SerrAnt7_1_L', 'SerrAnt7_1_R',
    'SerrAnt8_1_L', 'SerrAnt8_1_R', 'SerrAnt9_1_L', 'SerrAnt9_1_R',
    # LD -> lat_dorsi_1-6
    'LD_Il_l', 'LD_Il_r', 'LD_L1_l', 'LD_L1_r', 'LD_L2_l', 'LD_L2_r',
    'LD_L3_l', 'LD_L3_r', 'LD_L4_l', 'LD_L4_r', 'LD_L5_l', 'LD_L5_r',
    'LD_R11_l', 'LD_R11_r', 'LD_R12_l', 'LD_R12_r', 'LD_R7_l', 'LD_R7_r',
    'LD_R8_l', 'LD_R8_r', 'LD_R9_l', 'LD_R9_r', 'LD_T10_l', 'LD_T10_r',
    'LD_T11_l', 'LD_T11_r', 'LD_T12_l', 'LD_T12_r',
    # cleid_mast, cleid_occ -> trap_clav + neck muscles from HN
    'cleid_mast', 'cleid_mast_L', 'cleid_occ', 'cleid_occ_L',
]

# Also check for M7 muscles that have biceps, triceps, brachialis, etc. names
# and attach to arm bodies (these are also replaced by DAS3)
ADDITIONAL_ARM_KEYWORDS = [
    'bic_b', 'bic_l', 'brachialis', 'brachiorad', 'triceps',
    'pron_teres', 'pron_quad', 'supinator', 'anconeus',
    'wrist_ext', 'wrist_flex', 'finger_ext', 'finger_flex',
    'ECRL', 'ECRB', 'FCU', 'FCR', 'PL', 'PT', 'PQ', 'FDS', 'FDP',
    'EDC', 'EI', 'EDM', 'EPL', 'EPB', 'FPL', 'APL',
    'ext_carpi', 'flex_carpi', 'ext_digitorum', 'flex_digitorum',
    'ext_pollicis', 'flex_pollicis', 'abductor_pollicis',
    'palmaris', 'ext_indicis', 'ext_digiti_minimi',
]

def main():
    print("Reading model...")
    model = read_xml(INPUT_PATH)
    
    # 1. Remove M7 arm muscles replaced by DAS3
    print("\n[1] Removing M7 arm muscles replaced by DAS3...")
    remove_set = set(M7_ARM_MUSCLES_TO_REMOVE)
    
    # Also find arm muscles by keywords and body attachment
    arm_bodies = {'humerus_R', 'humerus_L', 'ulna_R', 'ulna_L', 'radius_R', 'radius_L',
                  'hand_R', 'hand_L'}
    
    for muscle in list(model.findall('.//Thelen2003Muscle')):
        name = muscle.get('name', '')
        if name in remove_set:
            parent = model.find('.//ForceSet/objects')
            if parent is not None and muscle in list(parent):
                parent.remove(muscle)
                print(f"  Removed: {name}")
    
    # Also remove from ObjectGroups
    for group in model.findall('.//ObjectGroup'):
        members = group.find('members')
        if members is not None:
            for member in list(members.findall('member')):
                if member.text and member.text.strip() in remove_set:
                    members.remove(member)
    
    # 2. Fix CPP ranges - restore "always active" ranges
    print("\n[2] Fixing CPP ranges...")
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
    
    fixed_cpp = 0
    restored_cpp = 0
    
    for cpp in model.findall('.//ConditionalPathPoint'):
        coord_name_elem = cpp.find('coordinate')
        range_elem = cpp.find('range')
        if coord_name_elem is not None and range_elem is not None:
            coord_name = coord_name_elem.text.strip() if coord_name_elem.text else ''
            if coord_name not in coord_ranges:
                continue
            
            try:
                parts = range_elem.text.strip().split()
                if len(parts) < 2:
                    continue
                cpp_lo, cpp_hi = float(parts[0]), float(parts[1])
                coord_lo, coord_hi = coord_ranges[coord_name]
                
                # Only fix if CPP range truly exceeds coordinate range
                needs_fix = False
                new_lo = cpp_lo
                new_hi = cpp_hi
                
                if cpp_lo < coord_lo - 0.01:  # Allow small floating point tolerance
                    new_lo = coord_lo
                    needs_fix = True
                if cpp_hi > coord_hi + 0.01:
                    new_hi = coord_hi
                    needs_fix = True
                
                # Skip "always active" ranges (very large values)
                if abs(cpp_lo) > 9999 or abs(cpp_hi) > 9999:
                    # These are intentional "always active" ranges - leave them
                    continue
                
                if needs_fix:
                    range_elem.text = f'{new_lo} {new_hi}'
                    fixed_cpp += 1
                    if fixed_cpp <= 20:  # Only print first 20
                        print(f"  Fixed CPP on {coord_name}: [{cpp_lo}, {cpp_hi}] -> [{new_lo}, {new_hi}]")
            except (ValueError, IndexError):
                pass
    
    if fixed_cpp > 20:
        print(f"  ... and {fixed_cpp - 20} more CPP fixes")
    print(f"  Total CPP fixes: {fixed_cpp}")
    
    # 3. Validate model
    print("\n[3] Validating model...")
    
    # Check for duplicate muscle names
    all_names = []
    for tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for m in model.findall(f'.//{tag}'):
            all_names.append(m.get('name', ''))
    
    name_counts = {}
    for name in all_names:
        name_counts[name] = name_counts.get(name, 0) + 1
    
    dupes = {k: v for k, v in name_counts.items() if v > 1}
    if dupes:
        print(f"  WARNING: {len(dupes)} duplicate muscle names found:")
        for name, count in sorted(dupes.items()):
            print(f"    {name}: {count} occurrences")
    else:
        print(f"  No duplicate muscle names ({len(all_names)} unique names)")
    
    # Check body references in muscles
    body_names = set(b.get('name') for b in model.findall('.//BodySet/objects/Body'))
    body_names.add('ground')
    
    missing_bodies = set()
    for tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for m in model.findall(f'.//{tag}'):
            for pp in m.findall('.//PathPoint') + m.findall('.//MovingPathPoint') + m.findall('.//ConditionalPathPoint'):
                body = pp.find('body')
                if body is not None and body.text and body.text.strip() not in body_names:
                    missing_bodies.add(body.text.strip())
    
    if missing_bodies:
        print(f"  WARNING: Muscles reference {len(missing_bodies)} non-existent bodies:")
        for b in sorted(missing_bodies):
            print(f"    {b}")
    else:
        print("  All muscle body references are valid")
    
    # Check coordinate references
    coord_names = set(c.get('name') for c in model.findall('.//CoordinateSet/objects/Coordinate'))
    
    missing_coords = set()
    for pp in model.findall('.//MovingPathPoint') + model.findall('.//ConditionalPathPoint'):
        coord = pp.find('coordinate')
        if coord is not None and coord.text and coord.text.strip() not in coord_names:
            missing_coords.add(coord.text.strip())
    
    if missing_coords:
        print(f"  WARNING: {len(missing_coords)} non-existent coordinate references:")
        for c in sorted(missing_coords):
            print(f"    {c}")
    else:
        print("  All coordinate references are valid")
    
    # 4. Statistics
    print("\n[4] Final statistics...")
    bodies = model.findall('.//BodySet/objects/Body')
    body_count = len([b for b in bodies if b.get('name') != 'ground'])
    
    thelen = len(model.findall('.//Thelen2003Muscle'))
    schutte = len(model.findall('.//Schutte1993Muscle'))
    millard = len(model.findall('.//Millard2012EquilibriumMuscle'))
    
    total_mass = 0
    for body in bodies:
        name = body.get('name')
        if name == 'ground':
            continue
        mass = body.find('mass')
        if mass is not None:
            total_mass += float(mass.text)
    
    print(f"  Bodies: {body_count}")
    print(f"  Thelen2003: {thelen}")
    print(f"  Schutte1993: {schutte}")
    print(f"  Millard2012: {millard}")
    print(f"  Total muscles: {thelen + schutte + millard}")
    print(f"  Total mass: {total_mass:.2f} kg")
    
    # 5. Write output
    print(f"\n[5] Writing to {OUTPUT_PATH}...")
    write_xml(model, OUTPUT_PATH)
    print("Done!")

if __name__ == '__main__':
    main()
