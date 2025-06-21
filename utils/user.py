from flask import Flask, request, jsonify, session, render_template
import sqlite3, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from getIP import get_local_ip, get_port
from system import get_flags

ip = get_local_ip()
port = get_port()
DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'databases', 'users.db')
DB_FILE = os.path.abspath(DB_FILE)

def user_routes(app):
    app.secret_key = '*adminnimda*'
    def init_db():
        if not os.path.exists(DB_FILE):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    flags TEXT DEFAULT ''
                )
            ''')
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('bot', 'botbot'))
            conn.commit()
            conn.close()

    init_db()

    def get_db():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    @app.route('/register', methods=['GET'])
    def register_front():
        return render_template('user/register.html', ip=ip, port=port)
    
    @app.route('/register-back', methods=['POST'])
    def register_back():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password required'}), 400

        conn = get_db()

        # Verificar se o usuário já existe
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Username already exists'}), 409

        # Se não existir, cria
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'User registered'})

    @app.route('/login', methods=['GET'])
    def login_front():
        return render_template('user/login.html', ip=ip, port=port)

    @app.route('/login-back', methods=['POST'])
    def login_back():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user'] = {
                'id':user['id'],
                'username':user['username']
            }
            print(dict(user))
            return jsonify({'status': 'success', 'message': 'Logged in', 'points': user['points'], 'flags': user['flags']}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    @app.route('/change-password', methods=['POST'])
    def change_password():
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

        data = request.json
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({'status': 'error', 'message': 'New password required'}), 400
        user_id = session['user']['id']
        
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
            conn.commit()
            conn.close()
            return jsonify({'status': 'ok', 'message': 'Password updated successfully'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Failed to update password: {str(e)}'}), 500
    
    @app.route('/logout')
    def logout():
        session.clear()
        return jsonify({'status': 'ok', 'message': 'Logout completo'}), 200
    
    @app.route('/profile-back', methods=['GET'])
    def profile():
        username = session.get('username')
        if not username:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user:
            return jsonify({
                'username': user['username'],
                'points': user['points'],
                'flags': user['flags']
            })
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

if __name__ == '__main__':
    pass
