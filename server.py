import socket
import os
import re

CONTENT_TYPES = {
    'html': 'text/html; charset=UTF-8',
    'jpg': 'image/jpeg',
    'js': 'text/javascript; charset=utf-8',
    'css': 'text/css; charset=utf-8',
    'ico': 'image/vnd.microsoft.icon',
    'gif': 'image/gif',
}
STATUS_CODES = {
    '200': 'OK',
    '404': 'NOT_FOUND',
    '403': 'FORBIDDEN',
    '500': 'INTERNAL_SERVER_ERROR'
}


class HttpRequest:
    def __init__(self, request):
        self.method = ""
        self.path = ""
        self.protocol = ""
        self.headers = {}
        self.process(request)

    def process(self, request):
        # Getting general headers and request headers
        req_lines = request.split("\n")
        general_header = req_lines[0]
        request_headers = req_lines[1:]
        # Getting HTTP method, path and HTTP version.
        # Example: GET /home HTTP/1.1
        self.method, self.path, self.protocol = general_header.split(" ")
        # Getting request headers
        self.headers = {}
        for header in request_headers:
            if header.strip() == "":
                continue
            header_parts = header.split(":", 1)
            self.headers[header_parts[0].strip()] = header_parts[1].strip()


class HttpServer:
    def __init__(self, host, port, root, routes, debug=True):
        self.methods = {
            "GET": self.method_get,
        }
        self.root = root.replace("/", os.path.sep)
        self.routes = routes
        self.socket = socket.socket()
        self.host = host
        self.port = port
        self.debug = debug
        self.fix_routes()

    def log(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def highlight(self, *args, **kwargs):
        self.log("----------------------------------------------------------")
        self.log(*args, **kwargs)
        self.log("----------------------------------------------------------")

    def get_absolute_path(self, relative_path):
        if relative_path.startswith("/"):
            relative_path = relative_path[1:]
        return os.path.sep.join((self.root, *relative_path.split("/")))
    
    def fix_routes(self):
        # Making partial route paths full and absolute
        abs_path_pattern = re.compile("^[A-Z]:/.+$")  # Absolute path Regex template
        for key, value in self.routes.items():
            # Checking of value is already an absolute path
            if abs_path_pattern.fullmatch(value) and os.path.isfile(value):
                full_path = value.replace("/", os.path.sep)
            else:
                full_path = self.get_absolute_path(value)
            self.routes[key] = full_path
        # Debugging routes and their serving path
        self.log(self.routes)

    def build_response(self, res_code, content_type, res_body):
        if type(res_body) == str:
            res_body = res_body.encode()
        if type(res_code) != str:
            res_code = str(res_code)
        res = f"HTTP/1.1 {res_code} {STATUS_CODES[res_code]}\r\n"
        res += f"Content-Type: {CONTENT_TYPES[content_type]}\r\n"
        res += f"Content-Length: {len(res_body)}\r\n\r\n"
        res = res.encode() + res_body
        return res

    def method_get(self, connection, request):
        # Priorities:
        # 1. Pre-defined route --> 500 if fails
        # 2. File requests --> 404 if fails
        # 3. Fails --> 404
        path = ""
        if request.path in self.routes:
            path = self.routes[request.path]
        else:
            for file_type in CONTENT_TYPES:
                if request.path.lower().endswith("." + file_type):
                    full_path = self.get_absolute_path(request.path)
                    if os.path.isfile(full_path):
                        path = full_path
                    break
        res = self.build_response(500, "html", "500 Internal error")
        if path == "":
            res = self.build_response(404, "html", "404 Not found")
        elif os.path.isfile(path):
            content_type = path.split(".")[-1].lower()
            if content_type in CONTENT_TYPES:
                try:
                    content = open(path, "rb").read()
                    res = self.build_response(200, content_type, content)
                except IOError:
                    print("Failed to read file: " + path)
        connection.send(res)

    def handle_connection(self, connection):
        # Receiving data from client socket
        data = connection.recv(1024).decode()
        if not data:  # If data is empty, terminate connection
            return
        # Processing the HTTP request
        request = HttpRequest(data)
        # Calling the right method handler
        if request.method in self.methods:
            self.log(request.method, request.path, request.protocol)
            self.methods[request.method](connection, request)

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.log(f"Listening on: http://{self.host}:{self.port}")
        while True:
            connection, address = self.socket.accept()
            self.handle_connection(connection)
