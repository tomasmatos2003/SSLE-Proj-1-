import time
import requests
import json

login_url = "http://10.151.101.12:5000/auth/login"
temps_url = "http://10.151.101.153:5003/temps"

login_data = {
    "username": "ssle",
    "password": "ssle"
}

proxies = {
    "http": "http://10.151.101.165:8080",  
    "https": "http://10.151.101.165:8080"
}

def get_auth_token():
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(login_url, headers=headers, data=json.dumps(login_data), proxies=proxies)
        
        if response.status_code == 200:
            print("Login successful!")
            token = response.json().get("token")
            if token:
                return token
            else:
                print("Token not found in the response.")
        else:
            print(f"Login failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return None

def get_temperature_data(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(temps_url, headers=headers, proxies=proxies)
        
        if response.status_code == 200:
            print("Temperature data retrieved successfully!")
            print(response.json())  
        else:
            print(f"Failed to retrieve temperature data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error during temperature data request: {e}")

def start_consuming():
    token = get_auth_token()
    if not token:
        print("Exiting. No valid token found.")
        return

    while True:
        get_temperature_data(token)
        
        time.sleep(30)

if __name__ == "__main__":
    start_consuming()

