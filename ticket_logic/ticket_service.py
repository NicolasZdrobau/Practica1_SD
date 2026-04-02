from storage.redis_client import get_redis

class TicketService:
    def __init__(self):
        self.redis = get_redis()
        self.unnumbered_counter_key = "tickets:unnumbered:sold"
        self.limit = 20000

    " Resetea el stock de tickets no numerados a 0, es decir, sin tickets vendidos"
    def init_unnumbered_stock(self):
        self.redis.set(self.unnumbered_counter_key, 0)
    
    def buy_numbered_ticket(self, client_id, seat_id, request_id):
        if seat_id < 1 or seat_id > 20000:
            return "Invalid seat ID"
        
        " Miramos si el request_id ya fue procesado para evitar por ejmeoplo compra repetida por parte del cliente "
        
        request_key = f"request:numbered:{request_id}"
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
    
    def buy_unnumbered_ticket(self, client_id, request_id):
        request_key = f"request:unnumbered:{request_id}"

        " Miramos si el request_id ya fue procesado para evitar por ejmeoplo compra repetida por parte del cliente "
        
        existing_request = self.redis.get(request_key)
        if existing_request is not None:
            print(f"Replayed request: {request_id}")
            return existing_request

        " Intentamos comprar un ticket incrementando el contador de tickets vendidos. Si el nuevo valor supera el límite, se revierte la compra y "
        "se marca como fallo por falta de stock, es decir todos los tickets vendidos"
        new_value = self.redis.incr(self.unnumbered_counter_key)

        if new_value <= self.limit:
            request_result = "success"
        else:
            self.redis.decr(self.unnumbered_counter_key)
            request_result = "failure:full"

        self.redis.set(request_key, request_result)
        return request_result