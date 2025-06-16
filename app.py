
from flask import Flask, render_template
from flask_cors import CORS
from command_injection.command_injection import command_injection_functions
from sql_injection.sql_injection import sql_injection_functions
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from getIP import get_local_ip, get_port


ip = get_local_ip()
port = get_port()

if __name__ == '__main__':
    
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    def home():
        return render_template('main.html', ip=ip, port=port)
    
    sql_injection_functions(app)
    command_injection_functions(app)
    app.run(debug=True, host='0.0.0.0', port=port)
