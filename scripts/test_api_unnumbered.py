import requests

url = "http://127.0.0.1:5000/buy/unnumbered"

payload = {
    "client_id": "user00001",
    "request_id": "00001"
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())