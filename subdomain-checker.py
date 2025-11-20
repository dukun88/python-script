import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def check(url):
    """Cek apakah subdomain hidup"""
    try:
        r = requests.get("http://" + url, timeout=2)
        return {"subdomain": url, "status": r.status_code}
    except Exception:
        return {"subdomain": url, "status": None}


def load_wordlist(path):
    """Load wordlist .txt"""
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def scan_subdomains(domain, wordlist_file, threads=50):
    sub_list = load_wordlist(wordlist_file)
    results = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(check, f"{sub}.{domain}")
            for sub in sub_list
        ]

        for future in as_completed(futures):
            results.append(future.result())

    return results


# ====================
# MAIN
# ====================
if __name__ == "__main__":
    domain = input("Masukkan domain: ")
    wordlist_path = input("Masukkan path wordlist.txt: ")

    results = scan_subdomains(domain, wordlist_path)

    print("\n=== HASIL SCAN ===")
    for r in results:
        if r["status"] is not None:
            print(f"[UP]   {r['subdomain']}  -> {r['status']}")
        else:
            print(f"[DOWN] {r['subdomain']}")