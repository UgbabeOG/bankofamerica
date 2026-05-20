import os
import re
import urllib.request
import urllib.parse
import ssl
import html

WORKSPACE_DIR = "/home/learn-2-earn/Documents/bankofamerica"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Create a custom SSL context to avoid certificate validation errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Pages to clone and localize
PAGES_TO_CLONE = {
    "https://www.bankofamerica.com/": "index.html",
    "https://www.bankofamerica.com": "index.html",
    "https://www.bankofamerica.com/credit-cards/": "credit-cards/index.html",
    "https://www.bankofamerica.com/deposits/checking/checking-accounts/": "deposits/checking/checking-accounts/index.html",
    "https://www.bankofamerica.com/deposits/savings/savings-accounts/": "deposits/savings/savings-accounts/index.html",
    "https://www.bankofamerica.com/auto-loans/": "auto-loans/index.html",
    "https://www.bankofamerica.com/mortgage/home-mortgage/": "mortgage/home-mortgage/index.html",
    "https://www.bankofamerica.com/help/overview/": "help/overview/index.html",
    "https://www.bankofamerica.com/customer-service/contact-us/": "customer-service/contact-us/index.html",
    "https://www.bankofamerica.com/smallbusiness/": "smallbusiness/index.html",
    "https://www.bankofamerica.com/student-banking/": "student-banking/index.html"
}

PAGE_PATH_MAPPINGS = {
    "/": "index.html",
    "/credit-cards/": "credit-cards/index.html",
    "/deposits/checking/checking-accounts/": "deposits/checking/checking-accounts/index.html",
    "/deposits/savings/savings-accounts/": "deposits/savings/savings-accounts/index.html",
    "/auto-loans/": "auto-loans/index.html",
    "/mortgage/home-mortgage/": "mortgage/home-mortgage/index.html",
    "/help/overview/": "help/overview/index.html",
    "/customer-service/contact-us/": "customer-service/contact-us/index.html",
    "/smallbusiness/": "smallbusiness/index.html",
    "/student-banking/": "student-banking/index.html"
}

ASSET_DOMAINS = [
    "assets.bankofamerica.com",
    "www1.bac-assets.com",
    "www2.bac-assets.com",
    "www.bankofamerica.com",
    "scripts-olui2.fs.ml.bac-assets.com",
    "api2.bac-assets.com",
    "secure2.bac-assets.com",
    "images.benefits.ml.bac-assets.com"
]

ASSET_EXTENSIONS = {
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot', '.html', '.json'
}

def clean_url_path(url_path):
    clean_path = re.sub(r'/+', '/', url_path)
    if clean_path.startswith('/'):
        clean_path = clean_path[1:]
    return clean_path

