#!/usr/bin/env python3

# ================================================================
#
#   ███████╗███████╗███╗   ██╗██╗   ██╗ ██████╗ ██████╗  █████╗
#   ╚══███╔╝██╔════╝████╗  ██║██║   ██║██╔═══██╗██╔══██╗██╔══██╗
#     ███╔╝ █████╗  ██╔██╗ ██║██║   ██║██║   ██║██████╔╝███████║
#    ███╔╝  ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██║
#   ███████╗███████╗██║ ╚████║ ╚████╔╝ ╚██████╔╝██║  ██║██║  ██║
#   ╚══════╝╚══════╝╚═╝  ╚═══╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
#
#   RECON TOOL v3.0  |  Empire: ZENVORA  |  By: Zenomro
#   Red Team Edition — Use only on authorized targets
#
# ================================================================

import subprocess, sys, os, json, sqlite3, random, time, argparse
from datetime import datetime

# ── Colors ──────────────────────────────────────────────────────
R  = '\033[91m'   # Red
G  = '\033[92m'   # Green
Y  = '\033[93m'   # Yellow
B  = '\033[94m'   # Blue
M  = '\033[95m'   # Magenta
C  = '\033[96m'   # Cyan
W  = '\033[97m'   # White
X  = '\033[0m'    # Reset
BD = '\033[1m'    # Bold
DM = '\033[2m'    # Dim

# ── Config File ─────────────────────────────────────────────────
CONFIG_FILE = os.path.expanduser("~/.zenvora_config.json")
DB_FILE     = os.path.expanduser("~/.zenvora_history.db")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0",
]

CVE_DB = {
    "openssh 6.6": ["CVE-2016-0777 (roaming — info leak)", "CVE-2016-0778 (buffer overflow)"],
    "openssh 7.2": ["CVE-2016-6515 (DoS)", "CVE-2016-10009 (privesc)"],
    "apache 2.4.7": ["CVE-2014-0226 (race condition)", "CVE-2014-0118 (DoS)", "CVE-2017-7679"],
    "apache 2.4.49": ["CVE-2021-41773 (path traversal — CRITICAL)", "CVE-2021-42013"],
    "apache 2.4.50": ["CVE-2021-42013 (RCE — CRITICAL)"],
    "vsftpd 2.3.4": ["CVE-2011-2523 (backdoor — CRITICAL)"],
    "proftpd 1.3.5": ["CVE-2015-3306 (RCE — CRITICAL)"],
    "samba 3": ["CVE-2017-7494 (SambaCry — RCE CRITICAL)"],
    "mysql 5.5": ["CVE-2012-2122 (auth bypass)", "CVE-2016-6662 (RCE)"],
    "php 5": ["CVE-2012-1823 (RCE)", "CVE-2014-4721 (info leak)"],
    "iis 6.0": ["CVE-2017-7269 (buffer overflow — CRITICAL)"],
    "nginx 1.1": ["CVE-2013-2028 (stack overflow)"],
    "openssl 1.0.1": ["CVE-2014-0160 (Heartbleed — CRITICAL)"],
    "drupal 7": ["CVE-2018-7600 (Drupalgeddon2 — RCE CRITICAL)"],
    "wordpress 4": ["CVE-2017-8295 (password reset)", "CVE-2019-8943 (path traversal)"],
}

# ================================================================
# UTILS
# ================================================================

def banner():
    os.system('clear')
    print(f"""
{R}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  ███████╗███████╗███╗   ██╗██╗   ██╗ ██████╗ ██████╗  █████╗║
║  ╚══███╔╝██╔════╝████╗  ██║██║   ██║██╔═══██╗██╔══██╗██╔══██║
║    ███╔╝ █████╗  ██╔██╗ ██║██║   ██║██║   ██║██████╔╝███████║
║   ███╔╝  ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██║
║  ███████╗███████╗██║ ╚████║ ╚████╔╝ ╚██████╔╝██║  ██║██║  ██║
║  ╚══════╝╚══════╝╚═╝  ╚═══╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
║                                                              ║{X}
{C}║   RECON TOOL v3.0  ·  Empire: ZENVORA  ·  By: Zenomro       ║{X}
{R}╚══════════════════════════════════════════════════════════════╝{X}
""")

def sec(title, emoji="◈"):
    print(f"\n{B}{'─'*62}{X}")
    print(f"{BD}{C}  {emoji}  {title}{X}")
    print(f"{B}{'─'*62}{X}\n")

def log(level, msg):
    icons = {"+":(G,"[+]"), "*":(Y,"[*]"), "-":(R,"[-]"), "!":(M,"[!]"), ">":(C,"[>]")}
    col, icon = icons.get(level, (W,"[?]"))
    print(f"  {col}{BD}{icon}{X} {msg}")

def run(cmd, timeout=90, use_proxy=False):
    if use_proxy:
        cmd = f"proxychains4 -q {cmd}"
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def stealth_delay(anon_level):
    if anon_level >= 1:
        delay = random.uniform(0.5, 2.0) if anon_level == 1 else random.uniform(1.0, 4.0)
        time.sleep(delay)

def get_random_ua():
    return random.choice(USER_AGENTS)

def progress(msg):
    print(f"  {Y}⟳{X}  {DM}{msg}...{X}", end='\r')

# ================================================================
# CONFIG & DATABASE
# ================================================================

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

