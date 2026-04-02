import time
import requests

BENCHMARK_FILE = "benchmark_numbered_60000.txt"
BASE_URL = "http://10.0.1.185"

success_count = 0
failure_count = 0
invalid_count = 0
http_error_count = 0
connection_error_count = 0
unexpected_count = 0

start = time.time()

with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) != 4 or parts[0] != "BUY":
            print(f"Línea inválida: {line}")
            continue

        client_id = parts[1]
        seat_id = int(parts[2])
        request_id = parts[3]

        payload = {
            "client_id": client_id,
            "seat_id": seat_id,
            "request_id": request_id
        }

        try:
            response = requests.post(
                f"{BASE_URL}/buy/numbered",
                json=payload,
                timeout=5
            )

            if response.status_code != 200:
                http_error_count += 1
                print(f"HTTP {response.status_code}: {response.text}")
                continue

            try:
                data = response.json()
            except ValueError:
                unexpected_count += 1
                print(f"Respuesta no JSON: {response.text}")
                continue

            result = data.get("result")

            if isinstance(result, str) and result.startswith("success:"):
                success_count += 1
            elif result == "failure:seat_taken":
                failure_count += 1
            elif result == "Invalid seat ID":
                invalid_count += 1
            else:
                unexpected_count += 1
                print("Resultado inesperado:", data)

        except requests.exceptions.ConnectionError as e:
            connection_error_count += 1
            print("ConnectionError:", e)
        except requests.exceptions.Timeout as e:
            connection_error_count += 1
            print("Timeout:", e)

end = time.time()

print("Execution time:", end - start)
print("Success count:", success_count)
print("Failure count:", failure_count)
print("Invalid count:", invalid_count)
print("HTTP error count:", http_error_count)
print("Connection/timeout count:", connection_error_count)
print("Unexpected count:", unexpected_count)