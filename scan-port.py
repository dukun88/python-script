import socket
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_port(host, port, timeout=0.3):
    """Mencoba koneksi ke port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                return port
    except:
        return None
    return None

def fast_port_scan(host, start=1, end=1024, threads=200):
    open_ports = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_port, host, port): port for port in range(start, end + 1)}

        for future in as_completed(futures):
            port = futures[future]
            result = future.result()
            if result:
                print(f"[OPEN] Port {result}")
                open_ports.append(result)

    return open_ports

if __name__ == "__main__":
    target = input("Target IP: ")
    print(f"Scanning {target} ...")

    open_ports = fast_port_scan(target, start=1, end=65535, threads=500)
    with open("open_ports.json", "w") as f:
        json.dump({"open_ports": open_ports}, f, indent=4)


    print("\nSelesai. Port terbuka:")
    print(open_ports)
