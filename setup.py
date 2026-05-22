#!/usr/bin/env python3

# ================================================================
#   ZENVORA SETUP v1.0
#   Empire: ZENVORA | By: Zenomro
#   Ek command mein poora tool ready
# ================================================================

import subprocess, sys, os, json, time

R  = '\033[91m'
G  = '\033[92m'
Y  = '\033[93m'
C  = '\033[96m'
W  = '\033[97m'
X  = '\033[0m'
BD = '\033[1m'
DM = '\033[2m'

CONFIG_FILE = os.path.expanduser("~/.zenvora_config.json")

def banner():
    os.system('clear')
    print(f"""
{R}╔══════════════════════════════════════════════════════╗
║                                                      ║
║   ███████╗███████╗████████╗██╗   ██╗██████╗          ║
║   ╚══███╔╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗         ║
║     ███╔╝ █████╗     ██║   ██║   ██║██████╔╝         ║
║    ███╔╝  ██╔══╝     ██║   ██║   ██║██╔═══╝          ║
║   ███████╗███████╗   ██║   ╚██████╔╝██║              ║
║   ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝              ║
║                                                      ║{X}
{C}║   SETUP v1.0  ·  Empire: ZENVORA  ·  By: Zenomro    ║{X}
{R}╚══════════════════════════════════════════════════════╝{X}
""")

def log(level, msg):
    icons = {"+":(G,"[+]"), "*":(Y,"[*]"), "-":(R,"[-]"), "!":(C,"[!]")}
    col, icon = icons.get(level, (W,"[?]"))
    print(f"  {col}{BD}{icon}{X} {msg}")

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def check_root():
    if os.geteuid() != 0:
        log("-", f"{R}Root access chahiye — sudo se run karo:{X}")
        print(f"\n  {Y}sudo python3 setup.py{X}\n")
        sys.exit(1)

def install_tools():
    print(f"\n  {BD}{W}[1/4] System Tools Install Ho Rahe Hain...{X}\n")

    tools = [
        ("nmap",          "nmap"),
        ("gobuster",      "gobuster"),
        ("wafw00f",       "wafw00f"),
        ("dnsenum",       "dnsenum"),
        ("theharvester",  "theharvester"),
        ("proxychains4",  "proxychains4"),
        ("tor",           "tor"),
        ("hydra",         "hydra"),
        ("sqlmap",        "sqlmap"),
        ("nikto",         "nikto"),
        ("openssl",       "openssl"),
        ("curl",          "curl"),
        ("dig",           "dnsutils"),
        ("masscan",       "masscan"),
        ("whatweb",       "whatweb"),
    ]

    log("*", "Updating package list...")
    run("apt update -qq 2>/dev/null")

    failed = []
    for tool_name, pkg in tools:
        # Check if already installed
        check = subprocess.run(f"which {tool_name} 2>/dev/null",
                               shell=True, capture_output=True, text=True)
        if check.stdout.strip():
            log("+", f"{tool_name} — {G}Already installed ✓{X}")
            continue

        print(f"  {Y}[*]{X} Installing {tool_name}...", end='\r')
        success = run(f"apt install -y {pkg} -qq 2>/dev/null")
        if success:
            log("+", f"{tool_name} — {G}Installed ✓{X}")
        else:
            log("-", f"{tool_name} — {R}Failed ✗{X}")
            failed.append(tool_name)

    if failed:
        print(f"\n  {Y}Failed tools: {', '.join(failed)}{X}")
        print(f"  {DM}Manually install: sudo apt install {' '.join(failed)}{X}")

def setup_proxychains():
    print(f"\n  {BD}{W}[2/4] ProxyChains Configure Ho Raha Hai...{X}\n")

    config_file = "/etc/proxychains4.conf"
    if not os.path.exists(config_file):
        config_file = "/etc/proxychains.conf"

    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()

        # Enable dynamic chain
        content = content.replace('#dynamic_chain', 'dynamic_chain')
        content = content.replace('strict_chain', '#strict_chain')

        # Add Tor socks5
        if 'socks5  127.0.0.1 9050' not in content:
            content += '\nsocks5  127.0.0.1 9050\n'

        with open(config_file, 'w') as f:
            f.write(content)

        log("+", f"{G}ProxyChains configured for Tor ✓{X}")
    else:
        log("-", "ProxyChains config not found")

