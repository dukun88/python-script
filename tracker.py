import requests

API_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,query"

def lookup(ip):
    try:
        r = requests.get(API_URL.format(ip=ip), timeout=10)
        data = r.json()
        if data.get("status") != "success":
            return {"ip": ip, "error": data.get("message", "lookup_failed")}
        return data
    except Exception as e:
        return {"ip": ip, "error": str(e)}

def print_result(data):
    if "error" in data:
        print(f"[!] {data['ip']} → ERROR: {data['error']}")
    else:
        print(f"""
IP        : {data['query']}
Country   : {data['country']}
Region    : {data['regionName']}
City      : {data['city']}
Lat/Lon   : {data['lat']}, {data['lon']}
ISP       : {data['isp']}
Org       : {data['org']}
----------------------------------------
        """.strip())

def main():
    print("=== IP Tracker CLI ===")
    print("Ketik 'exit' untuk keluar.")
    
    while True:
        ip = input("\nMasukkan IP target: ").strip()
        
        if ip.lower() in ["exit", "quit"]:
            print("Keluar...")
            break
        
        if ip == "":
            print("IP tidak boleh kosong.")
            continue
        
        data = lookup(ip)
        print_result(data)

if __name__ == "__main__":
    main()