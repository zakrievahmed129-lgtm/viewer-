import re

with open("scratch/all_cartoons_combined.py", "r", encoding="utf-8") as f:
    combined_code = f.read()

# Extract each class definition from combined_code
classes_to_extract = [
    "CartoonPullerOverlay",
    "CartoonDrunkOverlay",
    "CartoonWallOverlay",
    "CartoonPainterOverlay",
    "CartoonKeysOverlay",
    "CartoonGhostOverlay",
    "CartoonMegaphoneOverlay",
    "CartoonRotateOverlay",
    "ElusiveWindowLegsOverlay"
]

extracted_classes = {}
for i, name in enumerate(classes_to_extract):
    start_pattern = f"class {name}:"
    start_idx = combined_code.find(start_pattern)
    if start_idx == -1:
        raise ValueError(f"Could not find {name} in combined code!")
    
    if i < len(classes_to_extract) - 1:
        next_pattern = f"class {classes_to_extract[i+1]}:"
        end_idx = combined_code.find(next_pattern)
    else:
        end_idx = combined_code.find("def test_instantiate_all():")
        if end_idx == -1:
            end_idx = len(combined_code)
            
    extracted_classes[name] = combined_code[start_idx:end_idx].strip()
    print(f"Extracted {name} ({len(extracted_classes[name])} chars)")

print("All classes extracted successfully!")
