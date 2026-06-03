import re, json, os

OSIM_DIR = '/home/z/my-project/upload/'

MODEL_FILES = {
    'M7': '997_SizeScaled_CurvatureAdjust_MuscleAdjust.osim',
    'M7_18': 'M7_18_Baza.osim',
    'M8': 'Caruthers_FullBodyModel2016_Scaled_Arms.osim',
    'M8_Corr': 'M8_Caruthers_Corrected.osim',
    'M8_Norm': 'M8_NormTaz.osim',
    'M2': 'FBLSmodel.osim',  # 325 muscles, matches 324 in existing data
    'M4': 'ScapulothorachicJoint_Shoulder.osim',
    'M6': 'Head_Neck_Model.osim',
    'M9': 'Hand_Wrist_Model_for_development.osim',
    'Raj': 'Rajagopal2015.osim',
    'ULB': 'UpperLowerBody.osim',
}

MUSCLE_TYPES = [
    'Thelen2003Muscle', 'Millard2012EquilibriumMuscle',
    'Millard2012AccelerationMuscle', 'RigidTendonMuscle',
    'Schutte1993Muscle'
]

def parse_muscles_from_osim(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
    
    muscles = []
    
    # Find all muscle blocks - match <MuscleType name="..."> ... </MuscleType>
    for mtype in MUSCLE_TYPES:
        # Pattern: <Thelen2003Muscle name="muscle_name"> ... </Thelen2003Muscle>
        pattern = rf'<{mtype}\s+name="([^"]+)">(.*?)</{mtype}>'
        for match in re.finditer(pattern, content, re.DOTALL):
            muscle_name = match.group(1)
            muscle_body = match.group(2)
            
            # Extract path points - look for GeometryPath > PathPointSet
            bodies_in_path = []
            
            # Find PathPoint and ConditionalPathPoint
            pp_pattern = r'<(?:PathPoint|ConditionalPathPoint)\s+name="[^"]*">\s*<location>[^<]*</location>\s*<body>([^<]+)</body>'
            bodies_found = re.findall(pp_pattern, muscle_body)
            
            if not bodies_found:
                # Alternative: look in GeometryPath section
                gp_match = re.search(r'<GeometryPath>(.*?)</GeometryPath>', muscle_body, re.DOTALL)
                if gp_match:
                    gp_body = gp_match.group(1)
                    bodies_found = re.findall(pp_pattern, gp_body)
            
            if bodies_found:
                # Deduplicate consecutive same bodies
                deduped = []
                prev = None
                for b in bodies_found:
                    if b != prev:
                        deduped.append(b)
                        prev = b
                bodies_in_path = deduped
            
            muscles.append({
                'name': muscle_name,
                'bodies': bodies_in_path,
                'type': mtype
            })
    
    return muscles

# Parse all models
all_models = {}
for model_name, filename in MODEL_FILES.items():
    filepath = os.path.join(OSIM_DIR, filename)
    if not os.path.exists(filepath):
        print(f'WARNING: {filepath} not found')
        all_models[model_name] = []
        continue
    
    muscles = parse_muscles_from_osim(filepath)
    all_models[model_name] = muscles
    print(f'{model_name} ({filename}): {len(muscles)} muscles')

# Save
out_path = '/home/z/my-project/download/all_muscles_v3.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_models, f, ensure_ascii=False, indent=2)
print(f'\nSaved: {out_path}')
