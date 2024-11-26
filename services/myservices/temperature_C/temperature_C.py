import json
from flask import Flask, jsonify, request
import requests
import paho.mqtt.client as mqtt
import datetime
import jwt
from functools import wraps


app = Flask(__name__)


temps = [ ]
current_id = 0
SECRET_KEY = "your_secret_key"


mitmproxy_ip = "10.151.101.1"
mitmproxy_port = 8080
proxies = {
    "http": f"http://{mitmproxy_ip}:{mitmproxy_port}",
    "https": f"http://{mitmproxy_ip}:{mitmproxy_port}",
}

def on_message(client, userdata, message):
    global current_id
    try:
        temp_data = json.loads(message.payload.decode())
        print(f"Recebido: {temp_data}")

        new_temp = {
            'id': current_id,
            'temperature': temp_data['temperature'],
            'type': temp_data['type'],
            'continent' : temp_data['continent'],
	    'time': temp_data['time']
	}
        temps.append(new_temp)
        current_id += 1

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

mqtt_client = mqtt.Client("Ric")
mqtt_client.on_message = on_message

mqtt_client.connect("10.151.101.58")
mqtt_client.subscribe("/temp_C")
mqtt_client.loop_start()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/temps', methods=['GET'])
@token_required
def get_temps():
 return jsonify(temps)

@app.route('/tempsbyConti', methods=['GET'])
@token_required
def get_temps_by_conti():
    continent = request.args.get('continent')
    
    if continent:
        filtered_temps = [temp for temp in temps if temp['continent'].lower() == continent.lower()]
        return jsonify(filtered_temps)
    else:
        return jsonify(temps)


@app.route('/temps_of_day', methods=['GET'])
@token_required
def get_temps_of_day():
    date_str = request.args.get('date')

    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400

    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    filtered_temps = [
        temp for temp in temps if temp['time'].startswith(date_str)
    ]

    return jsonify(filtered_temps)


if __name__ == '__main__':
    try:
        response = requests.post("http://10.151.101.12:5000/services", data={
            "type": "C",
            "url": "http://10.151.101.153:5003/temps"
        }, proxies=proxies)

        if response.status_code == 200 or response.status_code == 201:
            print("Serviço registrado com sucesso!")
        else:
            print(f"Erro ao registrar serviço. Código: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer POST: {e}")

    app.run(host='0.0.0.0', port=5003)


