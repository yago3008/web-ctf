import sys, os, datetime, jwt
from flask import render_template, request, make_response, jsonify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from getIP import get_local_ip, get_port

ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'
SECRET_KEY1 = "senha_super_forte_123*"
SECRET_KEY2 = "qwerty"
SECRET_KEY3 = "senha_super_forte_*321"

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

        if unverified_header.get('alg') == 'none':
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
                SECRET_KEY1,
                algorithms=["HS256"]
            )
            return decoded_payload
        except jwt.ExpiredSignatureError:
            print("Token expirado!")
        except jwt.InvalidTokenError:
            print("Token inválido!")

    def is_admin(token):
        try:
            payload = decode_token_without_validation(token)
            return payload.get('role') == 'admin'
        except Exception as e:
            print(f"Erro ao decodificar token: {e}")
            return False
        
    @app.route('/9c4e8a52-7b88-4a60-bcf6-48c0c9c57e4c-jwt-lvl-1', methods=['GET'])
    def lvl1_front_jwt():
        initial_user_token = create_token(1, 'user')
        rendered_html = render_template(
            'lvl1-jwt.html',
            ip=ip,
            port=port
        )
        resp = make_response(rendered_html)
        resp.set_cookie('jwt_token', initial_user_token, httponly=True, samesite='Lax')
        return resp

    @app.route('/9c4e8a52-7b88-4a60-bcf6-48c0c9c57e4c-jwt-lvl-1-back', methods=['POST'])
    def lvl1_back_jwt():
        data = request.get_json() or {}
        token = data.get('jwt', '')

        if not token:
            resp = make_response(jsonify({"error": "Você ainda não é admin"}), 401)
            resp.set_cookie('jwt_token', create_token(1, 'user'), httponly=True, samesite='Lax')
            return resp

        if is_admin(token):
            response = make_response(jsonify({
                "path_level": f'{ROOT_INDEX}/f47ac10b-58cc-4372-a567-0e02b2c3d479-jwt-lvl-2'
            }), 200)
        else:
            response = make_response(jsonify({"error": "Você ainda não é admin"}), 401)

        response.set_cookie('jwt_token', token, httponly=True, samesite='Lax')
        return response

if __name__ == '__main__':
    print(jwt_attack_functions())