import time
from ticket_logic.ticket_service import TicketService

BENCHMARK_FILE = "benchmark_unnumbered_20000.txt"

service = TicketService()


success_count = 0
failure_count = 0


start = time.time()

with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) != 3 or parts[0] != "BUY":
            print(f"Línea inválida: {line}")
            continue

        client_id = parts[1]
        request_id = int(parts[2])
        

        result = service.buy_unnumbered_ticket(client_id, request_id)

        if result == "success":
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








