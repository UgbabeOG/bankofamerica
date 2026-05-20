import os
import urllib.request
import ssl
import re
import urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

WORKSPACE_DIR = "/home/learn-2-earn/Documents/bankofamerica"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

widget_files = [
    os.path.join(WORKSPACE_DIR, "spa/widgets/gt-nav-unauth-secure-bofa-widget/1.0.0/index.html"),
    os.path.join(WORKSPACE_DIR, "spa/widgets/gt-footer-unauth-secure-bofa-widget/1.0.0/index.html")
]

# Find all /secure2.bac-assets.com/ matches
local_pattern = re.compile(r'/secure2\.bac-assets\.com/[^\s"\'\'><,\)\(\\]+')

downloaded_count = 0

for file_path in widget_files:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
        
    print(f"Scanning: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    matches = local_pattern.findall(content)
    
    # Deduplicate
    paths_to_download = set()
    for match in matches:
        # Extract the path from /secure2.bac-assets.com/some/path
        # and standardise it
        clean_path = match.replace("/secure2.bac-assets.com/", "")
        clean_path = re.sub(r'/+', '/', clean_path)
        paths_to_download.add(clean_path)
        
    print(f"Found {len(paths_to_download)} unique paths to download")
    
    for path in sorted(paths_to_download):
        url = f"https://secure2.bac-assets.com/{path}"
        local_dest = os.path.join(WORKSPACE_DIR, "secure2.bac-assets.com", path)
        
        if not os.path.exists(local_dest):
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)
            print(f"  Downloading: {url} -> {local_dest}")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
                with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                    data = response.read()
                with open(local_dest, "wb") as f_out:
                    f_out.write(data)
                downloaded_count += 1
            except Exception as e:
                print(f"  Failed to download {url}: {e}")

print(f"Done. Downloaded {downloaded_count} new assets.")
