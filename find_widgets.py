import re
import json

paths = [
    "index.html",
    "deposits/checking/checking-accounts/index.html",
    "deposits/savings/savings-accounts/index.html"
]

for path in paths:
    print("Checking path:", path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Search for data-options=
    idx = content.find("data-options=")
    if idx == -1:
        print("  data-options not found")
        continue
    
    # Let's extract the attribute value. It might be single-quoted or double-quoted.
    quote_char = content[idx + len("data-options=")]
    
    # find the matching closing quote
    start_idx = idx + len("data-options=") + 1
    end_idx = content.find(quote_char, start_idx)
    if end_idx == -1:
        print("  closing quote not found")
        continue
    
    json_str = content[start_idx:end_idx]
    try:
        data = json.loads(json_str)
        print("  Successfully parsed JSON!")
        if "assets" in data and "widgets" in data["assets"]:
            widgets = data["assets"]["widgets"]
            for brand, brand_widgets in widgets.items():
                if isinstance(brand_widgets, dict):
                    for key, val in brand_widgets.items():
                        if isinstance(val, dict) and "name" in val:
                            name = val["name"]
                            version = val.get("version")
                            print(f"    {brand} -> {key}: {name} (version: {version})")
    except Exception as e:
        print("  JSON parse error:", e)
