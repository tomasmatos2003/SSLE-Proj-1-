from prometheus_client import start_http_server, Gauge
import requests
import time
from datetime import datetime
import logging

today_date = datetime.now().strftime('%Y-%m-%d')

logging.basicConfig(
    filename='/var/log/botnetattack.log',
    level=logging.INFO,
    format='%(message)s'
)

health_metric = Gauge(
    'service_health',
    'Health status of the service (1 for up, 0 for down)', 
    ['service']
)

response_time_metric = Gauge(
    'service_avg_response_time', 
    'Average time (seconds) to get 10 responses from the service', 
    ['service']
)

login_data = {
    "username": "ssle",
    "password": "ssle"
}

def get_token():
    try:
        response = requests.post("http://10.151.101.12:5000/auth/login", json=login_data)
        response.raise_for_status()
        token = response.json().get('token')
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching token: {e}")
        return None

TOKEN = get_token()
if TOKEN is None:
    raise SystemExit("Failed to obtain token, exiting...")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

SERVICES = [
    'http://10.151.101.12:5000/services',  #registy
    'http://10.151.101.12:5000/services/1',
    'http://10.151.101.12:5000/services/F',
    'http://10.151.101.153:5003/temps',  # Temperaturas C
    f'http://10.151.101.153:5003/temps_of_day?date={today_date}',  # Temperatures for today
    'http://10.151.101.153:5003/tempsbyConti?continent=africa',
    'http://10.151.101.136:5004/temps',  # Temperaturas C
    f'http://10.151.101.136:5004/temps_of_day?date={today_date}',  # Temperatures for today
    'http://10.151.101.136:5004/tempsbyConti?continent=africa'
]

previous_status = {service: None for service in SERVICES}

def measure_response_time(service):
    total_time = 0
    successful_responses = 0
    
    for _ in range(10):
        try:
            start_time = time.time()
            response = requests.get(service, headers=HEADERS, timeout=5)
            elapsed_time = time.time() - start_time
            if response.status_code == 200:
                total_time += elapsed_time
                successful_responses += 1
        except requests.exceptions.RequestException:
            pass

    if successful_responses > 0:
        return total_time / successful_responses
    else:
        return None

def check_service_health():
    for service in SERVICES:
        try:
            response = requests.get(service, headers=HEADERS)
            current_status = 1 if response.status_code == 200 else 0
        except requests.exceptions.RequestException:
            current_status = 0
        
        if previous_status[service] != current_status:
            print(f"{datetime.now()} - Service: {service}, Status Changed to: {current_status}")
            health_metric.labels(service=service).set(current_status)
            previous_status[service] = current_status
        
        avg_response_time = measure_response_time(service)
        if avg_response_time is not None:
            response_time_metric.labels(service=service).set(avg_response_time)
            
            if avg_response_time > 0.4:
                print(f"ALERT: Potential Botnet Attack detected on {service} - Avg Response Time: {avg_response_time:.2f}s")

                service_ip = service.split('/')[2]
                
                log_entry = f"10.151.101.23 - - [{datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')}] \"POST /botnetattack/{service_ip} HTTP/1.1\" 400 42 \"curl/8.10.1\""
                logging.info(log_entry)
        else:
            response_time_metric.labels(service=service).set(float('inf'))
            print(f"{datetime.now()} - Service: {service}, Failed to measure response time")

if __name__ == '__main__':
    start_http_server(8000)
    
    while True:
        check_service_health()
        time.sleep(20)

