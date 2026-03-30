import threading
import requests

results = []
lock = threading.Lock()

URL = "http://127.0.0.1:8080/buy/numbered"

def worker(i):
    payload = {
        "client_id": f"user{i:05d}",
        "seat_id": 42,
        "request_id": f"{i:05d}"
    }

    response = requests.post(URL, json=payload)

    with lock:
        results.append((
            response.status_code,
            response.text[:200]
        ))

threads = []

for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

for status, text in results:
    print("STATUS:", status)
    print("BODY:", text)
    print("---")