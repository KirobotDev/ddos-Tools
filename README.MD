# KIROSSTRESS v1.0
**Stress Ultime – DDoS**

---

## Fonctionnalités

- **Interface interactive** : URL, durée, niveau d’intensité  
- **300+ proxies vivants en direct**
- **5 sources fiables** : Proxyscrape, Proxy-List, GitHub, etc.  
- **Test en parallèle** : 300+ proxies vérifiés en < 30s  
- **Flood mixte** :  
  - `socket` TCP raw (brutal)  
  - `aiohttp` async via proxies (300+ IP différentes)  
- **Vérification automatique** : Site down pour **TOUT LE MONDE**  
- **Zéro dépendance locale** : tout en mémoire  
- **Ubuntu / Linux / Python 3.8+**

---

## Installation

```bash
# 1. Cloner ou copier le script
wget https://raw.githubusercontent.com/kirobotdev/ddos-tools/main/ddos.py

# 2. Installer les dépendances
pip install aiohttp requests

# 3. Lancer
python3 ddos.py
