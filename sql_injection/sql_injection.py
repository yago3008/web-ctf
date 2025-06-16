import sqlite3, os, base64, time,sys
from flask import Flask, request, g, render_template, jsonify
from glob import glob
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from getIP import get_local_ip, get_port

ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'
DB_FOLDER = 'databases'

def sql_injection_functions(app):
    DB_CONFIG = {
        'lvl1': os.path.join(DB_FOLDER, 'lvl1_database.db'),
        'lvl2': os.path.join(DB_FOLDER, 'lvl2_database.db'),
        'lvl3': os.path.join(DB_FOLDER, 'lvl3_database.db'),
    }

    def sleep(seconds):
        time.sleep(seconds)

    def database():
        return "lvl3_database.db"

    def get_db(db_key='lvl1'):
        if db_key not in DB_CONFIG:
            raise ValueError(f"Chave de banco de dados '{db_key}' nao configurada.")

        db_path = DB_CONFIG[db_key]
        if not hasattr(g, '_database_connections'):
            g._database_connections = {}

        if db_path not in g._database_connections:
            conn = sqlite3.connect(db_path)
            conn.create_function("sleep", 1, sleep)
            conn.create_function("database", 0, database)
            conn.create_function("db_name", 0, database)
            conn.row_factory = sqlite3.Row
            g._database_connections[db_path] = conn
        return g._database_connections[db_path]

    def get_result(db_conn, query):
        cursor = db_conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    @app.teardown_appcontext
    def close_connections(exception):
        if hasattr(g, '_database_connections'):
            for db_conn in g._database_connections.values():
                db_conn.close()

    def init_db_lvl1():
        with app.app_context():
            db = get_db('lvl1')
            schema_sql = f"""
                DROP TABLE IF EXISTS users;

                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    email TEXT
                );

                INSERT INTO users (username, password, email) VALUES
                ('admin', 'password', 'admin@gmail.com'),
                ('{ROOT_INDEX}/3b82a2d2-5e4e-47b0-9e50-3bba8d4dc6de-sqli-lvl-2', '{ROOT_INDEX}/3b82a2d2-5e4e-47b0-9e50-3bba8d4dc6de-sqli-lvl-2', '{ROOT_INDEX}/3b82a2d2-5e4e-47b0-9e50-3bba8d4dc6de-sqli-lvl-2'),
                ('bob', 'bob_secret', 'bob@gmail.com'),
                ('charlie', 'charliepass', 'charlie@gmail.com');
            """
            db.cursor().executescript(schema_sql)
            db.commit()

    def init_db_lvl2():
        with app.app_context():
            db = get_db('lvl2')
            schema_sql = f"""
                DROP TABLE IF EXISTS users;

                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    cpf TEXT
                );

                INSERT INTO users (username, cpf) VALUES
                ('admin', '47455178824'),
                ('root', '00000000000'),
                ('{ROOT_INDEX}/c431d46b-3db1-4728-b29c-25764d3be103-sqli-lvl-3', '{ROOT_INDEX}/c431d46b-3db1-4728-b29c-25764d3be103-sqli-lvl-3'),
                ('charlie', '32241248843');
            """
            db.cursor().executescript(schema_sql)
            db.commit()

    def init_db_lvl3():
        with app.app_context():
            db = get_db('lvl3')

            # Criação da tabela
            schema_sql = """
                DROP TABLE IF EXISTS images;

                CREATE TABLE images (
                    id INTEGER PRIMARY KEY,
                    image_data TEXT NOT NULL,
                    flag TEXT NOT NULL
                );
            """
            db.cursor().executescript(schema_sql)

            image_folder = os.path.join(os.path.dirname(__file__), os.pardir, 'images')

            cursor = db.cursor()

            for i in range(1, 6):
                pattern = os.path.join(image_folder, f'image{i}.*')
                matched_files = glob(pattern)

                if not matched_files:
                    print(f'Imagem image{i} não encontrada.')
                    continue

                image_path = matched_files[0]
                with open(image_path, 'rb') as img_file:
                    b64_data = base64.b64encode(img_file.read()).decode('utf-8')
                    cursor.execute("INSERT INTO images (id, image_data, flag) VALUES (?, ?, ?)", (i, b64_data, "FLAG-SQLI_FINISHED"))

            db.commit()

    @app.route('/82eec8cf-d431-42d8-b6cd-08c2fd40bdf7-sqli-lvl-1', methods=['GET'])
    def lvl1_front_sqli():
        return render_template('lvl1-sqli.html', ip=ip, port=port)

    @app.route('/82eec8cf-d431-42d8-b6cd-08c2fd40bdf7-sqli-lvl-1-back', methods=['GET'])
    def lvl1_back_sqli():
        username_param = request.args.get('username', '')

        sql_query = f"SELECT * from users WHERE username = '{username_param}'"
        print(f"Executando query: {sql_query}")

        db = get_db('lvl1')

        response_data = {}
        try:
            results = get_result(db, sql_query)

            if results:
                users_list = []
                for row in results:
                    users_list.append({
                        "id": row['id'],
                        "username": row['username'],
                        "password": row['password'],
                        "email": row['email']
                    })
                response_data = {"message": "Informacoes do usuario encontradas!", "data": users_list}
            else:
                response_data = {"message": f"Nenhum resultado encontrado para '{username_param}'."}
        except sqlite3.Error as e:
            response_data = {"error": f"ERRO SQL: {str(e)}"}
            return jsonify(response_data), 500

        return jsonify(response_data), 200

    @app.route('/3b82a2d2-5e4e-47b0-9e50-3bba8d4dc6de-sqli-lvl-2', methods=['GET'])
    def lvl2_front_sqli():
        return render_template('lvl2-sqli.html', ip=ip, port=port)

    @app.route('/3b82a2d2-5e4e-47b0-9e50-3bba8d4dc6de-sqli-lvl-2-back', methods=['GET'])
    def lvl2_back_sqli():
        cpf = request.args.get('cpf', '474.551.788-24')

        
        sql_query = f"SELECT * FROM users WHERE cpf = REPLACE(REPLACE('{cpf}', '.', ''), '-', '')"
        print(f"Executando query: {sql_query}")

        db = get_db('lvl2')

        response_data = {}
        try:
            results = get_result(db, sql_query)

            if results:
                users_list = []
                for row in results:
                    users_list.append({
                        "id": row['id'],
                        "username": row['username'],
                        "cpf": row['cpf']
                    })
                response_data = {"message": "Informacoes do usuario encontradas!", "data": users_list}
            else:
                response_data = {"message": f"Nenhum resultado encontrado para '{cpf}'."}
        except sqlite3.Error as e:
            response_data = {"error": f"ERRO SQL: {str(e)}"}

            return jsonify(response_data), 500
        return jsonify(response_data), 200

    @app.route('/c431d46b-3db1-4728-b29c-25764d3be103-sqli-lvl-3', methods=['GET'])
    def lvl3_front_sqli():
        return render_template('lvl3-sqli.html', ip=ip, port=port)

    @app.route('/c431d46b-3db1-4728-b29c-25764d3be103-sqli-lvl-3-back', methods=['GET'])
    def lvl3_back_sqli():
        image_id = request.args.get('id', '')

        sql_query = f"SELECT image_data FROM images WHERE id = {image_id}"
        print(f"Executando query para imagem: {sql_query}")

        db = get_db('lvl3')

        response_data = {}
        try:
            results = get_result(db, sql_query)
            image1 = get_result(db, "SELECT image_data FROM images WHERE id = 1")

            if results:
                image_base64 = results[0]['image_data']
                full_image_data = f"data:image/jpeg;base64,{image_base64}"
                response_data = {
                    "message": "Imagem encontrada!",
                    "image_data": full_image_data
                }
            else:
                image_base64 = image1[0]['image_data']
                full_image_data = f"data:image/jpeg;base64,{image_base64}"
                response_data = {
                    "message": "Imagem encontrada!",
                    "image_data": full_image_data
                }
        except sqlite3.Error as e:
                image1 = get_result(db, "SELECT image_data FROM images WHERE id = 1")
                image_base64 = image1[0]['image_data']
                full_image_data = f"data:image/jpeg;base64,{image_base64}"
                response_data = {
                    "message": "Imagem encontrada!",
                    "image_data": full_image_data
                }
        return jsonify(response_data), 200


    def start_all_dbs():
        init_db_lvl1()
        init_db_lvl2()
        init_db_lvl3()

    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    start_all_dbs()
