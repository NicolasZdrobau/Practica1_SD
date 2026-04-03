import sys
import time
import requests


BASE_URL = "http://10.0.1.185"


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python3 -m scripts.test_benchmark_unnumbered_concurrent <benchmark_file>")
        sys.exit(1)

    benchmark_file = sys.argv[1]

    success_count = 0
    failure_count = 0
    http_error_count = 0
    connection_error_count = 0
    unexpected_count = 0

    start = time.time()

    with open(benchmark_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) != 3 or parts[0] != "BUY":
                print(f"Línea inválida: {line}")
                continue

            client_id = parts[1]
            request_id = parts[2]

            payload = {
                "client_id": client_id,
                "request_id": request_id
            }

            try:
                response = requests.post(
                    f"{BASE_URL}/buy/unnumbered",
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

                if result == "success":
                    success_count += 1
                elif result == "failure:full":
                    failure_count += 1
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

    print(f"Benchmark file: {benchmark_file}")
    print(f"Execution time: {end - start}")
    print(f"Success count: {success_count}")
    print(f"Failure count: {failure_count}")
    print(f"HTTP error count: {http_error_count}")
    print(f"Connection/timeout count: {connection_error_count}")
    print(f"Unexpected count: {unexpected_count}")


if __name__ == "__main__":
    main()