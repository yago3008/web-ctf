
from flask import Flask, render_template, session, jsonify
from datetime import timedelta
from flask_cors import CORS
from labs.command_injection.command_injection import command_injection_functions
from labs.sql_injection.sql_injection import sql_injection_functions
from labs.jwt_attack.jwt_attack import jwt_attack_functions
from labs.csrf_attack.csrf_attack import csrf_attack_functions
from utils.user import user_routes
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from getIP import get_local_ip, get_port


ip = get_local_ip()
port = get_port()

if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    app.secret_key = '*adminnimda*'
    app.permanent_session_lifetime = timedelta(days=7)
    app.config.update(
    SESSION_COOKIE_SAMESITE=None,
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False
    )      

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.route('/')
    def home():
        return render_template('main.html', ip=ip, port=port)
    
    @app.route('/adm')
    def adm_route():
        print(session)
        if 'user' not in session:
            return jsonify({'status': 'fail', 'message': 'Usuario não autenticado'}), 401
        return jsonify({'status': 'ok', 'message': 'Usuario autenticado'}), 200
    
    user_routes(app)
    sql_injection_functions(app)
    command_injection_functions(app)
    jwt_attack_functions(app)
    csrf_attack_functions(app)

    app.run(debug=True, host='0.0.0.0', port=port)
