import os
import urllib.request
import ssl
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

WORKSPACE_DIR = "/home/learn-2-earn/Documents/bankofamerica"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

widgets = [
    ("gt-nav-unauth-secure-bofa-widget", "1.0.0"),
    ("gt-footer-unauth-secure-bofa-widget", "1.0.0")
]

for name, version in widgets:
    url = f"https://secure.bankofamerica.com/spa/widgets/{name}/{version}/index.html"
    local_path = os.path.join(WORKSPACE_DIR, "spa", "widgets", name, version, "index.html")
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    print(f"Downloading widget: {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved: {local_path}")
        
        # Parse for resources in asset-urls-container or style/script tags
        # Find asset-urls-container JSON
        container_match = re.search(r'id=["\']asset-urls-container["\'][^>]*>(.*?)</', html_content, re.DOTALL)
        if container_match:
            try:
                assets = json.loads(container_match.group(1).strip())
                print(f"Widget assets found in container:")
                print(json.dumps(assets, indent=2))
                
                # Download CSS
                for css_url in assets.get("css", []):
                    # Localize CSS URL
                    if css_url.startswith("https://") or css_url.startswith("//"):
                        full_css = css_url if css_url.startswith("https://") else "https:" + css_url
                        # Extract domain and path
                        # e.g. https://www2.bac-assets.com/deposits/spa-assets/...
                        parts = urllib.parse.urlparse(full_css)
                        local_css_path = os.path.join(WORKSPACE_DIR, parts.netloc, parts.path.lstrip("/"))
                        print(f"  Downloading CSS: {full_css} -> {local_css_path}")
                        
                        # Let's download it
                        os.makedirs(os.path.dirname(local_css_path), exist_ok=True)
                        req_css = urllib.request.Request(full_css, headers={'User-Agent': USER_AGENT})
                        with urllib.request.urlopen(req_css, context=ctx, timeout=15) as res_css:
                            css_content = res_css.read().decode('utf-8', errors='ignore')
                        with open(local_css_path, "w", encoding="utf-8") as f_css:
                            f_css.write(css_content)
                            
                # Download scripts
                for js_url in assets.get("scripts", []):
                    if js_url.startswith("https://") or js_url.startswith("//"):
                        full_js = js_url if js_url.startswith("https://") else "https:" + js_url
                        parts = urllib.parse.urlparse(full_js)
                        local_js_path = os.path.join(WORKSPACE_DIR, parts.netloc, parts.path.lstrip("/"))
                        print(f"  Downloading Script: {full_js} -> {local_js_path}")
                        
                        os.makedirs(os.path.dirname(local_js_path), exist_ok=True)
                        req_js = urllib.request.Request(full_js, headers={'User-Agent': USER_AGENT})
                        with urllib.request.urlopen(req_js, context=ctx, timeout=15) as res_js:
                            js_content = res_js.read()
                        with open(local_js_path, "wb") as f_js:
                            f_js.write(js_content)
            except Exception as e:
                print(f"Failed to parse or download container assets for {name}: {e}")
                
    except Exception as e:
        print(f"Failed to download or parse widget {name}: {e}")
