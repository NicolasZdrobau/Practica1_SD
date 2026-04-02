OUTPUT_FILE = "benchmark_unnumbered_60000.txt"
TOTAL_REQUESTS = 60000

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("# Concert Ticket Benchmark – Unnumbered Seats\n")
    f.write("# Total tickets: 20000\n")
    f.write("# Format: BUY <client_id> <request_id>\n\n")

    for i in range(1, TOTAL_REQUESTS + 1):
        f.write(f"BUY user{i:05d} {i:05d}\n")

print(f"Generated {OUTPUT_FILE} with {TOTAL_REQUESTS} requests")