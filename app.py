
from flask import Flask, render_template
from flask_cors import CORS
from command_injection.command_inection import command_injection_functions
from sql_injection.sql_injection import sql_injection_functions


if __name__ == '__main__':
    
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    def home():
        return render_template('main.html')
    
    sql_injection_functions(app)
    command_injection_functions(app)
    app.run(debug=True, host='0.0.0.0', port=5001)
