import sys, os, datetime, jwt, json, base64
from flask import render_template, request, make_response, jsonify, Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from getIP import get_local_ip, get_port

ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'
SECRET_KEY1 = "senha_super_forte_123*"
SECRET_KEY2 = "qwerty"


def jwt_attack_functions(app):

    def create_token(id, role):
        payload = {
        "id": id,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY1, algorithm="HS256")
        return token

    def decode_token_without_validation(token):
        unverified_header = jwt.get_unverified_header(token)

        if unverified_header.get('alg').lower() == 'none':
            payload = jwt.decode(token, options={"verify_signature": False})
        elif unverified_header.get('alg') == 'HS256':
            payload = jwt.decode(token, SECRET_KEY1, algorithms=['HS256'])
        else:
            raise Exception("Algoritmo não suportado")
        return payload
    
    def decode_token(token):
        try:
            decoded_payload = jwt.decode(
                token,
                SECRET_KEY2,
                algorithms=["HS256"]
            )
            print(decoded_payload)
            return decoded_payload.get('role') == 'admin'
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def decode_token_hand_made(token):
        if token is not None:
            try:
                header_b64, payload_b64, signature_b64 = token.split('.')

                def fix_b64_padding(b64_string):
                    return b64_string + '=' * (-len(b64_string) % 4)

                header_json = base64.urlsafe_b64decode(fix_b64_padding(header_b64)).decode('utf-8')
                header = json.loads(header_json)

                payload_json = base64.urlsafe_b64decode(fix_b64_padding(payload_b64)).decode('utf-8')
                payload = json.loads(payload_json)

                return {
                    "header": header,
                    "payload": payload,
                    "signature": signature_b64
                }
            except Exception as e:
                return None
        return None
    
    def is_admin(token):
        try:
            payload = decode_token_without_validation(token)
            return payload.get('role') == 'admin'
        except Exception as e:
            return False

    def add_token_and_template(template):
        initial_user_token = create_token(1, 'user')
        rendered_html = render_template(
            template,
            ip=ip,
            port=port
        )
        resp = make_response(rendered_html)
        resp.set_cookie('jwt_token', initial_user_token, samesite='Lax')
        return resp
    
    @app.route('/cd691c63-6cb7-4f06-bb75-970c317f0c58-jwt-lvl-1', methods=['GET'])
    def lvl1_front_jwt():
        return add_token_and_template('lvl1-jwt.html')
    
    @app.route('/cd691c63-6cb7-4f06-bb75-970c317f0c58-jwt-lvl-1-back', methods=['POST'])
    def lvl1_back_jwt():
        data = request.get_json() or {}
        token = data.get('jwt', '')

        if not token:
            resp = make_response(jsonify({"error": "Você ainda não é admin"}), 401)
            resp.set_cookie('jwt_token', create_token(1, 'user'), samesite='Lax')
            return resp

        if decode_token_hand_made(token) is not None and decode_token_hand_made(token)['header']['alg'] == 'HS256' and decode_token_hand_made(token)['payload']['role'] == 'admin':
            response = make_response(jsonify({
                "path_level": f'{ROOT_INDEX}/9c4e8a52-7b88-4a60-bcf6-48c0c9c57e4c-jwt-lvl-2'
            }), 200)
        else:
            response = make_response(jsonify({"error": "Você ainda não é admin"}), 401)

        response.set_cookie('jwt_token', token, samesite='Lax')
        return response

    @app.route('/9c4e8a52-7b88-4a60-bcf6-48c0c9c57e4c-jwt-lvl-2', methods=['GET'])
    def lvl2_front_jwt():
        return add_token_and_template('lvl2-jwt.html')

    @app.route('/9c4e8a52-7b88-4a60-bcf6-48c0c9c57e4c-jwt-lvl-2-back', methods=['POST'])
    def lvl2_back_jwt():
        data = request.get_json() or {}
        token = data.get('jwt', '')

        if not token:
            resp = make_response(jsonify({"error": "Você ainda não é admin"}), 401)
            resp.set_cookie('jwt_token', create_token(1, 'user'), samesite='Lax')
            return resp

        if is_admin(token):
            response = make_response(jsonify({
                "path_level": f'{ROOT_INDEX}/f47ac10b-58cc-4372-a567-0e02b2c3d479-jwt-lvl-3'
            }), 200)
        else:
            response = make_response(jsonify({"error": "Você ainda não é admin"}), 401)

        response.set_cookie('jwt_token', token, samesite='Lax')
        return response
    
    @app.route('/f47ac10b-58cc-4372-a567-0e02b2c3d479-jwt-lvl-3', methods=['GET'])
    def lvl3_front_jwt():
        return add_token_and_template('lvl3-jwt.html')
    
    @app.route('/f47ac10b-58cc-4372-a567-0e02b2c3d479-jwt-lvl-3-back', methods=['POST'])
    def lvl3_back_jwt():
        data = request.get_json() or {}
        token = data.get('jwt', '')

        if not token:
            resp = make_response(jsonify({"error": "Você ainda não é admin"}), 401)
            resp.set_cookie('jwt_token', create_token(1, 'user'), samesite='Lax')
            return resp

        if decode_token(token):
            response = make_response(jsonify({
                "flag": 'FLAG${JWT-C0MPL3T3}'
            }), 200)
        else:
            response = make_response(jsonify({"error": "Você ainda não é admin"}), 401)

        response.set_cookie('jwt_token', token, samesite='Lax')
        return response

if __name__ == '__main__':
    app = Flask(__name__)
    print(jwt_attack_functions(app))