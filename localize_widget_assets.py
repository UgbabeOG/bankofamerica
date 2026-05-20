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

# Use non-capturing group (?:https?:)?
url_pattern = re.compile(r'(?:https?:)?//secure2\.bac-assets\.com/[^\s"\'\'><,\)\(\\]+')

downloaded_count = 0

for file_path in widget_files:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
        
    print(f"Scanning: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find all matches
    matches = url_pattern.findall(content)
    
    # Deduplicate
    urls_to_download = set()
    for match in matches:
        url = match
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("http://"):
            url = url.replace("http://", "https://")
        urls_to_download.add(url)
        
    print(f"Found {len(urls_to_download)} unique secure2.bac-assets.com URLs")
    
    for url in sorted(urls_to_download):
        parts = urllib.parse.urlparse(url)
        # Avoid downloading folders or invalid paths
        path_str = parts.path
        # Clean double/triple/etc slashes
        path_str = re.sub(r'/+', '/', path_str)
        local_dest = os.path.join(WORKSPACE_DIR, "secure2.bac-assets.com", path_str.lstrip("/"))
        
        # If it's a file path and not already downloaded
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
                
    # Now replace the domain in the widget HTML file to point to root-relative path
    new_content = content.replace("https://secure2.bac-assets.com", "/secure2.bac-assets.com")
    new_content = new_content.replace("http://secure2.bac-assets.com", "/secure2.bac-assets.com")
    new_content = new_content.replace("//secure2.bac-assets.com", "/secure2.bac-assets.com")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated: {file_path}")

print(f"Done. Downloaded {downloaded_count} new assets.")
