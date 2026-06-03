#!/usr/bin/env python3
"""
Fix remaining issues in model2:
1. Remove duplicate deepmult/supmult muscles from Head_Neck (M7 versions already renamed correctly)
2. Fix body references: head_neck -> skull/thoracic1
3. Fix finger phalanx body references in HW muscles
"""

import xml.etree.ElementTree as ET
import re

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

# Head_Neck deepmult/supmult muscles that duplicate M7 versions
# These come from Head_Neck and overlap with M7's already-renamed versions
HN_DUPLICATE_MUSCLES = [
    'deepmult-T1-C5_r', 'deepmult-T1-C5_l',
    'deepmult-T1-C6_r', 'deepmult-T1-C6_l',
    'deepmult-T2-C7_r', 'deepmult-T2-C7_l',
    'deepmult-T2-T1_r', 'deepmult-T2-T1_l',
    'supmult-T1-C4_r', 'supmult-T1-C5_r', 'supmult-T2-C6_r',
    'supmult-T1-C4_l', 'supmult-T1-C5_l', 'supmult-T2-C6_l',
]

# Body name mapping for Hand_Wrist muscles
HW_BODY_RENAME = {
    # These are body names used in Hand_Wrist muscle path points
    # that need to be mapped to the renamed versions in the composite model
    '2proxph_r': 'proxph2_r', '2midph_r': 'midph2_r', '2distph_r': 'distph2_r',
    '3proxph_r': 'proxph3_r', '3midph_r': 'midph3_r', '3distph_r': 'distph3_r',
    '4proxph_r': 'proxph4_r', '4midph_r': 'midph4_r', '4distph_r': 'distph4_r',
    '5proxph_r': 'proxph5_r', '5midph_r': 'midph5_r', '5distph_r': 'distph5_r',
    '2proxph_l': 'proxph2_l', '2midph_l': 'midph2_l', '2distph_l': 'distph2_l',
    '3proxph_l': 'proxph3_l', '3midph_l': 'midph3_l', '3distph_l': 'distph3_l',
    '4proxph_l': 'proxph4_l', '4midph_l': 'midph4_l', '4distph_l': 'distph4_l',
    '5proxph_l': 'proxph5_l', '5midph_l': 'midph5_l', '5distph_l': 'distph5_l',
}

# Check what the actual body names are in the model
def get_actual_body_map(model):
    """Build mapping from old HW names to actual body names in model."""
    body_names = set(b.get('name') for b in model.findall('.//BodySet/objects/Body'))
    
    # Check if proxph2_r style names exist, or if 2proxph_r style exist
    actual_map = {}
    for old, new in HW_BODY_RENAME.items():
        if new in body_names:
            actual_map[old] = new
        elif old in body_names:
            # Old name is the actual name, new is wrong
            actual_map[new] = old
    
    return actual_map, body_names

