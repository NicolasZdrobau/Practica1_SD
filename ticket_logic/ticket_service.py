from storage.redis_client import get_redis

class TicketService:
    def __init__(self):
        self.redis = get_redis()
    
    def init_unnumbered_stock(self, total=20000):
        self.redis.set("tickets:unnumbered:stock", total)