def setup_tor():
    print(f"\n  {BD}{W}[3/4] Tor Setup Ho Raha Hai...{X}\n")

    run("systemctl enable tor 2>/dev/null")
    run("service tor start 2>/dev/null")
    time.sleep(3)

    # Check tor port
    port_check = subprocess.run("ss -tlnp | grep 9050", shell=True, capture_output=True, text=True)
    if port_check.stdout.strip():
        log("+", f"{G}Tor is running on port 9050 ✓{X}")
        return

    # Try curl with longer timeout
    try:
        check = subprocess.run(
            "curl --socks5 127.0.0.1:9050 --max-time 8 https://check.torproject.org/api/ip 2>/dev/null",
            shell=True, capture_output=True, text=True, timeout=15
        )
        if "true" in check.stdout.lower():
            log("+", f"{G}Tor is running ✓{X}")
        else:
            log("!", f"{Y}Tor started — verify manually:{X}")
            print(f"  {DM}  sudo service tor status{X}")
    except subprocess.TimeoutExpired:
        log("!", f"{Y}Tor started — connection test timed out (normal){X}")
        print(f"  {DM}  Verify: sudo service tor status{X}")

def setup_config():
    print(f"\n  {BD}{W}[4/4] ZENVORA Config Setup...{X}\n")

    cfg = {}

    # Shodan API
    print(f"  {Y}Shodan API key chahiye hai enhanced scanning ke liye.{X}")
    print(f"  {DM}  Free key: https://shodan.io → Register → My Account{X}")
    print(f"  {DM}  Skip karna hai to Enter dabaao{X}\n")

    key = input(f"  {C}Shodan API Key: {X}").strip()
    cfg['shodan_key'] = key if key else None

    if key:
        log("+", f"{G}Shodan API key saved ✓{X}")
    else:
        log("!", f"{Y}Shodan skipped — features disabled{X}")

    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

    log("+", f"{G}Config saved to {CONFIG_FILE} ✓{X}")

def create_alias():
    bashrc = os.path.expanduser("~/.bashrc")
    alias_line = f'\nalias zenvora="python3 {os.path.abspath("recon_v3.py")}"\n'

    with open(bashrc, 'r') as f:
        content = f.read()

    if 'alias zenvora' not in content:
        with open(bashrc, 'a') as f:
            f.write(alias_line)
        log("+", f"{G}Alias added — type 'zenvora' anywhere to run tool ✓{X}")
        log("!", f"{Y}Run: source ~/.bashrc to activate alias{X}")
    else:
        log("+", f"{G}Alias already exists ✓{X}")

def final_check():
    print(f"\n  {BD}{C}{'─'*52}{X}")
    print(f"  {BD}{W}  Final Check — All Tools{X}")
    print(f"  {BD}{C}{'─'*52}{X}\n")

    tools = ["nmap","gobuster","wafw00f","sqlmap","nikto",
             "hydra","tor","proxychains4","curl","masscan"]

    all_good = True
    for tool in tools:
        check = subprocess.run(f"which {tool} 2>/dev/null",
                               shell=True, capture_output=True, text=True)
        if check.stdout.strip():
            log("+", f"{tool:<15} {G}✓ Ready{X}")
        else:
            log("-", f"{tool:<15} {R}✗ Missing{X}")
            all_good = False

    return all_good

def main():
    banner()
    check_root()

    print(f"  {Y}Yeh script ZENVORA Recon Tool ke liye sab kuch setup karega.{X}")
    print(f"  {DM}  Tools install honge, Tor configure hoga, config save hogi.{X}\n")

    confirm = input(f"  {C}Start setup? (y/n): {X}").strip().lower()
    if confirm != 'y':
        print(f"\n  {Y}Setup cancelled.{X}\n")
        sys.exit(0)

    print()
    install_tools()
    setup_proxychains()
    setup_tor()
    setup_config()
    create_alias()

    print(f"\n  {BD}{C}{'═'*52}{X}")
    all_good = final_check()
    print(f"  {BD}{C}{'═'*52}{X}\n")

    if all_good:
        print(f"  {G}{BD}✅  ZENVORA Setup Complete!{X}\n")
    else:
        print(f"  {Y}{BD}⚠  Setup complete — kuch tools missing hain{X}\n")

    print(f"  {W}Ab tool use karo:{X}")
    print(f"  {DM}  python3 recon_v3.py --help{X}")
    print(f"  {DM}  python3 recon_v3.py -m quick scanme.nmap.org{X}")
    print(f"  {DM}  source ~/.bashrc && zenvora -m quick scanme.nmap.org{X}")
    print(f"\n  {DM}Empire: ZENVORA | Built by: Zenomro{X}\n")

if __name__ == "__main__":
    main()
