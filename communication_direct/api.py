from flask import Flask, request, jsonify
from ticket_logic.ticket_service import TicketService
import sys

" Creamos la aplicación Flask y el servicio de tickets """
app = Flask(__name__)
ticket_service = TicketService()



@app.route("/buy/numbered", methods=["POST"])
def buy_numbered():
    """ Endpoint para comprar un ticket numerado. Se espera un JSON y comprueba que tenga los campos necesarios. Luego llama al servicio de tickets y devuelve el resultado. """
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400
    
    client_id = data.get("client_id")
    seat_id = data.get("seat_id")
    request_id = data.get("request_id")

    if not client_id or not seat_id or not request_id:
        return jsonify({"error": "Missing required fields: client_id, seat_id, request_id"}), 400
    try:
        seat_id = int(seat_id)
    except ValueError:
        return jsonify({"error": "seat_id must be an integer"}), 400
    
    result = ticket_service.buy_numbered_ticket(client_id, seat_id, request_id)

    return jsonify({
    "result": result,
    "server_port": app.config["SERVER_PORT"]
}), 200

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app.config["SERVER_PORT"] = port

    print(f"Starting API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)