import json
import logging
from flask import Flask, jsonify, request
from logging.handlers import RotatingFileHandler
import time
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

services = []
SECRET_KEY = "your_secret_key"

log_file_path = '/var/log/flask/app.log'

log_handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.INFO)

log_format = '%(remote_addr)s - - [%(asctime)s] "%(request_method)s %(request_url)s HTTP/1.1" %(status_code)s %(content_length)s "%(user_agent)s"'

formatter = logging.Formatter(log_format, datefmt='%d/%b/%Y:%H:%M:%S %z')
log_handler.setFormatter(formatter)

app.logger.addHandler(log_handler)

app.logger.setLevel(logging.INFO)

@app.before_request
def log_request():
    user_agent = request.headers.get('User-Agent', '-')
    
    extra = {
        'remote_addr': request.remote_addr,
        'request_method': request.method,
        'request_url': request.path,
        'status_code': 200,  # Placeholder for status code (updated in after_request)
        'content_length': len(request.data) or 0,  # Set content_length to 0 if no data
        'user_agent': user_agent,
   }

    app.logger.info('Request received', extra=extra)


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


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == 'ssle' and password == 'ssle':
        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200
    

    return jsonify({"message": "Invalid username or password"}), 401



@app.route('/services', methods=['GET'])
@token_required
def get_services():
    return jsonify(services)

@app.route('/services/<int:id>', methods=['GET'])
@token_required
def get_services_by_id(id: int):
    for service in services:
        if service['id'] == id:
            return jsonify(service)
    return jsonify({'error': 'Service does not exist'}), 404

@app.route('/services/<string:type>', methods=['GET'])
@token_required
def get_services_by_type(type: str):
    for service in services:
        if service['type'] == type:
            return jsonify(service)
    return jsonify({'error': 'Service does not exist'}), 404


@app.route('/services', methods=['POST'])
def create_services():
    new_service = request.form.to_dict()

    if services:
        new_id = max(service['id'] for service in services) + 1
    else:
        new_id = 1

    new_service['id'] = new_id

    urls = [service['url'] for service in services]
    if new_service['url'] not in urls:
        services.append(new_service)
        return jsonify(new_service), 201
    return jsonify(new_service), 409

@app.after_request
def log_response(response):
    status_code = response.status_code
    content_length = response.content_length if response.content_length is not None else 0

    extra = {
        'remote_addr': request.remote_addr,
        'request_method': request.method,
        'request_url': request.path,
        'status_code': status_code,
        'content_length': content_length,
        'user_agent': request.headers.get('User-Agent', '-'),
    }

    app.logger.info('Response sent', extra=extra)

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

