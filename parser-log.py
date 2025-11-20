import re
from collections import Counter

log_pattern = re.compile(
    r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<proto>\S+)" '
    r'(?P<status>\d{3}) (?P<size>\d+)'
)

ip_counter = Counter()
status_counter = Counter()

with open("access.log", "r") as f:
    for line in f:
        m = log_pattern.search(line)
        if m:
            d = m.groupdict()
            ip_counter[d["ip"]] += 1
            status_counter[d["status"]] += 1

print("IP terbanyak:", ip_counter.most_common(5))
print("Status code:", status_counter)
