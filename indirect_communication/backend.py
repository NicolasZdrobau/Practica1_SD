import redis

class TicketService:
    def __init__(self, host='localhost', port=6379, limit=20000):
        self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.limit = limit
        self.seats_pool_key = "available_seats"  # La llista de seients lliures
        self.req_set_key = "processed_requests" # On guardem els IDs per evitar duplicats

    def initialize_seats(self):
        """Omple la llista amb tots els números de seient (1 a 20000)."""
        # Només ho fem si la llista no existeix o està buida
        if self.r.exists(self.seats_pool_key):
            return
            
        print(f" [*] Inicialitzant {self.limit} seients...")
        # Fem servir un pipeline per anar més ràpid
        pipe = self.r.pipeline()
        for i in range(1, self.limit + 1):
            pipe.rpush(self.seats_pool_key, i)
        pipe.execute()

    def is_already_processed(self, request_id):
        """Comprova si aquest request_id ja s'ha processat correctament abans."""
        return self.r.sismember(self.req_set_key, request_id)

    def mark_as_processed(self, request_id):
        """Afegeix el request_id al conjunt de processats."""
        self.r.sadd(self.req_set_key, request_id)
        
    def buy_unumbered_ticket(self, request_id):
        if self.is_already_processed(request_id):
            return False, "DUPLICATE_REQUEST"

        # LPOP treu i retorna el primer element de la llista (Atòmic)
        seat_assigned = self.r.lpop(self.seats_pool_key)
        
        if seat_assigned:
            # Marquem el seient com a ocupat per aquest usuari
            self.r.set(f"seat:{seat_assigned}", f"SOLD_TO_{request_id}")
            self.mark_as_processed(request_id)
            return True, seat_assigned
        else:
            return False, "FULL"

    def buy_numbered_ticket(self, seat_id, request_id):
        if self.is_already_processed(request_id):
            return False, "DUPLICATE_REQUEST"

        try:
            s_id = int(seat_id)
            
            # LREM intenta treure el seient específic de la llista de lliures
            # LREM(key, count, value). count=0 vol dir totes les ocurrències
            removed_count = self.r.lrem(self.seats_pool_key, 0, s_id)
            
            if removed_count > 0:
                # Si removed_count és 1, vol dir que el seient estava lliure i l'hem tret
                self.r.set(f"seat:{s_id}", f"SOLD_TO_{request_id}")
                self.mark_as_processed(request_id)
                return True, s_id
            else:
                # Si és 0, el seient ja no estava a la llista (ja s'ha venut)
                # Hem de comprovar si és que el concert està ple o el seient ocupat
                if self.r.llen(self.seats_pool_key) == 0:
                    return False, "FULL"
                else:
                    return False, "ALREADY_SOLD"
                
        except ValueError:
            return False, "INVALID_FORMAT"