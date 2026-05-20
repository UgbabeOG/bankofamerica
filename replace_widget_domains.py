import os

files_to_update = [
    "index.html",
    "deposits/checking/checking-accounts/index.html",
    "deposits/savings/savings-accounts/index.html"
]

for rel_path in files_to_update:
    path = os.path.join("/home/learn-2-earn/Documents/bankofamerica", rel_path)
    if not os.path.exists(path):
        print(f"Skipping non-existent file: {path}")
        continue
    
    print(f"Processing: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Let's count occurrences
    count_3000 = content.count("http://localhost:3000")
    count_3005 = content.count("http://localhost:3005")
    print(f"  Found {count_3000} of localhost:3000, {count_3005} of localhost:3005")
    
    # Replace
    new_content = content.replace("http://localhost:3000", "http://localhost:8000")
    new_content = new_content.replace("http://localhost:3005", "http://localhost:8000")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  Done.")
