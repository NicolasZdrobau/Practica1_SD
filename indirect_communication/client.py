import pika
import sys
import time

RABBIT_HOST = '10.0.1.16' 
RABBIT_USER = 'admin'
RABBIT_PASS = 'admin123'

def send_benchmark_requests(file_path):
    try:
        # Configurem les credencials per a l'autenticació PLAIN
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
        
        # Connectem a la IP d'AWS en comptes de localhost
        parameters = pika.ConnectionParameters(
            host=RABBIT_HOST,
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declarem la cua (ha de coincidir amb la del worker)
        channel.queue_declare(queue='ticket_requests', durable=True)

        print(f" [*] Connectat a RabbitMQ a {RABBIT_HOST}")
        print(f" [*] Llegint fitxer: {file_path}...")
        
        start_time = time.time()
        count = 0

        with open(file_path, 'r') as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line: continue
                
                channel.basic_publish(
                    exchange='',
                    routing_key='ticket_requests',
                    body=clean_line,
                    properties=pika.BasicProperties(
                        delivery_mode=2, # Missatges persistents
                    )
                )
                count += 1
        
        end_time = time.time()
        print(f"---")
        print(f" [+] ÈXIT: S'han enviat {count} peticions.")
        print(f" [+] Temps d'execució del client: {end_time - start_time:.2f} segons.")
        print(f"---")
        
        connection.close()

    except FileNotFoundError:
        print(f" [!] Error: No s'ha trobat el fitxer '{file_path}'")
    except pika.exceptions.ProbableAuthenticationError:
        print(f" [!] Error: Credencials incorrectes (admin/admin123).")
    except Exception as e:
        print(f" [!] Error inesperat: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Ús: python client.py <nom_del_fitxer_benchmark.txt>")
    else:
        file_to_read = sys.argv[1]
        send_benchmark_requests(file_to_read)