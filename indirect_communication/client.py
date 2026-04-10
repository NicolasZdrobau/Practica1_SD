import pika
import sys
import time
import uuid

# Modificar per l'adreça del servidor RabbitMQ si no està en local
RABBIT_HOST = 'localhost' 
# Modificar per les credencials si no són les per defecte (admin/admin123 en AWS)
RABBIT_USER = 'guest'
RABBIT_PASS = 'guest'

class TicketClient:
    def __init__(self, file_path):
        self.file_path = file_path
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
        )
        self.channel = self.connection.channel()

        # Creem una cua exclusiva i temporal per rebre les respostes
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        # Ens subscrivim a la cua de respostes
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.responses_received = 0
        self.total_requests = 0
        self.results_summary = {
            "SUCCESS": 0, 
            "FULL": 0, 
            "DUPLICATE_REQ": 0, 
            "SEAT_OCCUPIED": 0, 
            "INVALID": 0
        }

    def on_response(self, ch, method, props, body):
        # Normalitzem a majúscules per facilitar la comparació        
        res = body.decode().upper()
        self.responses_received += 1
        
        if res.isdigit() or "TRUE" in res:
            self.results_summary["SUCCESS"] += 1
        elif "FULL" in res or "PLE" in res:
            self.results_summary["FULL"] += 1
        elif "DUPLICATE" in res:
            self.results_summary["DUPLICATE_REQ"] += 1
        elif "ALREADY_SOLD" in res or "OCUPAT" in res:
            self.results_summary["SEAT_OCCUPIED"] += 1
        elif "INVALID" in res:
            self.results_summary["INVALID"] += 1
        else:
            self.results_summary["INVALID"] += 1
            
        print(f" [+] Progress: {self.responses_received}/{self.total_requests} respostes rebudes...", end='\r')

    def run_benchmark(self):
        try:
            print(f" [*] Connectat a RabbitMQ. Llegint {self.file_path}...")
            
            # Llegim les línies filtrant comentaris (#) i línies buides
            lines = []
            with open(self.file_path, 'r') as f:
                for l in f:
                    clean_line = l.strip()
                    # Ignorem si la línia està buida o comença per #
                    if not clean_line or clean_line.startswith('#'):
                        continue
                    lines.append(clean_line)
            
            self.total_requests = len(lines)
            
            if self.total_requests == 0:
                print(" [!] El fitxer està buit o només conté comentaris.")
                return

            start_time = time.time()

            for line in lines:
                corr_id = str(uuid.uuid4())
                self.channel.basic_publish(
                    exchange='',
                    routing_key='ticket_requests',
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue, # Diem al worker on respondre
                        correlation_id=corr_id, # ID únic per cada petició
                        delivery_mode=2,
                    ),
                    body=line
                )
            
            print(f" [+] Enviades {self.total_requests} peticions. Esperant respostes...")

            # Es queda en aquest bucle fins que rebem totes les respostes
            while self.responses_received < self.total_requests:
                self.connection.process_data_events(time_limit=None)

            total_time = time.time() - start_time
            
            print("\n")
            print(f" {'RESUM DETALLAT DEL BENCHMARK':^43}")
            print("")
            print(f" {'Temps total:':<25} {total_time:>13.2f} s ")
            print(f" {'Rendiment:':<25} {self.total_requests/total_time:>11.2f} req/s ")
            print("")
            print(f" {' [✓] Èxits:':<25} {self.results_summary['SUCCESS']:>15} ")
            print(f" {' [!] Concert Ple:':<25} {self.results_summary['FULL']:>15} ")
            print(f" {' [D] Peticions Duplicades:':<25} {self.results_summary['DUPLICATE_REQ']:>15} ")
            print(f" {' [S] Seients ja Ocupats:':<25} {self.results_summary['SEAT_OCCUPIED']:>15} ")
            print(f" {' [X] Format Incorrecte:':<25} {self.results_summary['INVALID']:>15} ")
            print("")
            print(f" {'TOTAL PROCESSATS:':<25} {self.responses_received:>15} ")

        except Exception as e:
            print(f" [!] Error: {e}")
        finally:
            self.connection.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Ús: python client.py <fitxer.txt>")
    else:
        client = TicketClient(sys.argv[1])
        client.run_benchmark()