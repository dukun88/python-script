from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

LOGFILE = "access.log"

def log_visit(ip, ua, path):
    with open(LOGFILE, "a") as f:
        f.write(f"{datetime.now()} | IP: {ip} | Agent: {ua} | Path: {path}\n")

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def track(path):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "Unknown")

    log_visit(ip, ua, path)

    return redirect("https://www.youtube.com/watch?v=0zxiPjlpK6k")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
