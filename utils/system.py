import os
import sqlite3
import sys

from flask import app, request, session
from getIP import get_local_ip, get_port

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'
flags = {
        "cmdi-lvl-1": f"{ROOT_INDEX}/2f8b1e6a-9c8d-4fd1-97b2-5db0cda55d0e-cmdi-lvl-2?domain=127.0.0.1",
        "cmdi-lvl-2": f"{ROOT_INDEX}/34f7e6a2-9b8c-4e17-82f1-3c5d9bfa2a11-cmdi-lvl-3?domain=127.0.0.1",
        "cmdi-lvl-3": "FLAG${Y0U-R0CK}",
        "sqli-lvl-1": f"{ROOT_INDEX}/3b82a2d2-5e4e-47b0-9e50-3bba8d4dc6de-sqli-lvl-2",
        "sqli-lvl-2": f"{ROOT_INDEX}/c431d46b-3db1-4728-b29c-25764d3be103-sqli-lvl-3",
        "sqli-lvl-3": "FLAG${SQL1-F1N1SH3D}",
        "csrf-lvl-1": "",
        "csrf-lvl-2": "",
        "csrf-lvl-3": "",
        "jwt-lvl-1": "{ROOT_INDEX}/9c4e8a52-7b88-4a60-bcf6-48c0c9c57e4c-jwt-lvl-2",
        "jwt-lvl-2": f"{ROOT_INDEX}/f47ac10b-58cc-4372-a567-0e02b2c3d479-jwt-lvl-3",
        "jwt-lvl-3": "FLAG${JWT-C0MPL3T3}",
        "ssrf-lvl-1": "",
        "ssrf-lvl-2": "",
        "ssrf-lvl-3": "",
        "bac-lvl-1": "",
        "bac-lvl-2": "",
        "bac-lvl-3": "",
        "race-cond-lvl-1": "",
        "race-cond-lvl-2": "",
        "race-cond-lvl-3": "",
        "xss-lvl-1": "",
        "xss-lvl-2": "",
        "xss-lvl-3": "",
    }

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'databases', 'users.db')
DB_FILE = os.path.abspath(DB_FILE)

def get_flags():
    return flags

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/validate-flag', methods=['POST'])
def validate_flag():
    user_id = session['user']['id']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM users
        WHERE id = (?)
    ''', (user_id,))
    user = cursor.fetchone()
    flag = request.args.get('flag')
    # if(flag in flags):
    # here goes the logic for adding the new flag to
    # the user's register if it's valid