import requests
from ticket_logic.ticket_service import TicketService


url = "http://127.0.0.1:5000/buy/numbered"

payload = {
    "client_id": "user00002",
    "seat_id": 43,
    "request_id": "00002"
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())
"""
service = TicketService()
service.redis.flushdb()"""