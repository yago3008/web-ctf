import os, subprocess, re, urllib, sys
from flask import Flask, request, g, make_response, redirect, render_template, jsonify, session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from getIP import get_local_ip, get_port


ip = get_local_ip()
port = get_port()
ROOT_INDEX = f'http://{ip}:{port}'
BLACKLIST_PATTERNS = [
    r'\brm\b', r'\brmdir\b'
]
TRAVERSAL_PATTERNS = [
    r'\.\.', r'\.\./', r'\.\.\\', r'%2e%2e', r'%2e%2f', r'%2f%2e', r'\\\.\.', r'/\.\.', r'\bcd\b', r'/'
]

def command_injection_functions(app):
    def setup_ctf_dirs():
        dirs = [
            "1d8f3d1a-b55b-4d23-b1cd-fd3d1e8a67e9-cmdi-lvl-1",
            "2f8b1e6a-9c8d-4fd1-97b2-5db0cda55d0e-cmdi-lvl-2",
            "34f7e6a2-9b8c-4e17-82f1-3c5d9bfa2a11-cmdi-lvl-3"
        ]
        flags = {
            "1d8f3d1a-b55b-4d23-b1cd-fd3d1e8a67e9-cmdi-lvl-1": flags["cmdi-lvl-1"],
            "2f8b1e6a-9c8d-4fd1-97b2-5db0cda55d0e-cmdi-lvl-2": flags["cmdi-lvl-2"],
            "34f7e6a2-9b8c-4e17-82f1-3c5d9bfa2a11-cmdi-lvl-3": flags["cmdi-lvl-3"]
        }
        
        for i, d in enumerate(dirs):
            os.makedirs(d, exist_ok=True)
            flag_path = os.path.join(d, f"flag-{i+1}.txt")
            with open(flag_path, "w") as f:
                f.write(flags[d])

    def is_blocked():
        block_cookie = request.cookies.get("block")
        if block_cookie == "1": return True
        return False

    def assign_cookie():
        resp = make_response(redirect("/"))
        resp.set_cookie("block", "1")
        return resp

    def is_domain_in_blacklist(domain):
        for pattern in BLACKLIST_PATTERNS:
            if re.search(pattern, domain, flags=re.IGNORECASE):
                return True
        return False

    def is_path_traversal(payload):
        decoded = urllib.parse.unquote(payload)
        for pattern in TRAVERSAL_PATTERNS:
            if re.search(pattern, decoded, flags=re.IGNORECASE):
                return True
        return False

    def run_rules(domain):
        if is_blocked(): return f"<pre>Seu IP Esta Bloqueado!</pre>"
        if is_domain_in_blacklist(domain): return assign_cookie()
        if is_path_traversal(domain): return f"<pre>Travessia de Diretorio Detectada!</pre>"

    @app.route('/1d8f3d1a-b55b-4d23-b1cd-fd3d1e8a67e9-cmdi-lvl-1', methods=['GET'])
    def lvl1_front_cmdi():
        return render_template('command_injection/lvl1-cmdi.html', ip=ip, port=port)
    
    @app.route('/1d8f3d1a-b55b-4d23-b1cd-fd3d1e8a67e9-cmdi-lvl-1-back', methods=['GET'])
    def lvl1_back_cmdi():
        domain = request.args.get('domain', '127.0.0.1')
        resp = run_rules(domain)
        if resp is not None: return resp

        blocked_cmd = ['vi', 'nano', 'vim']

        for b_cmd in blocked_cmd:
            if b_cmd in domain:
                return f'Erro: Comando nao permitido, tente bypassar esse filtro!'

        try:
            result = subprocess.run(f'cd ./1d8f3d1a-b55b-4d23-b1cd-fd3d1e8a67e9-cmdi-lvl-1 && ping -W 2 -c 1 {domain}', shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            return jsonify({"result": output}), 200
        except Exception as e:
            return jsonify({"error": f"Erro ao executar comando: {str(e)}"}), 500

    @app.route('/2f8b1e6a-9c8d-4fd1-97b2-5db0cda55d0e-cmdi-lvl-2', methods=['GET'])
    def lvl2_front_cmdi():
        return render_template('command_injection/lvl2-cmdi.html', ip=ip, port=port)
        
    @app.route('/2f8b1e6a-9c8d-4fd1-97b2-5db0cda55d0e-cmdi-lvl-2-back', methods=['GET'])
    def lvl2_back_cmdi():
        domain = request.args.get('domain', '127.0.0.1')
        resp = run_rules(domain)
        if resp is not None: return resp
        
        blocked_cmd = [' ',';', '&&', '||', 'vi', 'nano', 'vim']

        for b_cmd in blocked_cmd:
            if b_cmd in domain:
                return jsonify({"error": "Comando nao permitido, tente bypassar esse filtro!"}), 400
        try:
            result = subprocess.run(f'cd ./2f8b1e6a-9c8d-4fd1-97b2-5db0cda55d0e-cmdi-lvl-2 && ping -W 2 -c 1 {domain}', shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            first_line = (result.stdout + result.stderr).strip().split('\n')[0]
            if 'Name or service' in first_line:
                return jsonify({"result": f"Safadinho tentou pegar erro, isso aqui nao vai te retornar erros verbosos!"}), 200    
            return jsonify({"result": output}), 200
        
        except Exception as e:
            return jsonify({"error": f"Erro ao executar comando: {str(e)}"}), 500

    @app.route('/34f7e6a2-9b8c-4e17-82f1-3c5d9bfa2a11-cmdi-lvl-3', methods=['GET'])
    def lvl3_front_cmdi():
        return render_template('command_injection/lvl3-cmdi.html', ip=ip, port=port)
    
    @app.route('/34f7e6a2-9b8c-4e17-82f1-3c5d9bfa2a11-cmdi-lvl-3-back', methods=['GET'])
    def lvl3_back_cmdi():
        domain = request.args.get('domain', '127.0.0.1')
        resp = run_rules(domain)
        if resp is not None: return resp

        blocked_cmd = ['\'', ';', '&&', ' ', '|', '&', '||', 'curl', 'wget', 'vi', 'nano', 'vim']

        for b_cmd in blocked_cmd:
            if b_cmd in domain.lower():
                return jsonify({"error": "Comando nao permitido, tente bypassar esse filtro!"}), 400
            
        try:
            result = subprocess.run(f'cd ./34f7e6a2-9b8c-4e17-82f1-3c5d9bfa2a11-cmdi-lvl-3 && ping -W 2 {domain} -c1', shell=True, capture_output=True, text=True)
            first_line = (result.stdout + result.stderr).strip().split('\n')[0]
            if 'Name or service' in first_line or 'cannot resolve' in first_line:
                return jsonify({"result": f"Safadinho tentou pegar erro, isso aqui nao vai te retornar erros verbosos!"}), 200 
            return jsonify({"result": f"Comando Executado: ping -W 2 {domain} -c1\nResult: {first_line}"}), 200
        except Exception as e:
            return jsonify({"error": f"Erro ao executar comando: {str(e)}"}), 500
        
    setup_ctf_dirs()

if __name__ == '__main__':
    print(ROOT_INDEX)