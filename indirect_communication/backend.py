import redis

class TicketService:
    def __init__(self, host='localhost', port=6379, limit=20000):
        self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.limit = limit
        self.counter_key = "tickets_sold"
        self.req_set_key = "processed_requests" # On guardem els IDs per evitar duplicats

    def is_already_processed(self, request_id):
        """Comprova si aquest request_id ja s'ha processat correctament abans."""
        return self.r.sismember(self.req_set_key, request_id)

    def mark_as_processed(self, request_id):
        """Afegeix el request_id al conjunt de processats."""
        self.r.sadd(self.req_set_key, request_id)
        
    def buy_unumbered_ticket(self, request_id):
        if self.is_already_processed(request_id):
            return False, "DUPLICATE_REQUEST"

        new_value = self.r.incr(self.counter_key)
        
        if new_value <= self.limit:
            self.mark_as_processed(request_id)
            return True, new_value
        else:
            # Si hem incrementat però no podem vendre, restem 1 per mantenir el comptador real
            self.r.decr(self.counter_key)
            return False, "FULL"

    def buy_numbered_ticket(self, seat_id, request_id):
        if self.is_already_processed(request_id):
            return False, "DUPLICATE_REQUEST"

        try:
            s_id = int(seat_id)
            if s_id < 1 or s_id > self.limit:
                return False, "OUT_OF_RANGE"
            
            seat_key = f"seat:{s_id}"
            
            # Intentem agafar el seient
            if self.r.setnx(seat_key, f"SOLD_TO_{request_id}"):
                
                # Intentem incrementar l'aforament total
                new_value = self.r.incr(self.counter_key)
        
                if new_value <= self.limit:
                    self.mark_as_processed(request_id)
                    return True, s_id
                else:
                    # Si el concert està ple, hem d'alliberar el seient 
                    # i tornar el comptador enrere
                    self.r.delete(seat_key)
                    self.r.decr(self.counter_key)
                    return False, "FULL"
            else:
                return False, "ALREADY_SOLD"
                
        except ValueError:
            return False, "INVALID_FORMAT"