import time
from ticket_logic.ticket_service import TicketService

BENCHMARK_FILE = "benchmark_numbered_60000.txt"

service = TicketService()
service.redis.flushdb()   # solo en pruebas
"""
success_count = 0
failure_count = 0
invalid_count = 0

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

        result = service.buy_numbered_ticket(client_id, seat_id, request_id)

        if result.startswith("success:"):
            success_count += 1
        elif result == "failure:seat_taken":
            failure_count += 1
        elif result == "Invalid seat ID":
            invalid_count += 1
        else:
            print("Resultado inesperado:", result)

end = time.time()

print("Execution time:", end - start)
print("Success count:", success_count)
print("Failure count:", failure_count)
print("Invalid count:", invalid_count)
"""




print(service.buy_numbered_ticket("userA", 42, "reqA"))   # compra asiento
print(service.buy_numbered_ticket("userB", 42, "reqB"))   # falla
print(service.buy_numbered_ticket("userB", 42, "reqB"))   # misma request otra vez