import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
from threading import Thread
from datetime import datetime
import logging
import json


UDP_IP = "127.0.0.1"
UDP_PORT = 5000
FILENAME = "storage//data.json"

logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")


def run_socket_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            logging.debug(f"Data {data} has been received from {address}")
            data_parse = urllib.parse.unquote_plus(data.decode())
            print(data_parse)

            data_list = data_parse.split("&")
            logging.debug(f"Data_list = {data_list}")

            time_received = data_list[0]
            user_data = data_list[1:]

            logging.debug(f"time_received = {time_received}\nuser_data = {user_data}")

            data_dict = {
                key: value for key, value in [el.split("=") for el in user_data]
            }

            with open(FILENAME, "r") as f:
                data_json = json.load(f)

            data_json[time_received] = data_dict

            logging.debug(f"data_json = {data_json}")

            with open(FILENAME, "w") as f:
                json.dump(data_json, f)

    except KeyboardInterrupt:
        print(f"Destroy server")
    finally:
        sock.close()


def run_socket_client(ip, port, bin_text, received_time):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server = ip, port

        data = "&".join([received_time, bin_text])
        data_b = data.encode()

        sock.sendto(data_b, server)
        logging.debug(f"Data: {data} has been sent to socket server")


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data_b = self.rfile.read(int(self.headers["Content-Length"]))
        data = data_b.decode()
        received_time = str(datetime.now())

        run_socket_client(UDP_IP, UDP_PORT, data, received_time)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("0.0.0.0", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    thread1 = Thread(target=run_socket_server, args=(UDP_IP, UDP_PORT))
    thread2 = Thread(target=run_http_server, args=())

    thread1.start()
    thread2.start()
