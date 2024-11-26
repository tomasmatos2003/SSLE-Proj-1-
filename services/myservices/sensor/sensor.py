import time
import random
import paho.mqtt.client as mqtt
import json
import datetime

broker_address = "10.151.101.58"
topic_c = "/temp_C" 
topic_f = "/temp_F"

topic_storage = "/storage"


def simulate_temperature_for_all_continents():
    continent_temperature_ranges = {
        'Africa': (-10, 40),       # Temperaturas médias de -10 a 40 °C
        'Antarctica': (-60, -10),  # Temperaturas médias de -60 a -10 °C
        'Asia': (-20, 50),         # Temperaturas médias de -20 a 50 °C
        'Australia': (0, 40),      # Temperaturas médias de 0 a 40 °C
        'Europe': (-10, 35),       # Temperaturas médias de -10 a 35 °C
        'North America': (-30, 45),# Temperaturas médias de -30 a 45 °C
        'South America': (-10, 40) # Temperaturas médias de -10 a 40 °C
    }

    temperature_results = []

    for continent, (temp_min, temp_max) in continent_temperature_ranges.items():
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        temperature_c = random.uniform(temp_min, temp_max)
        temperature_f = temperature_c * 9/5 + 32
        temperature_k = temperature_c + 273.15

        temperature_results.append({
            'continent': continent,
            'temperature': round(temperature_c, 2),
            'unit': 'C',
            'time':current_time
        })
        
        temperature_results.append({
            'continent': continent,
            'temperature': round(temperature_f, 2),
            'unit': 'F',
            'time':current_time
        })
        
    return temperature_results

def publish_temperature(client):
    temperature_list = simulate_temperature_for_all_continents()

    for result in temperature_list:

        message = {
            'temperature': result['temperature'],
            'type': result['unit'],
            'continent': result['continent'],
            'time': result['time']
        }

        if result['unit'] == 'C':
            client.publish(topic_c, json.dumps(message))
        elif result['unit'] == 'F':
            client.publish(topic_f, json.dumps(message))
        print(f"Publicado: {message}")

client = mqtt.Client("TemperatureSensor")
client.connect(broker_address)

try:
    while True:
        publish_temperature(client)
        time.sleep(30)
except KeyboardInterrupt:
    print("Sensor interrompido.")
finally:
    client.disconnect()
