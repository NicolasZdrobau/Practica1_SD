from storage.redis_client import get_redis

class TicketService:
    def __init__(self):
        self.redis = get_redis()
    
    def init_unnumbered_stock(self, total=20000):
        self.redis.set("tickets:unnumbered:stock", total)
    
    def buy_numbered_ticket(self, client_id, seat_id, request_id):
        if seat_id < 1 or seat_id > 20000:
            return "Invalid seat ID"
        
        " Miramos si el request_id ya fue procesado para evitar por ejmeoplo compra repetida por parte del cliente "
        
        request_key = f"request:{request_id}"
        existing_request = self.redis.get(request_key)

        if existing_request is not None:
            print(f"Replayed request: {request_id}")
            return existing_request
                
        seat_key = f"seat:{seat_id}"

        result = self.redis.setnx(seat_key, f"{client_id}:{request_id}")

        if result:
            request_result = f"success:{seat_id}"
        else:
            request_result = "failure:seat_taken"
        
        self.redis.set(request_key, request_result)
        return request_result
    