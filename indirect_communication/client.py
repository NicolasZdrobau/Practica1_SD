import pika
import sys
import time

def send_benchmark_requests(file_path):
    try:
        # Connexió a RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        
        # Declarem la cua
        channel.queue_declare(queue='ticket_requests', durable=True)

        print(f" [*] Llegint fitxer: {file_path}")
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
                        delivery_mode=2, # Fa que el missatge sigui persistent en disc
                    )
                )
                count += 1
        
        end_time = time.time()
        print(f" [+] S'han enviat {count} peticions correctament.")
        print(f" [+] Temps d'enviament: {end_time - start_time:.2f} segons.")
        
        connection.close()

    except FileNotFoundError:
        print(f" [!] Error: No s'ha trobat el fitxer '{file_path}'")
    except Exception as e:
        print(f" [!] Error inesperat: {e}")

if __name__ == "__main__":
    # Comprovem si l'usuari ha passat el nom del fitxer com a argument
    if len(sys.argv) < 2:
        print("Ús: python client.py <nom_del_fitxer_benchmark.txt>")
    else:
        file_to_read = sys.argv[1]
        send_benchmark_requests(file_to_read)