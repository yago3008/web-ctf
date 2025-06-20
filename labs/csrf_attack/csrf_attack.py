import sys, os, datetime, jwt, json, base64
import requests as req
from flask import render_template, request, make_response, jsonify, Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from getIP import get_local_ip, get_port

ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'

def csrf_attack_functions(app):
    def get_bot_session(login_url):
        s = req.Session()
        data = {
            'username': 'bot',
            'password': 'botbot'
        }
        response = s.post(login_url, json=data)
        if response.status_code == 200:
            print("Login realizado com sucesso. Cookies obtidos:")
            for cookie in s.cookies:
                print(f'{cookie.name} = {cookie.value}')
            return s
        else:
            print(f'Falha no login: {response.status_code}')
            return None

    def bot_request_with_cookies(session, url_csrf, payload=None):
        if session is None:
            print("Sessão inválida. Faça o login primeiro.")
            return None
        response = session.post(url_csrf, json=payload) if payload else session.get(url_csrf)
        print(f'Requisição para {url_csrf} retornou {response.text}')
        return response

    @app.route('/3b8f23c4-9c5a-4f27-8d3d-5fcb5b3e2746-csrf-lvl-1', methods=['GET'])
    def lvl1_front_csrf():
        return render_template('csrf_attack/lvl1-csrf.html')
    
    @app.route('/3b8f23c4-9c5a-4f27-8d3d-5fcb5b3e2746-csrf-lvl-1-back', methods=['POST'])
    def lvl1_back_csrf():
        data = request.get_json() or {}
        csrf_url = data.get('csrf_url', '')


    sess = get_bot_session('http://192.168.1.66:5001/login-back')
    bot_request_with_cookies(sess, 'http://192.168.1.66:5001/adm')
if __name__ == '__main__':
    app = Flask(__name__)
    csrf_attack_functions(app)