def download_file(url, local_path):
    dir_name = os.path.dirname(local_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return True

    print(f"Downloading: {url} -> {local_path}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            content = response.read()
            with open(local_path, "wb") as f:
                f.write(content)
        # If it's a CSS file, we should scan and download its relative assets
        if local_path.endswith('.css'):
            localize_css_assets(local_path, url)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def localize_css_assets(css_path, css_url):
    try:
        with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read CSS {css_path}: {e}")
        return

    # Find url(...) patterns in CSS
    url_pattern = re.compile(r'url\s*\(\s*([\'"]?)(.*?)\1\s*\)', re.IGNORECASE)
    matches = url_pattern.findall(content)
    
    replacements = {}
    for quote, rel_url in matches:
        rel_url = rel_url.strip()
        if not rel_url or rel_url.startswith('data:') or rel_url.startswith('#'):
            continue
        
        # Build absolute URL of the asset
        abs_url = urllib.parse.urljoin(css_url, rel_url)
        parsed = urllib.parse.urlparse(abs_url)
        
        # Check if asset domain is in our list
        domain = parsed.netloc
        if not domain or not any(domain == d or domain.endswith("." + d) for d in ASSET_DOMAINS):
            continue
            
        clean_path = clean_url_path(parsed.path)
        _, ext = os.path.splitext(clean_path.lower())
        
        # We only download valid extensions
        if ext in ASSET_EXTENSIONS:
            # We want to place the resource in workspace_dir/domain/clean_path
            local_filename = os.path.join(WORKSPACE_DIR, domain, clean_path)
            
            # Download the asset
            download_url = f"https://{domain}/{clean_path}"
            if parsed.query:
                download_url += f"?{parsed.query}"
            
            if download_file(download_url, local_filename):
                # Calculate path relative to the CSS file
                css_dir = os.path.dirname(css_path)
                rel_path_to_resource = os.path.relpath(local_filename, css_dir)
                replacements[f"{quote}{rel_url}{quote}"] = f"'{rel_path_to_resource}'"

    if replacements:
        print(f"Localizing CSS assets in {css_path} ({len(replacements)} matches)...")
        # Apply replacements
        sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
        for original, new_path in sorted_replacements:
            content = content.replace(f"({original})", f"({new_path})")
            content = content.replace(f"({original.strip('\'\"')})", f"({new_path})")
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)

def get_rel_prefix(depth):
    return "../" * depth

def clean_raw_string(s):
    url_to_clean = s
    while True:
        changed = False
        for suffix in ('&amp;', '&amp', '&quot;', '&quot', '&#x27;', '&#x27', '&#x3d;', '&#x3d', '&#x3D;', '&#x3D', '&gt;', '&gt', '&lt;', '&lt', ';', '"', "'", '>', '<', ')', ']', '}', '\\'):
            if url_to_clean.endswith(suffix):
                url_to_clean = url_to_clean[:-len(suffix)]
                changed = True
        if not changed:
            break
    return url_to_clean

def get_localized_url(val, page_depth, prefix, live_page_url):
    # Ignore data URIs, empty strings, mailto, tel, javascript: or hash links
    if not val or val.startswith('data:') or val.startswith('#') or val.startswith('mailto:') or val.startswith('tel:') or val.startswith('javascript:'):
        return None
        
    # If the URL is already localized, skip it
    if val.startswith('../') or any(val.startswith(d) for d in ASSET_DOMAINS) or any(val.startswith(p_file) for p_file in PAGES_TO_CLONE.values()):
        return None
        
    parsed = urllib.parse.urlparse(val)
    domain = parsed.netloc
    path = parsed.path
    
    # Case 1: Absolute URL
    if domain:
        if not any(domain == d or domain.endswith("." + d) for d in ASSET_DOMAINS):
            return None
            
        clean_path = clean_url_path(path)
        _, ext = os.path.splitext(clean_path.lower())
        
        page_url = f"https://{domain}/{clean_path}"
        if not page_url.endswith('/') and ext == '':
            page_url += '/'
            
        matched_page = None
        for p_url, p_file in PAGES_TO_CLONE.items():
            if p_url.rstrip('/') == page_url.rstrip('/'):
                matched_page = p_file
                break
                
        if matched_page:
            return prefix + matched_page
            
        if ext in ASSET_EXTENSIONS or ext == '.go' or 'spa-assets' in clean_path or 'min/' in clean_path or 'js/' in clean_path or 'css/' in clean_path or 'fonts/' in clean_path or 'images/' in clean_path:
            local_filename = os.path.join(WORKSPACE_DIR, domain, clean_path)
            download_url = f"https://{domain}/{clean_path}"
            if parsed.query:
                download_url += f"?{parsed.query}"
            
            download_file(download_url, local_filename)
            return prefix + f"{domain}/{clean_path}"
            
    # Case 2: Root-relative URL (starts with a single slash)
    elif val.startswith('/') and not val.startswith('//'):
        clean_path = clean_url_path(path)
        _, ext = os.path.splitext(clean_path.lower())
        
        norm_path = "/" + clean_path
        if not norm_path.endswith('/') and ext == '':
            norm_path += '/'
            
        matched_page = None
        for r_path, p_file in PAGE_PATH_MAPPINGS.items():
            if r_path.rstrip('/') == norm_path.rstrip('/'):
                matched_page = p_file
                break
                
        if matched_page:
            return prefix + matched_page
            
        if ext in ASSET_EXTENSIONS or 'spa-assets' in clean_path or 'min/' in clean_path or 'js/' in clean_path or 'css/' in clean_path or 'fonts/' in clean_path or 'images/' in clean_path:
            local_filename = os.path.join(WORKSPACE_DIR, clean_path)
            download_url = f"https://www.bankofamerica.com/{clean_path}"
            if parsed.query:
                download_url += f"?{parsed.query}"
                
            download_file(download_url, local_filename)
            return prefix + clean_path

    # Case 3: Protocol-relative URL (starts with //)
    elif val.startswith('//'):
        return get_localized_url("https:" + val, page_depth, prefix, live_page_url)
        
    # Case 4: Page-relative URL
    else:
        abs_url = urllib.parse.urljoin(live_page_url, val)
        return get_localized_url(abs_url, page_depth, prefix, live_page_url)
        
    return None

def localize_content(html_content, page_depth, live_page_url):
    prefix = get_rel_prefix(page_depth)
    
    def repl_attr(match):
        attr = match.group(1)
        quote = match.group(2)
        val = match.group(3).strip()
        
        val_clean = clean_raw_string(html.unescape(val))
        local_val = get_localized_url(val_clean, page_depth, prefix, live_page_url)
        if local_val:
            return f'{attr}={quote}{local_val}{quote}'
        return match.group(0)

    def repl_url(match):
        quote = match.group(1)
        val = match.group(2).strip()
        val_clean = clean_raw_string(html.unescape(val))
        local_val = get_localized_url(val_clean, page_depth, prefix, live_page_url)
        if local_val:
            return f'url({quote}{local_val}{quote})'
        return match.group(0)

    # Match attributes like href, src, etc.
    attr_pattern = re.compile(
        r'\b(href|src|data-href|data-src|data-mobile-src|data-tablet-src|data-desktop-src)\s*=\s*(["\'])(.*?)\2',
        re.IGNORECASE
    )
    html_content = attr_pattern.sub(repl_attr, html_content)
    
    # Match url(...) inside styles
    url_pattern = re.compile(r'url\s*\(\s*([\'"]?)(.*?)\1\s*\)', re.IGNORECASE)
    html_content = url_pattern.sub(repl_url, html_content)
    
    return html_content

def clone_and_localize_all():
    for live_url, local_rel_path in PAGES_TO_CLONE.items():
        local_path = os.path.join(WORKSPACE_DIR, local_rel_path)
        depth = len(local_rel_path.split('/')) - 1
        
        print(f"\nProcessing page: {live_url} -> {local_path} (depth={depth})")
        
        # Download or load content
        if local_rel_path == "index.html" and os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                page_html = f.read()
        else:
            print(f"Downloading live page HTML: {live_url}")
            try:
                req = urllib.request.Request(live_url, headers={'User-Agent': USER_AGENT})
                with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                    page_html = response.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Failed to download page HTML {live_url}: {e}")
                continue
                
        localized_html = localize_content(page_html, depth, live_url)
        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(localized_html)
        print(f"Saved localized page: {local_path}")

if __name__ == "__main__":
    clone_and_localize_all()
    print("\nLocalization completed successfully!")
