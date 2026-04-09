import pika  # Llibreria estàndard per RabbitMQ
from backend import TicketService

HOST = 'localhost'
credentials = pika.PlainCredentials("guest", "guest")

# Connectem amb el servidor RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, credentials=credentials))
channel = connection.channel()

# Ens assegurem que la cua existeix
channel.queue_declare(queue='ticket_requests', durable=True)

backend = TicketService(host=HOST)
backend.initialize_seats() # S'assegura que la llista existeix abans de processar res

def callback(ch, method, properties, body):
    # El missatge arriba com a string, ex: "BUY client_1 req_101" o "BUY client_1 42 req_2001"
    line = body.decode().strip()
    parts = line.split()
    
    res = "INVALID_FORMAT"
    
    # Validació bàsica
    if parts and parts[0] == "BUY":
        # El request_id sempre és l'última part del missatge
        req_id = parts[-1]
        client_id = parts[1]

        # CAS A: TIQUET NUMERAT (Té 4 parts: BUY, client, seient, request)
        if len(parts) == 4:
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
            success, res = backend.buy_unumbered_ticket(req_id)
            
            if success:
                print(f" [V] NO-NUMERAT: Tiquet {res} venut a {client_id}")
            elif res == "DUPLICATE_REQUEST":
                print(f" [!] Ignorat: La petició {req_id} ja s'havia processat.")
            else:
                print(f" [X] NO-NUMERAT: Esgotats!")
    
    if properties.reply_to:
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to, # Respon a la cua temporal del client
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=str(res) # Enviem el resultat
        )
        
    # Confirmem que hem processat el missatge
    ch.basic_ack(delivery_tag=method.delivery_tag)

# "Fair dispatch": No enviïs un altre missatge a aquest worker fins que no acabi l'actual.
channel.basic_qos(prefetch_count=1)

# Configurem qui escolta la cua
channel.basic_consume(queue='ticket_requests', on_message_callback=callback)

print(' [*] Esperant missatges. Per sortir prem CTRL+C')
channel.start_consuming()