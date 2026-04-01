import pika  # Llibreria estàndard per RabbitMQ
from indirect_communication.backend import TicketService

# Connectem amb el servidor RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Ens assegurem que la cua existeix
channel.queue_declare(queue='ticket_requests', durable=True)

backend = TicketService()

def callback(ch, method, properties, body):
    # El missatge arriba com a string, ex: "BUY client_1 req_101" o "BUY client_1 42 req_2001"
    line = body.decode().strip()
    parts = line.split()
    
    # Validació bàsica
    if not parts or parts[0] != "BUY":
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    
    # El request_id sempre és l'última part del missatge
    req_id = parts[-1]
    
    # CAS A: TIQUET NUMERAT (Té 4 parts: BUY, client, seient, request)
    if len(parts) == 4:
        client_id = parts[1]
        seat_id = parts[2]
        success, res = backend.buy_numbered_ticket(seat_id, req_id)
        if success:
            print(f" [V] NUMERAT: Seient {seat_id} venut a {client_id}")
        elif res == "DUPLICATE_REQUEST":
            print(f" [!] Ignorat: La petició {req_id} ja s'havia processat.")
        else:
            print(f" [X] NUMERAT: Seient {seat_id} OCUPAT")

    # CAS B: TIQUET NO NUMERAT (Té 3 parts: BUY, client, request)
    elif len(parts) == 3:
        client_id = parts[1]
        success, res = backend.buy_unumbered_ticket(req_id)
        if success:
            print(f" [V] NO-NUMERAT: Tiquet {res} venut a {client_id}")
        elif res == "DUPLICATE_REQUEST":
            print(f" [!] Ignorat: La petició {req_id} ja s'havia processat.")
        else:
            print(f" [X] NO-NUMERAT: Esgotats!")

    # Confirmem que hem processat el missatge
    ch.basic_ack(delivery_tag=method.delivery_tag)

# "Fair dispatch": No enviïs un altre missatge a aquest worker fins que no acabi l'actual.
channel.basic_qos(prefetch_count=1)

# Configurem qui escolta la cua
channel.basic_consume(queue='ticket_requests', on_message_callback=callback)

print(' [*] Esperant missatges. Per sortir prem CTRL+C')
channel.start_consuming()