#!/usr/bin/env python3
"""
Dump all muscle names per model for debugging pattern matching.
"""
import json

with open('/home/z/my-project/download/all_muscles_v3.json') as f:
    muscle_data = json.load(f)

model_names = ["M7", "M7_18", "M8", "M8_Corr", "M8_Norm", "M2", "M4", "M6", "M9", "Raj", "ULB"]

for mn in model_names:
    muscles = muscle_data.get(mn, [])
    names = [m["name"] for m in muscles]
    print(f"\n{'='*100}")
    print(f"  {mn} - {len(names)} muscles")
    print(f"{'='*100}")
    for name in sorted(names):
        print(f"    {name}")
