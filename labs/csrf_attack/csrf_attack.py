import sys, os, datetime, jwt, json, base64
from flask import render_template, request, make_response, jsonify, Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from getIP import get_local_ip, get_port

ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'

print(ROOT_INDEX)