def setup_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT, mode TEXT, anon_level INTEGER,
        risk_score INTEGER, open_ports TEXT,
        cves_found TEXT, timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def save_scan(target, mode, anon_level, risk, ports, cves):
    setup_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO scans VALUES (NULL,?,?,?,?,?,?,?)",
              (target, mode, anon_level, risk,
               json.dumps(ports), json.dumps(cves),
               datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def show_history():
    setup_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()

    banner()
    sec("Scan History — Last 20 Scans", "📋")
    if not rows:
        log("-", "No scan history found")
        return

    print(f"  {BD}{W}{'ID':<5} {'Target':<30} {'Mode':<10} {'Anon':<6} {'Risk':<8} {'Date'}{X}")
    print(f"  {'─'*60}")
    for row in rows:
        rid, target, mode, anon, risk, ports, cves, ts = row
        risk_col = R if risk >= 60 else Y if risk >= 30 else G
        print(f"  {DM}{rid:<5}{X} {C}{target:<30}{X} {Y}{mode:<10}{X} {M}L{anon:<5}{X} {risk_col}{risk:<8}{X} {DM}{ts}{X}")

# ================================================================
# SETUP — API KEY
# ================================================================

def first_run_setup():
    cfg = load_config()
    if 'shodan_key' not in cfg:
        banner()
        sec("First Time Setup — ZENVORA", "⚙️")
        print(f"  {Y}Shodan API key chahiye hai enhanced scanning ke liye.{X}")
        print(f"  {DM}Free key: https://shodan.io → Register → My Account{X}\n")
        key = input(f"  {C}Shodan API Key (skip ke liye Enter dabaao): {X}").strip()
        cfg['shodan_key'] = key if key else None
        save_config(cfg)
        log("+", "Config saved!" if key else "Skipped — Shodan features disabled")
        time.sleep(1)
    return cfg

# ================================================================
# ANONYMITY ENGINE
# ================================================================

def check_anonymity(anon_level, target_waf=None):
    sec("Anonymity Engine — ZENVORA", "🔒")

    if anon_level == 0:
        log("*", "Anonymity: DISABLED — Raw connection")
        return False

    # Level indicators
    levels = {
        1: ("BASIC",    Y, "Fake User-Agent + Random Delays"),
        2: ("MEDIUM",   M, "ProxyChains + Fake UA + Delays"),
        3: ("MAXIMUM",  G, "Tor + ProxyChains + Fake UA + Delays"),
    }

    label, col, desc = levels[anon_level]
    log("+", f"Anonymity Level: {col}{BD}{label}{X} — {desc}")

    # Check Tor — Auto Start
    if anon_level == 3:
        log("*", "Starting Tor automatically...")
        run("sudo service tor start 2>/dev/null")
        time.sleep(3)
        tor_check = run("curl --socks5 127.0.0.1:9050 --max-time 8 https://check.torproject.org/api/ip 2>/dev/null", timeout=12)
        if "true" in tor_check.lower():
            log("+", f"{G}Tor: ACTIVE — Auto started ✓{X}")
        else:
            port_check = run("ss -tlnp | grep 9050")
            if port_check:
                log("+", f"{G}Tor: RUNNING on port 9050 ✓{X}")
            else:
                log("!", f"{Y}Tor: Could not start — Falling back to Level 2{X}")
                anon_level = 2

    # Check ProxyChains
    if anon_level >= 2:
        proxy_check = run("which proxychains4 2>/dev/null")
        if proxy_check:
            log("+", f"{G}ProxyChains: Available ✓{X}")
        else:
            log("!", f"{Y}ProxyChains not found — install: sudo apt install proxychains4{X}")
            anon_level = 1

    # Safety percentage
    safety = calculate_safety(anon_level, target_waf)
    print()
    print(f"  {BD}{'─'*50}{X}")
    print_safety_bar(safety, anon_level, target_waf)
    print(f"  {BD}{'─'*50}{X}")

    return anon_level

def calculate_safety(anon_level, waf=None):
    base = {0: 10, 1: 45, 2: 65, 3: 82}
    score = base.get(anon_level, 10)

    if waf:
        waf_lower = waf.lower()
        if 'cloudflare' in waf_lower:   score -= 15
        elif 'akamai' in waf_lower:     score -= 12
        elif 'aws' in waf_lower:        score -= 10
        else:                           score -= 5
    else:
        score += 8

    return min(max(score, 5), 95)

def print_safety_bar(pct, anon_level, waf):
    filled = int(pct / 5)
    bar = "█" * filled + "░" * (20 - filled)
    col = R if pct < 40 else Y if pct < 65 else G

    print(f"\n  {BD}  Safety Score:{X}")
    print(f"  {col}  [{bar}] {pct}%{X}")
    print()

    if anon_level == 0:
        print(f"  {R}  ⚠  No anonymity — Your real IP is exposed{X}")
        print(f"  {R}  ⚠  Server logs will capture your identity{X}")
    elif anon_level == 1:
        print(f"  {Y}  ◉  Basic protection only{X}")
        print(f"  {Y}  ◉  IP still visible — only behavior masked{X}")
    elif anon_level == 2:
        print(f"  {M}  ◉  Medium protection — proxy IP shown{X}")
        print(f"  {M}  ◉  Proxy provider can see your traffic{X}")
    elif anon_level == 3:
        print(f"  {G}  ◉  High protection — Tor exit node shown{X}")
        print(f"  {G}  ◉  Timing attacks still possible{X}")

    if waf:
        print(f"\n  {R}  ⚠  WAF Detected: {waf}{X}")
        print(f"  {R}  ⚠  Safety reduced — WAF logs all requests{X}")

    print(f"\n  {DM}  Note: 100% anonymity is impossible.{X}")
    print(f"  {DM}  Always use on authorized targets only.{X}")

# ================================================================
# SCAN MODULES
# ================================================================

def scan_whois(target, anon_level):
    progress("Running WHOIS lookup")
    stealth_delay(anon_level)
    raw = run(f"whois {target} 2>/dev/null")
    results = {}
    important = ['Registrar:', 'Creation Date:', 'Registry Expiry Date:',
                 'Name Server:', 'Registrar Abuse Contact Email:', 'Updated Date:']
    for line in raw.splitlines():
        for field in important:
            if field.lower() in line.lower() and field not in results:
                results[field.rstrip(':')] = line.split(':', 1)[-1].strip()
    for k, v in results.items():
        log("+", f"{k}: {C}{v}{X}")
    return raw, results

def scan_dns(target, anon_level):
    progress("Enumerating DNS records")
    stealth_delay(anon_level)
    results = {}

    # Get IPv4 only — filter out IPv6
    ip_out = run(f"dig {target} A +short 2>/dev/null | grep -E '^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$' | head -1")
    if not ip_out.strip():
        ip_out = run(f"nslookup {target} 2>/dev/null | grep -E 'Address.*[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+' | tail -1")
        ip = ip_out.split(':')[-1].strip() if ip_out else "Unknown"
    else:
        ip = ip_out.strip()
    results['IP'] = ip
    log("+", f"IP Address: {C}{ip}{X}")

    for record in ['A', 'MX', 'NS', 'TXT']:
        stealth_delay(anon_level)
        out = run(f"dig {target} {record} +short 2>/dev/null")
        if out.strip():
            results[record] = out.strip()
            log("+", f"{record} Record: {C}{out.strip()[:70]}{X}")

    return results

def scan_ports(target, mode, anon_level):
    progress("Scanning ports")
    open_ports = []

    if mode == 'quick':
        port_range = "21,22,23,25,53,80,443,445,3306,3389,8080,8443"
        speed = "-T4"
    elif mode == 'stealth':
        port_range = "21,22,23,25,53,80,443,445,3306,3389,8080,8443"
        speed = "-T1"
    else:
        port_range = "1-65535"
        speed = "-T4"

    use_proxy = anon_level >= 2
    out = run(f"nmap -sV {speed} -p {port_range} {target} 2>/dev/null", timeout=180, use_proxy=use_proxy)

    for line in out.splitlines():
        if '/tcp' in line and 'open' in line:
            parts = line.split()
            port    = parts[0]
            service = parts[2] if len(parts) > 2 else ''
            version = ' '.join(parts[3:]) if len(parts) > 3 else ''
            open_ports.append({'port': port, 'service': service, 'version': version})
            log("+", f"Port {C}{port}{X} — {Y}{service}{X} {DM}{version}{X}")

    stealth_delay(anon_level)
    os_out = run(f"nmap -O {target} 2>/dev/null | grep -E 'Running:|OS details:|Device type:'")
    os_info = os_out.strip() if os_out else "Unknown"
    if os_info and os_info != "Unknown":
        for line in os_info.splitlines():
            log("+", f"OS: {Y}{line.strip()}{X}")

    return open_ports, os_info

def scan_waf(target, anon_level):
    progress("Detecting WAF")
    stealth_delay(anon_level)
    url = f"http://{target}" if not target.startswith('http') else target
    out = run(f"wafw00f {url} 2>/dev/null")
    waf = None
    for line in out.splitlines():
        if 'is behind' in line.lower():
            waf = line.strip()
            log("!", f"{R}WAF Detected: {waf}{X}")
        elif 'no waf' in line.lower():
            log("+", f"{G}No WAF detected — direct access possible{X}")
    return waf

def scan_subdomains(target, anon_level):
    progress("Finding subdomains")
    stealth_delay(anon_level)
    found = []

    # DNSenum
    out = run(f"dnsenum {target} 2>/dev/null | grep -E '^[a-zA-Z0-9].*\\.{target}'", timeout=60)
    for line in out.splitlines():
        if target in line and line.strip():
            sub = line.strip().split()[0]
            if sub not in found:
                found.append(sub)
                log("+", f"Subdomain: {C}{sub}{X}")

    # Get main IP to detect wildcards
    main_ip = run(f"dig {target} A +short 2>/dev/null | grep -E '^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$' | head -1").strip()

    # Brute common subdomains
    common = ['www','mail','admin','dev','test','api','ftp','vpn','blog','shop',
              'portal','staging','beta','app','secure','login','dashboard']
    for sub in common:
        stealth_delay(anon_level)
        sub_ip = run(f"dig {sub}.{target} A +short 2>/dev/null | grep -E '^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$' | head -1").strip()
        # Skip if same IP as main domain (wildcard) or empty
        if sub_ip and sub_ip != main_ip and 'NXDOMAIN' not in sub_ip:
            full = f"{sub}.{target}"
            if full not in found:
                found.append(full)
                log("+", f"Subdomain: {C}{full}{X} → {sub_ip}")

    if not found:
        log("-", "No real subdomains found (wildcard DNS may be active)")
    return found

def scan_emails(target, anon_level):
    progress("Harvesting emails")
    stealth_delay(anon_level)
    out = run(f"theHarvester -d {target} -b google,bing,yahoo -l 100 2>/dev/null | grep '@'", timeout=60)
    emails = []
    for line in out.splitlines():
        if '@' in line and target in line:
            email = line.strip()
            if email not in emails:
                emails.append(email)
                log("+", f"Email: {C}{email}{X}")
    if not emails:
        log("-", "No emails found (theHarvester may not be installed)")
    return emails

def scan_dirs(target, anon_level, mode):
    progress("Brute forcing directories")
    url = f"http://{target}" if not target.startswith('http') else target
    wordlist = "/usr/share/wordlists/dirb/common.txt"

    if not os.path.exists(wordlist):
        log("-", "Wordlist not found")
        return []

    ua = get_random_ua() if anon_level >= 1 else "gobuster/3.8"
    threads = "5" if mode == 'stealth' else "20"

    out = run(f'gobuster dir -u {url} -w {wordlist} -t {threads} --timeout 10s -a "{ua}" 2>/dev/null', timeout=180)
    found = []
    for line in out.splitlines():
        if '(Status:' in line:
            status = line.split('Status:')[1].split(')')[0].strip()
            path = line.split()[0]
            if status in ['200','301','302','403']:
                found.append({'path': path, 'status': status})
                emoji = "✅" if status == '200' else "⚠️ " if status == '403' else "↪️ "
                log("+", f"{emoji} {C}{path}{X} [{Y}{status}{X}]")
    return found

def scan_ssl(target, anon_level):
    progress("Analyzing SSL certificate")
    stealth_delay(anon_level)
    out = run(f"echo | openssl s_client -connect {target}:443 2>/dev/null | openssl x509 -noout -text 2>/dev/null | grep -E 'Subject:|Issuer:|Not Before:|Not After:|DNS:'")
    if out:
        for line in out.splitlines():
            if line.strip():
                log("+", f"SSL: {DM}{line.strip()}{X}")
    else:
        log("-", "SSL not available or port 443 closed")
    return out

def scan_shodan(target, api_key, anon_level):
    if not api_key:
        log("-", "Shodan API key not set — skipping")
        return {}
    progress("Querying Shodan")
    stealth_delay(anon_level)

    ip_out = run(f"nslookup {target} 2>/dev/null | grep 'Address' | tail -1")
    ip = ip_out.split(':')[-1].strip()

    out = run(f"curl -s 'https://api.shodan.io/shodan/host/{ip}?key={api_key}' 2>/dev/null", timeout=15)
    try:
        data = json.loads(out)
        if 'error' not in data:
            log("+", f"Shodan OS: {C}{data.get('os','Unknown')}{X}")
            log("+", f"Shodan Ports: {C}{data.get('ports','N/A')}{X}")
            log("+", f"Shodan Org: {C}{data.get('org','Unknown')}{X}")
            log("+", f"Shodan Country: {C}{data.get('country_name','Unknown')}{X}")
            return data
        else:
            log("-", f"Shodan: {data.get('error','Unknown error')}")
    except:
        log("-", "Could not parse Shodan response")
    return {}

def check_cves(open_ports):
    found_cves = []
    for port in open_ports:
        version_str = f"{port['service']} {port['version']}".lower()
        for pattern, cves in CVE_DB.items():
            if pattern.lower() in version_str:
                for cve in cves:
                    severity = R+"CRITICAL"+X if 'CRITICAL' in cve else Y+"HIGH"+X
                    log("!", f"CVE Found: {severity} — {cve} ({port['port']})")
                    found_cves.append({'port': port['port'], 'cve': cve})
    if not found_cves:
        log("+", "No known CVEs matched in database")
    return found_cves

def scan_web_vulns(target, anon_level):
    progress("Checking web security headers")
    url = f"http://{target}" if not target.startswith('http') else target
    ua = get_random_ua() if anon_level >= 1 else "curl/7.0"

    out = run(f'curl -sI -A "{ua}" {url} 2>/dev/null')
    issues = []
    security_headers = [
        "X-Frame-Options", "X-XSS-Protection",
        "X-Content-Type-Options", "Content-Security-Policy",
        "Strict-Transport-Security", "Referrer-Policy"
    ]
    for header in security_headers:
        if header.lower() in out.lower():
            log("+", f"{G}Header present: {header}{X}")
        else:
            log("!", f"{Y}Missing header: {header}{X}")
            issues.append(f"Missing {header}")

    # Server info leak
    for line in out.splitlines():
        if line.lower().startswith('server:'):
            log("!", f"{Y}Server info exposed: {line.strip()}{X}")
            issues.append(f"Server info leak: {line.strip()}")

    return issues

# ================================================================
# RISK SCORE ENGINE
# ================================================================

def calculate_risk(open_ports, cves, waf, dirs, anon_level):
    score = 0

    # Ports
    risky_ports = {'21': 15, '23': 20, '445': 20, '3389': 15,
                   '3306': 15, '80': 5, '443': 3, '22': 8}
    for p in open_ports:
        port_num = p['port'].split('/')[0]
        score += risky_ports.get(port_num, 3)

    # CVEs
    for cve in cves:
        score += 20 if 'CRITICAL' in cve['cve'] else 12

    # No WAF
    if not waf:
        score += 10

    # Interesting dirs
    for d in dirs:
        if d['status'] == '200':
            score += 5
        if d['status'] == '403':
            score += 2

    score = min(score, 100)

    # Display
    if score >= 70:
        col, label = R, "CRITICAL"
    elif score >= 50:
        col, label = R, "HIGH"
    elif score >= 30:
        col, label = Y, "MEDIUM"
    else:
        col, label = G, "LOW"

    filled = int(score / 5)
    bar = "█" * filled + "░" * (20 - filled)

    print(f"\n  {BD}  Hackability Score:{X}")
    print(f"  {col}  [{bar}] {score}/100 — {label}{X}\n")

    return score

# ================================================================
# ATTACK SUGGESTIONS
# ================================================================

def suggest_attacks(target, open_ports, waf, dirs, cves, anon_level):
    attacks = []
    avoid   = []
    port_nums = [p['port'].split('/')[0] for p in open_ports]

    # Port based
    if '21' in port_nums:
        attacks.append(("FTP Anonymous Login", f"ftp {target}", "MEDIUM"))
        attacks.append(("FTP Brute Force", f"hydra -l admin -P /usr/share/wordlists/rockyou.txt ftp://{target}", "MEDIUM"))
    if '22' in port_nums:
        attacks.append(("SSH Brute Force", f"hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://{target}", "MEDIUM"))
    if '23' in port_nums:
        attacks.append(("Telnet Access", f"telnet {target}", "HIGH"))
    if '80' in port_nums or '443' in port_nums or '8080' in port_nums:
        attacks.append(("Full Vuln Scan", f"nmap --script vuln {target}", "HIGH"))
        attacks.append(("SQL Injection", f"sqlmap -u http://{target} --dbs --random-agent", "HIGH"))
        attacks.append(("XSS Test", "Inject <script>alert(1)</script> in all input fields", "MEDIUM"))
        attacks.append(("Nikto Scan", f"nikto -h http://{target}", "MEDIUM"))
    if '445' in port_nums:
        attacks.append(("SMB Enum", f"smbclient -L //{target}", "HIGH"))
        attacks.append(("EternalBlue", f"nmap --script smb-vuln-ms17-010 {target}", "CRITICAL"))
    if '3306' in port_nums:
        attacks.append(("MySQL Brute", f"hydra -l root -P /usr/share/wordlists/rockyou.txt mysql://{target}", "HIGH"))
    if '3389' in port_nums:
        attacks.append(("RDP Brute", f"hydra -l administrator -P /usr/share/wordlists/rockyou.txt rdp://{target}", "MEDIUM"))

    # CVE based
    for cve in cves:
        attacks.append((f"Exploit {cve['cve']}", f"searchsploit {cve['cve'].split()[0]}", "CRITICAL"))

    # Dir based
    for d in dirs:
        if d['status'] == '403':
            attacks.append((f"403 Bypass {d['path']}", f"Try headers: X-Original-URL: {d['path']}", "LOW"))

    # WAF
    if waf:
        avoid.append(f"Direct automated scans — {waf} will block and log")
        avoid.append("SQLmap without tamper scripts — will be blocked")
        avoid.append("Nikto without WAF bypass — noisy, gets blocked")
        attacks.append(("WAF Bypass", "Use: sqlmap --tamper=space2comment,between", "HIGH"))
    else:
        attacks.append(("Full Auto Scan", f"nmap -A -p- --script vuln {target}", "HIGH"))

    avoid.append("DDoS — noisy, illegal, ruins the target")
    avoid.append("File deletion or modification")
    avoid.append("Uploading malware to production")

    # Print
    print(f"\n  {BD}{G}✅  RECOMMENDED ATTACKS:{X}\n")
    for name, cmd, sev in attacks:
        col = R if sev == 'CRITICAL' else Y if sev == 'HIGH' else C
        print(f"  {col}[{sev}]{X} {BD}{name}{X}")
        print(f"        {DM}→ {cmd}{X}\n")

    print(f"\n  {BD}{R}❌  AVOID THESE:{X}\n")
    for a in avoid:
        print(f"  {R}✗{X} {a}")

    return attacks, avoid

# ================================================================
# REPORT GENERATOR
# ================================================================

def generate_report(target, mode, anon_level, safety, whois_r, dns_r,
                    open_ports, os_info, waf, dirs, subdomains, emails,
                    cves, web_issues, risk_score, attacks, avoid):

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Save reports in 'reports' folder next to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_name = f"zenvora_{target.replace('.','_').replace('http://','').replace('https://','').replace('/','_')}_{ts}"
    fname = os.path.join(script_dir, base_name + ".txt")

    L = []
    def a(t=""): L.append(t)

    a("═"*65)
    a("  ██████╗ ███████╗ ██████╗ ██████╗ ███╗  ██╗")
    a("  ╚════██╗██╔════╝██╔═══██╗██╔══██╗████╗ ██║")
    a("   █████╔╝█████╗  ██║   ██║██████╔╝██╔██╗██║")
    a("   ╚═══██╗██╔══╝  ██║   ██║██╔══██╗██║╚████║")
    a("  ██████╔╝███████╗╚██████╔╝██║  ██║██║ ╚███║")
    a("  ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚══╝")
    a("═"*65)
    a(f"  TARGET     : {target}")
    a(f"  MODE       : {mode.upper()}")
    a(f"  ANONYMITY  : Level {anon_level} | Safety: {safety}%")
    a(f"  RISK SCORE : {risk_score}/100")
    a(f"  DATE       : {datetime.now().strftime('%d %B %Y, %H:%M')}")
    a(f"  REPORT ID  : ZENV-{ts}")
    a("═"*65)
    a()

    # WHOIS
    a("─"*65)
    a("  [1] WHO OWNS THIS TARGET?")
    a("─"*65)
    _, parsed = whois_r
    for k,v in (parsed or {}).items():
        a(f"  {k}: {v}")
    a()

    # DNS
    a("─"*65)
    a("  [2] DNS INFORMATION")
    a("─"*65)
    for k,v in (dns_r or {}).items():
        a(f"  {k}: {v}")
    a()

    # Subdomains
    a("─"*65)
    a("  [3] SUBDOMAINS FOUND")
    a("─"*65)
    if subdomains:
        for s in subdomains:
            a(f"  → {s}")
    else:
        a("  None found")
    a()

    # Emails
    a("─"*65)
    a("  [4] EMAILS HARVESTED")
    a("─"*65)
    if emails:
        for e in emails:
            a(f"  → {e}")
    else:
        a("  None found")
    a()

    # Ports
    a("─"*65)
    a("  [5] OPEN PORTS & SERVICES")
    a("─"*65)
    a(f"  Total open: {len(open_ports)}")
    a()
    for p in open_ports:
        a(f"  PORT    : {p['port']}")
        a(f"  Service : {p['service']} {p['version']}")
        a()
    a(f"  OS      : {os_info}")
    a()

    # CVEs
    a("─"*65)
    a("  [6] CVEs FOUND")
    a("─"*65)
    if cves:
        for c in cves:
            a(f"  !! {c['cve']} on port {c['port']}")
    else:
        a("  No known CVEs matched")
    a()

    # WAF
    a("─"*65)
    a("  [7] WAF / FIREWALL")
    a("─"*65)
    a(f"  Status : {'DETECTED — ' + waf if waf else 'NOT DETECTED'}")
    a(f"  Impact : {'Direct attacks blocked' if waf else 'Direct attacks possible'}")
    a()

    # Directories
    a("─"*65)
    a("  [8] HIDDEN DIRECTORIES")
    a("─"*65)
    if dirs:
        for d in dirs:
            status_text = "OPEN" if d['status']=='200' else "FORBIDDEN" if d['status']=='403' else "REDIRECTS"
            a(f"  {d['path']} — {status_text}")
    else:
        a("  None found")
    a()

    # Web issues
    a("─"*65)
    a("  [9] WEB SECURITY ISSUES")
    a("─"*65)
    if web_issues:
        for i in web_issues:
            a(f"  ⚠  {i}")
    else:
        a("  No major issues found")
    a()

    # Anonymity
    a("─"*65)
    a("  [10] ANONYMITY STATUS")
    a("─"*65)
    anon_labels = {0:"NONE",1:"BASIC",2:"MEDIUM",3:"MAXIMUM"}
    a(f"  Level   : {anon_level} — {anon_labels.get(anon_level,'NONE')}")
    a(f"  Safety  : {safety}%")
    if waf:
        a(f"  Warning : WAF detected — safety reduced")
    a()

    # Attacks
    a("─"*65)
    a("  [11] RECOMMENDED ATTACKS")
    a("─"*65)
    if attacks:
        for i,(name,cmd,sev) in enumerate(attacks,1):
            a(f"  [{i}] {name} [{sev}]")
            a(f"      {cmd}")
            a()
    else:
        a("  N/A — Passive OSINT mode (no active attacks suggested)")
    a()

    # Avoid
    a("─"*65)
    a("  [12] WHAT NOT TO DO")
    a("─"*65)
    if avoid:
        for av in avoid:
            a(f"  ✗ {av}")
    else:
        a("  OSINT mode — No active attacks performed")
        a("  ✗ Do not run active scans without authorization")
        a("  ✗ Do not use this data for illegal purposes")
    a()

    # Footer
    a("═"*65)
    a("  ZENVORA RECON TOOL v3.0")
    a("  Empire: ZENVORA  |  Built by: Zenomro")
    a("  Use only on authorized targets.")
    a("═"*65)

    with open(fname,'w') as f:
        f.write('\n'.join(L))

    # JSON export
    json_fname = os.path.join(script_dir, base_name + ".json")
    json_data = {
        "target": target, "mode": mode, "anon_level": anon_level,
        "safety_pct": safety, "risk_score": risk_score,
        "open_ports": open_ports, "cves": cves, "waf": waf,
        "subdomains": subdomains, "emails": emails,
        "directories": dirs, "timestamp": datetime.now().isoformat()
    }
    with open(json_fname,'w') as f:
        json.dump(json_data, f, indent=2)

    return fname, json_fname

# ================================================================
# SCAN ORCHESTRATORS
# ================================================================

def run_quick(target, anon_level, cfg):
    sec("Quick Scan Mode", "⚡")
    waf_pre    = scan_waf(target, 0)
    safety     = calculate_safety(anon_level, waf_pre)
    anon_level = check_anonymity(anon_level, waf_pre)

    sec("WHOIS",    "🌐"); whois_r   = scan_whois(target, anon_level)
    sec("DNS",      "🔎"); dns_r     = scan_dns(target, anon_level)
    sec("Ports",    "⚡"); ports, os = scan_ports(target, 'quick', anon_level)
    sec("CVE Check","🔬"); cves      = check_cves(ports)

    risk = calculate_risk(ports, cves, waf_pre, [], anon_level)
    sec("Attack Suggestions","⚔️")
    attacks, avoid = suggest_attacks(target, ports, waf_pre, [], cves, anon_level)

    sec("Saving Report","📄")
    f, j = generate_report(target,'quick',anon_level,safety,
                           whois_r,dns_r,ports,os,waf_pre,[],[],[],cves,[],risk,attacks,avoid)
    save_scan(target,'quick',anon_level,risk,[p['port'] for p in ports],[c['cve'] for c in cves])
    log("+", f"TXT Report: {C}{f}{X}")
    log("+", f"JSON Report: {C}{j}{X}")

def run_full(target, anon_level, cfg):
    sec("Full Scan Mode — All Systems Go", "🔥")
    waf_pre    = scan_waf(target, 0)
    safety     = calculate_safety(anon_level, waf_pre)
    anon_level = check_anonymity(anon_level, waf_pre)

    sec("WHOIS",       "🌐"); whois_r    = scan_whois(target, anon_level)
    sec("DNS",         "🔎"); dns_r      = scan_dns(target, anon_level)
    sec("Subdomains",  "🌍"); subs       = scan_subdomains(target, anon_level)
    sec("Emails",      "📧"); emails     = scan_emails(target, anon_level)
    sec("Ports",       "⚡"); ports, os  = scan_ports(target, 'full', anon_level)
    sec("SSL",         "🔐"); ssl        = scan_ssl(target, anon_level)
    sec("Directories", "📁"); dirs       = scan_dirs(target, anon_level, 'full')
    sec("Web Headers", "🌐"); web_issues = scan_web_vulns(target, anon_level)
    sec("Shodan",      "🛰️"); shodan_r   = scan_shodan(target, cfg.get('shodan_key'), anon_level)
    sec("CVE Check",   "🔬"); cves       = check_cves(ports)

    sec("Risk Score","📊")
    risk = calculate_risk(ports, cves, waf_pre, dirs, anon_level)
    sec("Attack Suggestions","⚔️")
    attacks, avoid = suggest_attacks(target, ports, waf_pre, dirs, cves, anon_level)

    sec("Saving Report","📄")
    f, j = generate_report(target,'full',anon_level,safety,
                           whois_r,dns_r,ports,os,waf_pre,dirs,subs,emails,cves,web_issues,risk,attacks,avoid)
    save_scan(target,'full',anon_level,risk,[p['port'] for p in ports],[c['cve'] for c in cves])
    log("+", f"TXT Report: {C}{f}{X}")
    log("+", f"JSON Report: {C}{j}{X}")

def run_stealth(target, anon_level, cfg):
    if anon_level == 0:
        anon_level = 2
        log("*", f"Stealth mode — auto setting anonymity to Level 2")
    sec("Stealth Scan Mode — Silent & Slow", "🥷")
    waf_pre    = scan_waf(target, 0)
    safety     = calculate_safety(anon_level, waf_pre)
    anon_level = check_anonymity(anon_level, waf_pre)

    sec("WHOIS",      "🌐"); whois_r   = scan_whois(target, anon_level)
    sec("DNS",        "🔎"); dns_r     = scan_dns(target, anon_level)
    sec("Subdomains", "🌍"); subs      = scan_subdomains(target, anon_level)
    sec("Ports",      "⚡"); ports, os = scan_ports(target, 'stealth', anon_level)
    sec("CVE Check",  "🔬"); cves      = check_cves(ports)

    sec("Risk Score","📊")
    risk = calculate_risk(ports, cves, waf_pre, [], anon_level)
    sec("Attack Suggestions","⚔️")
    attacks, avoid = suggest_attacks(target, ports, waf_pre, [], cves, anon_level)

    sec("Saving Report","📄")
    f, j = generate_report(target,'stealth',anon_level,safety,
                           whois_r,dns_r,ports,os,waf_pre,[],subs,[],cves,[],risk,attacks,avoid)
    save_scan(target,'stealth',anon_level,risk,[p['port'] for p in ports],[c['cve'] for c in cves])
    log("+", f"TXT Report: {C}{f}{X}")
    log("+", f"JSON Report: {C}{j}{X}")

def run_web(target, anon_level, cfg):
    sec("Web Scan Mode — Application Focus", "🌐")
    waf_pre    = scan_waf(target, 0)
    safety     = calculate_safety(anon_level, waf_pre)
    anon_level = check_anonymity(anon_level, waf_pre)

    sec("DNS",         "🔎"); dns_r      = scan_dns(target, anon_level)
    sec("Directories", "📁"); dirs       = scan_dirs(target, anon_level, 'web')
    sec("Web Headers", "🌐"); web_issues = scan_web_vulns(target, anon_level)
    sec("SSL",         "🔐"); ssl        = scan_ssl(target, anon_level)
    sec("Ports",       "⚡"); ports, os  = scan_ports(target, 'quick', anon_level)
    sec("CVE Check",   "🔬"); cves       = check_cves(ports)

    sec("Risk Score","📊")
    risk = calculate_risk(ports, cves, waf_pre, dirs, anon_level)
    sec("Attack Suggestions","⚔️")
    attacks, avoid = suggest_attacks(target, ports, waf_pre, dirs, cves, anon_level)

    sec("Saving Report","📄")
    f, j = generate_report(target,'web',anon_level,safety,
                           ({},{}),dns_r,ports,os,waf_pre,dirs,[],[],cves,web_issues,risk,attacks,avoid)
    save_scan(target,'web',anon_level,risk,[p['port'] for p in ports],[c['cve'] for c in cves])
    log("+", f"TXT Report: {C}{f}{X}")
    log("+", f"JSON Report: {C}{j}{X}")

def run_osint(target, anon_level, cfg):
    sec("OSINT Mode — Passive Recon Only", "👁️")
    log("*", "No active scanning — 100% passive")
    anon_level = check_anonymity(anon_level, None)

    sec("WHOIS",      "🌐"); whois_r = scan_whois(target, anon_level)
    sec("DNS",        "🔎"); dns_r   = scan_dns(target, anon_level)
    sec("Subdomains", "🌍"); subs    = scan_subdomains(target, anon_level)
    sec("Emails",     "📧"); emails  = scan_emails(target, anon_level)
    sec("Shodan",     "🛰️"); shodan  = scan_shodan(target, cfg.get('shodan_key'), anon_level)
    sec("SSL",        "🔐"); ssl     = scan_ssl(target, anon_level)

    safety = calculate_safety(anon_level, None)

    sec("Google Dorks — Use These Manually","🔍")
    dorks = [
        f'site:{target} filetype:pdf',
        f'site:{target} filetype:sql',
        f'site:{target} inurl:admin',
        f'site:{target} inurl:login',
        f'site:{target} intext:password',
        f'site:{target} inurl:config',
    ]
    for d in dorks:
        log("+", f"{C}{d}{X}")

    sec("Saving Report","📄")
    f, j = generate_report(target,'osint',anon_level,safety,
                           whois_r,dns_r,[],'-',None,[],subs,emails,[],[],0,[],[])
    log("+", f"TXT Report: {C}{f}{X}")
    log("+", f"JSON Report: {C}{j}{X}")

# ================================================================
# HELP
# ================================================================

def show_help():
    banner()
    print(f"""
  {BD}{W}USAGE:{X}
    python3 recon.py -m <mode> [--anon <level>] <target>

  {BD}{W}MODES:{X}
    {C}quick{X}    Fast scan — ports, services, CVEs          (~3 min)
    {C}full{X}     Complete scan — everything                 (~20 min)
    {C}stealth{X}  Slow & quiet — minimal footprint           (~30 min)
    {C}web{X}      Web app focused — dirs, headers, SSL       (~8 min)
    {C}osint{X}    Passive only — no active scanning          (~5 min)

  {BD}{W}ANONYMITY:{X}
    {Y}--anon 0{X}  No anonymity (default)
    {Y}--anon 1{X}  Fake User-Agent + Random delays
    {Y}--anon 2{X}  ProxyChains + Fake UA + Delays
    {Y}--anon 3{X}  Tor + ProxyChains + Fake UA + Delays

  {BD}{W}EXAMPLES:{X}
    {DM}python3 recon.py -m quick scanme.nmap.org{X}
    {DM}python3 recon.py -m full --anon 2 target.com{X}
    {DM}python3 recon.py -m stealth --anon 3 target.com{X}
    {DM}python3 recon.py -m web --anon 1 target.com{X}
    {DM}python3 recon.py -m osint target.com{X}

  {BD}{W}OTHER COMMANDS:{X}
    {DM}python3 recon.py --history{X}       View scan history
    {DM}python3 recon.py --setup{X}         Reconfigure API keys
    {DM}python3 recon.py --help{X}          Show this help

  {BD}{R}WARNING: Use only on authorized targets!{X}
  {DM}Empire: ZENVORA | Tool by: Zenomro{X}
""")

# ================================================================
# MAIN
# ================================================================

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-m', '--mode',    default='quick')
    parser.add_argument('--anon',          type=int, default=0)
    parser.add_argument('--history',       action='store_true')
    parser.add_argument('--setup',         action='store_true')
    parser.add_argument('--help','-h',     action='store_true')
    parser.add_argument('target',          nargs='?', default=None)
    args = parser.parse_args()

    if args.help or len(sys.argv) == 1:
        show_help()
        return

    if args.history:
        show_history()
        return

    cfg = first_run_setup()

    if args.setup:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        first_run_setup()
        return

    if not args.target:
        show_help()
        return

    target = args.target.replace('http://','').replace('https://','').rstrip('/')
    mode   = args.mode.lower()
    anon   = args.anon

    banner()
    print(f"\n  {G}Target   : {BD}{W}{target}{X}")
    print(f"  {G}Mode     : {BD}{Y}{mode.upper()}{X}")
    print(f"  {G}Anonymity: {BD}{M}Level {anon}{X}")
    print(f"  {DM}  Starting ZENVORA Recon Engine...{X}\n")
    time.sleep(1)

    modes = {
        'quick':   run_quick,
        'full':    run_full,
        'stealth': run_stealth,
        'web':     run_web,
        'osint':   run_osint,
    }

    if mode not in modes:
        log("-", f"Unknown mode: {mode}")
        show_help()
        return

    modes[mode](target, anon, cfg)

    # Auto stop Tor if it was started
    if anon == 3:
        log("*", "Stopping Tor...")
        run("sudo service tor stop 2>/dev/null")
        log("+", f"{G}Tor stopped ✓{X}")

    print(f"\n  {C}{'━'*62}{X}")
    print(f"  {BD}{W}  ZENVORA Recon Complete.{X}")
    print(f"  {DM}  Empire: ZENVORA  |  Built by: Zenomro{X}")
    print(f"  {C}{'━'*62}{X}\n")

if __name__ == "__main__":
    main()
