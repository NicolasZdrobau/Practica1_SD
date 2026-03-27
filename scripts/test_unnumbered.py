from ticket_logic.ticket_service import TicketService

# crear servicio
service = TicketService()

# inicializar stock (20000 o el número que quieras para test)
service.init_unnumbered_stock()

# comprobar que funciona
print(service.redis.get("tickets:unnumbered:stock"))