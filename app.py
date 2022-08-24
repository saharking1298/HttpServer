# HTTP Server application
# Creator: Sahar Lando
from server import HttpServer
import os

HOST = "127.0.0.1"
PORT = 3500


class App:
    def __init__(self):
        # Root folder
        root = os.sep.join((os.path.dirname(__file__), "public"))
        # Keys = web URIs
        # Values = relative / absolute file paths
        routes = {
            '/': '/index.html',
            '/favicon.ico': 'imgs/favicon.ico',
            '/calculate-next': self.calculate_next
        }
        self.server = HttpServer(HOST, PORT, root, routes)

    def calculate_next(self, request):
        # Takes 1 URL parameter: num
        # Returns num + 1
        response = "Parameter 'num' doesn't exist"
        print(request.params)
        if "num" in request.params:
            try:
                response = str(int(request.params["num"]) + 1)
            except TypeError:
                response = "Invalid number"
        return 200, "text", response

    def start(self):
        self.server.start()


def main():
    app = App()
    app.start()


if __name__ == '__main__':
    main()
