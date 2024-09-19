import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = '127.0.0.1'  # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")

        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        # 1. Data e hora do sistema
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 2. Uptime do sistema
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])
            uptime_string = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))

        # 3. Modelo do processador e velocidade
        with open("/proc/cpuinfo", "r") as f:
            cpu_info = f.readlines()
            model_name = ""
            cpu_mhz = ""
            for line in cpu_info:
                if "model name" in line:
                    model_name = line.split(":")[1].strip()
                if "cpu MHz" in line:
                    cpu_mhz = line.split(":")[1].strip()
                    break

        # 4. Capacidade ocupada do processador (%)
        with open("/proc/stat", "r") as f:
            cpu_times = f.readline().split()[1:5]
            cpu_times = list(map(int, cpu_times))
            idle_time = cpu_times[3]
            total_time = sum(cpu_times)
            cpu_usage = 100 * (1 - (idle_time / total_time))

        # 5. Quantidade de memória RAM total e usada
        with open("/proc/meminfo", "r") as f:
            mem_info = f.readlines()
            total_mem = int(mem_info[0].split()[1]) / 1024  # Convert KB to MB
            free_mem = int(mem_info[1].split()[1]) / 1024   # Convert KB to MB
            used_mem = total_mem - free_mem

        # 6. Versão do sistema
        with open("/proc/version", "r") as f:
            version_info = f.readline().strip()

        # 7. Lista de processos em execução (PID e nome)
        process_list = []
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                try:
                    with open(f"/proc/{pid}/comm", "r") as f:
                        process_name = f.read().strip()
                        process_list.append(f"PID: {pid}, Nome: {process_name}")
                except Exception:
                    continue

        # 8. Lista de unidades de disco físicas a partir de /proc/partitions
        with open("/proc/partitions", "r") as f:
            partitions = f.readlines()[2:]  # Ignora cabeçalhos
            disk_info = []
            for partition in partitions:
                cols = partition.split()
                major, minor, blocks, name = int(cols[0]), int(cols[1]), int(cols[2]), cols[3]
                # Filtra dispositivos loopback (ex: loop0, loop1)
                if not name.startswith("loop"):
                    disk_info.append(f"Dispositivo: {name}, Tamanho: {blocks / 2048:.2f} MB")

        

        # 9. Lista de dispositivos USB
        usb_info = os.popen("lsusb").read()

        # 10. Lista de adaptadores de rede e endereçamento IP
        network_info = os.popen("ip -br addr").read()

        # Gerar página HTML
        self.wfile.write("<html><head><title>Informações do Sistema</title></head>".encode())
        self.wfile.write("<body><h1>Informações do Sistema</h1>".encode())
        self.wfile.write(f"<p>Data e hora: {current_time}</p>".encode())
        self.wfile.write(f"<p>Uptime do sistema: {uptime_string}</p>".encode())
        self.wfile.write(f"<p>Modelo do processador: {model_name}</p>".encode())
        self.wfile.write(f"<p>Velocidade do processador: {cpu_mhz} MHz</p>".encode())
        self.wfile.write(f"<p>Uso do processador: {cpu_usage:.2f}%</p>".encode())
        self.wfile.write(f"<p>Memória RAM total: {total_mem:.2f} MB</p>".encode())
        self.wfile.write(f"<p>Memória RAM usada: {used_mem:.2f} MB</p>".encode())
        self.wfile.write(f"<p>Versão do sistema: {version_info}</p>".encode())

        # Gerar a lista de processos em execução
        self.wfile.write("<h2>Processos em Execução:</h2>".encode())
        self.wfile.write("<ul>".encode())
        for process in process_list:
            self.wfile.write(f"<li>{process}</li>".encode())
        self.wfile.write("</ul>".encode())

        # Gerar a lista de discos físicos
        self.wfile.write("<h2>Unidades de Disco Físicas:</h2>".encode())
        self.wfile.write("<ul>".encode())
        for disk in disk_info:
            self.wfile.write(f"<li>{disk}</li>".encode())
        self.wfile.write("</ul>".encode())

        self.wfile.write("<h2>Dispositivos USB:</h2>".encode())
        self.wfile.write(f"<pre>{usb_info}</pre>".encode())

        self.wfile.write("<h2>Adaptadores de Rede:</h2>".encode())
        self.wfile.write(f"<pre>{network_info}</pre>".encode())
        self.wfile.write("</body></html>".encode())

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
    print(f"Server Starts - {HOST_NAME}:{PORT_NUMBER}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

    print(f"Server Stops - {HOST_NAME}:{PORT_NUMBER}")