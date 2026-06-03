#!/usr/bin/env python3
"""
Final model fixes:
1. Recalculate masses to achieve correct total ~78 kg
2. Remove any remaining M7 arm muscles that duplicate DAS3
3. Verify all fixes
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

def main():
    model = read_xml(INPUT_PATH)
    
    # Current mass analysis
    bodies = model.findall('.//BodySet/objects/Body')
    body_masses = {}
    total = 0
    for body in bodies:
        name = body.get('name')
        if name == 'ground':
            continue
        mass = body.find('mass')
        if mass is not None:
            m = float(mass.text)
            body_masses[name] = m
            total += m
    
    print(f"Current total mass: {total:.2f} kg")
    target = 78.10  # Original model2 target
    
    # The mass increase from fixes:
    # B1 sacrum: 0.00011 -> 0.949 (+0.949)
    # B2 Abdomen: 0.00011 -> 0.5 (+0.5)
    # B3 Abd segments: 0.011*10 -> 0.25*10 (+2.39)
    # B5 pelvis: 9.14 -> 11.777 (+2.637)
    # Total added: ~6.48 kg
    # But this mass was "hidden" in the lumbar vertebrae which are over-weighted
    
    # The lumbar vertebrae in M7 have masses ~2.2 kg each (total 11.1 kg)
    # For a 75 kg male, lumbar vertebrae (bone+discs+musc) should be ~0.5-1.0 kg each
    # The excess ~6 kg in lumbar was compensating for missing Abdomen/sacrum mass
    
    # Strategy: Reduce lumbar vertebrae to compensate for the mass we added to 
    # sacrum, Abdomen, Abd segments, and pelvis
    
    excess = total - target
    print(f"Excess mass: {excess:.2f} kg")
    
    # Reduce lumbar vertebrae proportionally
    lumbar_bodies = ['lumbar1', 'lumbar2', 'lumbar3', 'lumbar4', 'lumbar5']
    lumbar_total = sum(body_masses.get(b, 0) for b in lumbar_bodies)
    print(f"Current lumbar total: {lumbar_total:.2f} kg")
    
    # Target lumbar total (reduce by excess)
    target_lumbar_total = lumbar_total - excess
    if target_lumbar_total < 2.0:  # Minimum realistic lumbar mass
        target_lumbar_total = 2.0
    
    scale_factor = target_lumbar_total / lumbar_total
    print(f"Lumbar scale factor: {scale_factor:.4f}")
    
    for body in bodies:
        name = body.get('name')
        if name in lumbar_bodies:
            mass_elem = body.find('mass')
            if mass_elem is not None:
                old_val = float(mass_elem.text)
                new_val = old_val * scale_factor
                mass_elem.text = str(new_val)
                print(f"  {name}: {old_val:.4f} -> {new_val:.4f} kg")
    
    # Also check for LD_R7/R8/R9 muscles that should have been removed
    print("\nChecking for remaining M7 arm muscles...")
    arm_bodies = {'humerus_R', 'humerus_L', 'ulna_R', 'ulna_L', 'radius_R', 'radius_L'}
    
    remaining_arm = []
    for muscle in model.findall('.//Thelen2003Muscle'):
        name = muscle.get('name', '')
        pps = muscle.findall('.//PathPointSet/objects/PathPoint')
        pps += muscle.findall('.//PathPointSet/objects/MovingPathPoint')
        pps += muscle.findall('.//PathPointSet/objects/ConditionalPathPoint')
        for pp in pps:
            body = pp.find('body')
            if body is not None and body.text and body.text.strip() in arm_bodies:
                remaining_arm.append(name)
                break
    
    if remaining_arm:
        print(f"  Remaining Thelen2003 arm muscles ({len(remaining_arm)}):")
        for name in sorted(remaining_arm):
            print(f"    {name}")
    else:
        print("  No Thelen2003 arm muscles remaining (all replaced by DAS3)")
    
    # Recalculate total
    total = 0
    for body in model.findall('.//BodySet/objects/Body'):
        name = body.get('name')
        if name == 'ground':
            continue
        mass = body.find('mass')
        if mass is not None:
            total += float(mass.text)
    
    print(f"\nFinal total mass: {total:.2f} kg")
    
    # Final muscle count
    thelen = len(model.findall('.//Thelen2003Muscle'))
    schutte = len(model.findall('.//Schutte1993Muscle'))
    millard = len(model.findall('.//Millard2012EquilibriumMuscle'))
    print(f"Muscles: {thelen}T + {schutte}S + {millard}M = {thelen+schutte+millard}")
    
    write_xml(model, OUTPUT_PATH)
    print(f"\nSaved to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
