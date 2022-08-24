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
            '/calculate-next': self.calculate_next,
            '/calculate-area': self.calculate_area,
        }
        self.server = HttpServer(HOST, PORT, root, routes)

    def calculate_area(self, request):
        # Takes 2 URL parameters: height, width
        # Returns square area (height * width)
        status = 200
        try:
            height = int(request.params["height"])
            width = int(request.params["width"])
            response = str(float(height * width) / 2)
        except ValueError:
            response = "NaN"
        except IndexError:
            status = 400
            response = "Missing one or more required parameters: 'height', 'width'"
        return status, "text", response

    def calculate_next(self, request):
        # Takes 1 URL parameter: num
        # Returns num + 1
        response = "Missing one or more required parameters: 'num'"
        status = 400
        if "num" in request.params:
            try:
                response = str(int(request.params["num"]) + 1)
                status = 200
            except ValueError:
                status = 200
                response = "NaN"
        return status, "text", response

    def start(self):
        self.server.start()


def main():
    app = App()
    app.start()


if __name__ == '__main__':
    main()
