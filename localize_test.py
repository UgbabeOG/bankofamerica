import re
import os

WORKSPACE_DIR = "/home/learn-2-earn/Documents/bankofamerica"
INDEX_HTML = os.path.join(WORKSPACE_DIR, "index.html")

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# Refined regex that excludes HTML entities (like &quot; or &#x3d;)
# Path does not contain '&', ';', or quotes.
# Query does not contain ';' or quotes.
url_pattern = re.compile(
    r'(https?:)?//([a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+)(/[a-zA-Z0-9_\-\.\/]*(?:\?[a-zA-Z0-9_\-\.\/&=%~!:\(\)\+]*)?(?:\#[a-zA-Z0-9_\-\.\/&=%~!:\(\)\+]*)?)'
)

matches = url_pattern.findall(content)
unique_urls = sorted(list(set([f"{m[0]}//{m[1]}{m[2]}" for m in matches])))

print(f"Total unique matches: {len(unique_urls)}")
print("Sample matches:")
for url in unique_urls[:30]:
    print(f"- {url}")
