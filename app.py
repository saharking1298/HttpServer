# HTTP Server application
# Creator: Sahar Lando
from server import HttpServer
import os

HOST = "127.0.0.1"
PORT = 3500


def main():
    # Root folder
    root = os.sep.join((os.path.dirname(__file__), "public"))
    # Keys = web URIs
    # Values = relative / absolute file paths
    routes = {
        '/': '/index.html',
    }
    server = HttpServer(HOST, PORT, root, routes)
    server.start()


if __name__ == '__main__':
    main()