def main():
    print("Reading model...")
    model = read_xml(INPUT_PATH)
    
    actual_map, body_names = get_actual_body_map(model)
    print(f"Bodies in model: {len(body_names)}")
    
    # Debug: print finger body names
    finger_bodies = [b for b in body_names if any(x in b for x in ['proxph', 'midph', 'distph', 'mc'])]
    print(f"Finger/hand bodies: {sorted(finger_bodies)}")
    
    # 1. Remove duplicate deepmult/supmult muscles from Head_Neck
    print("\n[1] Removing duplicate deepmult/supmult from Head_Neck...")
    removed = 0
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in list(model.findall(f'.//{muscle_tag}')):
            name = muscle.get('name', '')
            if name in HN_DUPLICATE_MUSCLES:
                # Check if this is a Head_Neck muscle by checking if it references "spine" body
                # (HN muscles reference "spine" which was mapped to "thoracic1")
                # Actually, just check if there's a duplicate
                parent = model.find('.//ForceSet/objects')
                if parent is not None:
                    # Find all muscles with this name
                    dupes = [m for m in parent.findall(f'.//{muscle_tag}') if m.get('name') == name]
                    if len(dupes) > 1:
                        # Remove the second one (the Head_Neck addition)
                        # The first one is the M7 version (already renamed)
                        # Check which one references thoracic bodies (M7) vs spine-mapped bodies
                        for d in dupes[1:]:
                            parent.remove(d)
                            removed += 1
                            print(f"  Removed duplicate: {name}")
    
    if removed == 0:
        # Maybe duplicates are in different muscle type lists
        # Let's check all ForceSet objects
        all_muscles = {}
        for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
            for muscle in model.findall(f'.//{muscle_tag}'):
                name = muscle.get('name', '')
                if name not in all_muscles:
                    all_muscles[name] = []
                all_muscles[name].append((muscle_tag, muscle))
        
        for name, entries in all_muscles.items():
            if len(entries) > 1:
                # Keep the first, remove the rest
                parent = model.find('.//ForceSet/objects')
                for tag, muscle in entries[1:]:
                    if parent is not None and muscle in list(parent):
                        parent.remove(muscle)
                        removed += 1
                        print(f"  Removed duplicate ({tag}): {name}")
    
    print(f"  Removed {removed} duplicate muscles")
    
    # 2. Fix body references: head_neck -> skull or thoracic1
    print("\n[2] Fixing body references...")
    head_neck_fixes = 0
    
    for muscle_tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for muscle in model.findall(f'.//{muscle_tag}'):
            name = muscle.get('name', '')
            for pp in muscle.findall('.//PathPoint') + muscle.findall('.//MovingPathPoint') + muscle.findall('.//ConditionalPathPoint'):
                body = pp.find('body')
                if body is not None and body.text:
                    bname = body.text.strip()
                    
                    # Fix head_neck references
                    if bname == 'head_neck':
                        # Determine if this should be skull or thoracic1
                        # If muscle name contains neck/head -> skull
                        # If muscle name contains thoracic -> thoracic1
                        if any(x in name.lower() for x in ['head', 'skull', 'neck', 'cerv', 'hyoid', 'splen_cap', 'splen_cerv', 'semispin_cap', 'long_colli', 'long_cap', 'rect_cap', 'obliq_cap']):
                            body.text = 'skull'
                        else:
                            body.text = 'thoracic1'
                        head_neck_fixes += 1
                        print(f"  Fixed head_neck -> {body.text} in {name}")
                    
                    # Fix finger phalanx references
                    if bname in actual_map:
                        body.text = actual_map[bname]
    
    print(f"  Fixed {head_neck_fixes} head_neck body references")
    
    # 3. Final validation
    print("\n[3] Final validation...")
    
    # Check duplicate names
    all_names = []
    for tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for m in model.findall(f'.//{tag}'):
            all_names.append(m.get('name', ''))
    
    name_counts = {}
    for name in all_names:
        name_counts[name] = name_counts.get(name, 0) + 1
    
    dupes = {k: v for k, v in name_counts.items() if v > 1}
    if dupes:
        print(f"  WARNING: {len(dupes)} duplicate muscle names:")
        for name, count in sorted(dupes.items()):
            print(f"    {name}: {count}")
    else:
        print(f"  No duplicates ({len(all_names)} unique muscles)")
    
    # Check body references
    body_names = set(b.get('name') for b in model.findall('.//BodySet/objects/Body'))
    body_names.add('ground')
    
    missing_bodies = {}
    for tag in ['Thelen2003Muscle', 'Schutte1993Muscle', 'Millard2012EquilibriumMuscle']:
        for m in model.findall(f'.//{tag}'):
            for pp in m.findall('.//PathPoint') + m.findall('.//MovingPathPoint') + m.findall('.//ConditionalPathPoint'):
                body = pp.find('body')
                if body is not None and body.text and body.text.strip() not in body_names:
                    bname = body.text.strip()
                    mname = m.get('name', '')
                    if bname not in missing_bodies:
                        missing_bodies[bname] = []
                    missing_bodies[bname].append(mname)
    
    if missing_bodies:
        print(f"  WARNING: {len(missing_bodies)} missing body references:")
        for bname, muscles in sorted(missing_bodies.items()):
            print(f"    {bname} (used by {len(muscles)} muscles): {muscles[:3]}...")
    else:
        print("  All body references valid")
    
    # Check coordinate references
    coord_names = set(c.get('name') for c in model.findall('.//CoordinateSet/objects/Coordinate'))
    missing_coords = set()
    for pp in model.findall('.//MovingPathPoint') + model.findall('.//ConditionalPathPoint'):
        coord = pp.find('coordinate')
        if coord is not None and coord.text and coord.text.strip() not in coord_names:
            missing_coords.add(coord.text.strip())
    
    if missing_coords:
        print(f"  WARNING: Missing coordinates: {sorted(missing_coords)}")
    else:
        print("  All coordinate references valid")
    
    # Statistics
    bodies = model.findall('.//BodySet/objects/Body')
    body_count = len([b for b in bodies if b.get('name') != 'ground'])
    thelen = len(model.findall('.//Thelen2003Muscle'))
    schutte = len(model.findall('.//Schutte1993Muscle'))
    millard = len(model.findall('.//Millard2012EquilibriumMuscle'))
    total_mass = sum(float(b.find('mass').text) for b in bodies if b.get('name') != 'ground' and b.find('mass') is not None)
    
    print(f"\n[4] Final model statistics:")
    print(f"  Bodies: {body_count}")
    print(f"  Thelen2003: {thelen}")
    print(f"  Schutte1993: {schutte}")
    print(f"  Millard2012: {millard}")
    print(f"  Total muscles: {thelen + schutte + millard}")
    print(f"  Total mass: {total_mass:.2f} kg")
    
    # Write
    print(f"\n[5] Writing to {OUTPUT_PATH}...")
    write_xml(model, OUTPUT_PATH)
    print("Done!")

if __name__ == '__main__':
    main()
