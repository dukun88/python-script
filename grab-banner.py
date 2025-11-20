import socket

def grab_banner(host, port, timeout=2):
    """Mengambil banner dari service tertentu"""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        banner = s.recv(1024)
        return banner.decode(errors="ignore")  
    except Exception as e:
        return None
    finally:
        s.close()


if __name__ == "__main__":
    target = input("Target : ")   
    ports = [21, 22, 25, 80, 110, 443, 445, 3306]

    print(f"[+] Banner Grabber untuk {target}\n")

    for p in ports:
        print(f"--- Port {p} ---")
        banner = grab_banner(target, p)
        if banner:
            print("Banner:", banner.strip())
        else:
            print("Tidak ada banner / Port tertutup.")
        print()
