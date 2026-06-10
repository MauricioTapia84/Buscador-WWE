#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import http.server
import socketserver

PORT = 8080
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

# Navegar a la raíz del proyecto para asegurar consistencia de ejecución
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SERVER_DIR, "..", ".."))
os.chdir(PROJECT_ROOT)

class OrugaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Habilitar CORS para facilitar desarrollo local si es necesario
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        # Endpoint health sencillo
        if self.path == '/health' or self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "ia-oruga-backend"}).encode('utf-8'))
            return
        if self.path == '/api/execute':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                command = data.get('command', '')
                
                if not command:
                    self.send_error_response("Comando vacío o no provisto.")
                    return
                
                print(f"[IA ORUGA BACKEND] Ejecutando comando local solicitado: {command}")
                
                # Ejecutar comando en el directorio del proyecto
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT
                )
                
                response_data = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "code": result.returncode
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except Exception as e:
                self.send_error_response(f"Error al ejecutar el comando: {str(e)}")

        elif self.path == '/api/write_file':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                filepath = data.get('filepath', '')
                content = data.get('content', '')
                
                if not filepath:
                    self.send_error_response("Falta el filepath.")
                    return
                
                full_path = os.path.abspath(os.path.join(PROJECT_ROOT, filepath))
                if not full_path.startswith(PROJECT_ROOT):
                    self.send_error_response("Intento de acceso fuera del workspace.")
                    return
                
                # Crear directorios padres si no existen
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"[IA ORUGA BACKEND] Archivo escrito localmente: {filepath}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": f"Archivo guardado con éxito en {filepath}."}).encode('utf-8'))
            except Exception as e:
                self.send_error_response(f"Error al escribir el archivo: {str(e)}")

        elif self.path == '/api/apply_diff':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                filepath = data.get('filepath', '')
                diff_text = data.get('diff', '')
                
                if not filepath or not diff_text:
                    self.send_error_response("Falta el filepath o el diff_text.")
                    return
                
                full_path = os.path.abspath(os.path.join(PROJECT_ROOT, filepath))
                if not full_path.startswith(PROJECT_ROOT):
                    self.send_error_response("Intento de acceso fuera del workspace.")
                    return
                
                if not os.path.exists(full_path):
                    self.send_error_response(f"El archivo {filepath} no existe.")
                    return
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse lines to find matches and make replacements
                diff_lines = [l.rstrip('\r\n') for l in diff_text.split('\n')]
                
                removes = []
                adds = []
                for line in diff_lines:
                    if line.startswith('-'):
                        removes.append(line[1:].lstrip(' '))
                    elif line.startswith('+'):
                        adds.append(line[1:].lstrip(' '))
                
                lines_in_file = content.split('\n')
                replaced = False
                
                if removes:
                    match_start = -1
                    match_len = len(removes)
                    for idx in range(len(lines_in_file) - match_len + 1):
                        slice_lines = [l.lstrip(' ') for l in lines_in_file[idx : idx + match_len]]
                        if slice_lines == removes:
                            match_start = idx
                            break
                    
                    if match_start != -1:
                        matched_first_line = lines_in_file[match_start]
                        space_count = len(matched_first_line) - len(matched_first_line.lstrip(' '))
                        indent = matched_first_line[:space_count]
                        
                        indented_adds = [indent + l for l in adds]
                        lines_in_file[match_start : match_start + match_len] = indented_adds
                        new_content = "\n".join(lines_in_file)
                        
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        replaced = True
                
                if replaced:
                    print(f"[IA ORUGA BACKEND] Parche diff aplicado localmente a: {filepath}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "message": f"Parche aplicado con éxito a {filepath}."}).encode('utf-8'))
                else:
                    self.send_error_response("No se pudo mapear el bloque a eliminar (diff) con las líneas del archivo. Verifica los cambios manualmente.")
            except Exception as e:
                self.send_error_response(f"Error al aplicar el parche: {str(e)}")

        else:
            self.send_error(404, "Endpoint no encontrado")

    def send_error_response(self, message):
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

def run():
    # Asegurar que el puerto se libere rápido al reiniciar
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, OrugaRequestHandler)
    print(f"==========================================================")
    echo_msg = f" 🐛 Servidor Activo de IA Oruga en el puerto {PORT}"
    print(echo_msg)
    print(f" Raíz del espacio de trabajo: {PROJECT_ROOT}")
    print(f" URL de la aplicación: http://localhost:{PORT}/agent/web/index.html")
    print(f"==========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[IA ORUGA BACKEND] Deteniendo servidor local...")
        httpd.server_close()
        sys.exit(0)

if __name__ == '__main__':
    run()
