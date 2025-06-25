import sys, os, sqlite3
import requests as req
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from flask import render_template, request, make_response, jsonify, Flask, session
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from getIP import get_local_ip, get_port

DB_FILE = os.path.join(os.path.dirname(__file__), '../..', 'databases', 'users.db')
DB_FILE = os.path.abspath(DB_FILE)
ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'
bot_cookie = ''

def csrf_attack_functions(app):
    def get_db():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    def get_bot_browser(login_url):
        # Configurar o navegador
        options = Options()
        options.add_argument("--headless")  # Se quiser rodar em background
        driver = webdriver.Chrome(options=options)

        # Acessa a página de login
        driver.get(login_url)

        # Preenche o formulário de login (ajuste conforme os campos reais)
        driver.find_element(By.NAME, "username").send_keys("bot")
        driver.find_element(By.NAME, "password").send_keys(get_bot_password())

        # Submete o formulário
        driver.find_element(By.TAG_NAME, "form").submit()

        # Espera carregar e sessão ser criada
        time.sleep(1)

        return driver

    def bot_open_csrf_link(driver, malicious_url):
        # Agora o navegador já está com o cookie de sessão do bot
        driver.get(malicious_url)
        time.sleep(2)  # Dá tempo pro JavaScript do atacante executar o CSRF

        print(driver.page_source)
        driver.quit()

    def get_bot_password():
        conn = get_db()
        user = conn.execute('SELECT password FROM users WHERE username = ?', ('bot',)).fetchone()
        conn.close()

        if user:
            password = user[0]
            return password
        else:
            return None

    @app.route('/3b8f23c4-9c5a-4f27-8d3d-5fcb5b3e2746-csrf-lvl-1', methods=['GET'])
    def lvl1_front_csrf():
        return render_template('csrf_attack/lvl1-csrf.html', ip=ip, port=port)
    
    @app.route('/3b8f23c4-9c5a-4f27-8d3d-5fcb5b3e2746-csrf-lvl-1-back', methods=['POST'])
    def lvl1_back_csrf():
        data = request.get_json() or {}
        csrf_url = data.get('url', '')
        current_bot_password = get_bot_password()

        driver = get_bot_browser(f'{ROOT_INDEX}/login')
        bot_open_csrf_link(driver, csrf_url)

        if current_bot_password != get_bot_password():
            return jsonify({"result": 'FLAG-PINTO'}), 200
        return jsonify({"error": 'error to connect to your link or password has not changed'}), 500

if __name__ == '__main__':
    pass
    app = Flask(__name__)
    csrf_attack_functions(app)