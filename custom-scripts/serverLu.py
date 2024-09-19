import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import os
import re

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 8000

class MeuManipulador(BaseHTTPRequestHandler):

    def tempo(self):
        try:
            with open('/proc/uptime', 'r') as f:
                tempo_atividade_segundos = float(f.readline().split()[0])
                return tempo_atividade_segundos
        except Exception as e:
            return f"erro: {e}"

    def info_cpu(self):
        try:
            with open('/proc/cpuinfo', 'r') as f:
                linhas = f.readlines()
                modelo_cpu = ""
                velocidade_cpu = ""
                for linha in linhas:
                    if "model name" in linha:
                        modelo_cpu = linha.split(":")[1].strip()
                    if "cpu MHz" in linha:
                        velocidade_cpu = linha.split(":")[1].strip()
                return modelo_cpu, velocidade_cpu
        except Exception as e:
            return f"erro: {e}", ""

    def uso_cpu(self):
        try:
            with open('/proc/stat', 'r') as f:
                fields = f.readline().split()
                tempo_ocioso = int(fields[4])
                tempo_total = sum(int(campo) for campo in fields[1:])
                return 100 - (tempo_ocioso * 100 / tempo_total)
        except Exception as e:
            return f"erro: {e}"

    def info_memoria(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                linhas = f.readlines()
                memoria_total = int(linhas[0].split()[1]) // 1024  # Converter para MB
                memoria_livre = int(linhas[1].split()[1]) // 1024  # Converter para MB
                memoria_usada = memoria_total - memoria_livre
                return memoria_total, memoria_usada
        except Exception as e:
            return f"erro: {e}", 0

    def versao_os(self):
        try:
            with open('/proc/version', 'r') as f:
                return f.readline().strip()
        except Exception as e:
            return f"erro: {e}"

    def processos(self):
        try:
            pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
            lista_processos = []
            for pid in pids:
                try:
                    with open(f'/proc/{pid}/comm', 'r') as f:
                        nome_processo = f.readline().strip()
                    lista_processos.append(f"PID: {pid}, Nome: {nome_processo}")
                except Exception:
                    continue
            return lista_processos
        except Exception as e:
            return [f"erro: {e}"]

    def particoes(self):
        try:
            with open('/proc/partitions', 'r') as f:
                linhas = f.readlines()[2:]  # Ignora as duas primeiras linhas do cabeçalho
                lista_particoes = []
                for linha in linhas:
                    campos = linha.split()
                    if len(campos) == 4:
                        nome = campos[3]
                        if nome.startswith(('sda', 'sdb', 'sdc')):
                            tamanho = int(campos[2]) * 1024  # Tamanho em bytes
                            tamanho_gb = tamanho / (1024 ** 3)  # Convertendo para GB
                            lista_particoes.append(f"Partição: {nome}, Tamanho: {tamanho_gb:.2f} GB")
                return lista_particoes
        except Exception as e:
            return [f"erro: {e}"]

    def dispositivos_usb(self):
        try:
            usb_info = []
            usb_path = '/sys/bus/usb/devices/'
            
            for device in os.listdir(usb_path):
                device_path = os.path.join(usb_path, device)
                
                if os.path.isdir(device_path):
                    # id forn e id produto
                    try:
                        with open(os.path.join(device_path, 'idVendor'), 'r') as f:
                            vendor_id = f.read().strip()
                        
                        with open(os.path.join(device_path, 'idProduct'), 'r') as f:
                            product_id = f.read().strip()
                        
                        # porta
                        try:
                            with open(os.path.join(device_path, 'busnum'), 'r') as f:
                                bus_number = f.read().strip()
                            
                            with open(os.path.join(device_path, 'devnum'), 'r') as f:
                                device_number = f.read().strip()
                            
                            usb_info.append(f"ID Vendor: {vendor_id}, ID Product: {product_id}, Bus Number: {bus_number}, Device Number: {device_number}")
                        except FileNotFoundError:
                            usb_info.append(f"ID Vendor: {vendor_id}, ID Product: {product_id}, Porta não encontrada")
                    
                    except FileNotFoundError:
                        continue
            
            return usb_info
        except Exception as e:
            return [f"erro: {e}"]

    def tabela_roteamento(self):
        try:
            rota_info = []
            with open('/proc/net/route', 'r') as f:
                linhas = f.readlines()[1:]  
                for linha in linhas:
                    campos = linha.split()
                    if len(campos) >= 11:
                        interface = campos[0]
                        destino = self.hex_to_ip(campos[1])
                        gateway = self.hex_to_ip(campos[2])
                        mascara = self.hex_to_ip(campos[7])
                        rota_info.append(f"Interface: {interface}, Destino: {destino}, Gateway: {gateway}, Máscara: {mascara}")
            return rota_info
        except Exception as e:
            return [f"erro: {e}"]

    def hex_to_ip(self, hex_ip):
        # Converte o endereço IP hexadecimal para o formato decimal
        return ".".join([str(int(hex_ip[i:i + 2], 16)) for i in range(6, -2, -2)])

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        """Responder a uma requisição GET."""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        hora_atual = datetime.now()
        tempo_atividade_segundos = self.tempo()
        modelo_cpu, velocidade_cpu = self.info_cpu()
        uso_cpu = self.uso_cpu()
        memoria_total, memoria_usada = self.info_memoria()
        versao_os = self.versao_os()
        lista_processos = self.processos()
        particoes = self.particoes()
        dispositivos_usb = self.dispositivos_usb()
        tabela_roteamento = self.tabela_roteamento()

        # Construir a resposta HTML
        response = (
            "<html><head><title>Informações do Sistema</title></head>"
            "<body><h1>Alunos: Luiza Nunes, Nicolas Salles e Pietro Lessa</h1><h2>Informações do Sistema</h2>"
            f"<p><strong>Data e Hora:</strong> {hora_atual}</p>"
            f"<p><strong>Tempo de Atividade:</strong> {tempo_atividade_segundos} segundos</p>"
            f"<p><strong>Modelo do CPU:</strong> {modelo_cpu}</p>"
            f"<p><strong>Velocidade do CPU:</strong> {velocidade_cpu} MHz</p>"
            f"<p><strong>Uso do CPU:</strong> {uso_cpu:.2f}%</p>"
            f"<p><strong>Memória Total:</strong> {memoria_total} MB</p>"
            f"<p><strong>Memória Usada:</strong> {memoria_usada} MB</p>"
            f"<p><strong>Versão do Sistema Operacional:</strong> {versao_os}</p>"
            "<h2>Processos em Execução</h2><ul>"
        )
        for processo in lista_processos:
            response += f"<li>{processo}</li>"
        
        response += "</ul><h2>Partições</h2><ul>"
        for particao in particoes:
            response += f"<li>{particao}</li>"

        response += "</ul><h2>Dispositivos USB</h2><ul>"
        for usb in dispositivos_usb:
            response += f"<li>{usb}</li>"

        response += "</ul><h2>Tabela de Roteamento</h2><ul>"
        for rota in tabela_roteamento:
            response += f"<li>{rota}</li>"

        response += "</ul></body></html>"
        self.wfile.write(response.encode())

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MeuManipulador)
    print(f"Servidor Iniciado - {HOST_NAME}:{PORT_NUMBER}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(f"Servidor Parado - {HOST_NAME}:{PORT_NUMBER}")