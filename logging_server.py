import http.server
import socketserver
import os
import sys

PORT = 8000
DIRECTORY = "/home/learn-2-earn/Documents/bankofamerica"

class LoggingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        print(f"GET Request: {self.path}", flush=True)
        # Log to file
        with open(os.path.join(DIRECTORY, "server_log.txt"), "a") as f:
            f.write(f"GET {self.path}\n")
        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        print(f"POST Request: {self.path} | Data: {post_data}", flush=True)
        # Log to file
        with open(os.path.join(DIRECTORY, "server_log.txt"), "a") as f:
            f.write(f"POST {self.path} | Data: {post_data}\n")
            
        # Mock responses if needed, else serve as simple HTTP or 404
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"status": "success"}')

    def end_headers(self):
        # Add CORS headers to all responses to fix CORS warnings
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

os.chdir(DIRECTORY)
# Clear old log
if os.path.exists("server_log.txt"):
    os.remove("server_log.txt")

with socketserver.TCPServer(("", PORT), LoggingHandler) as httpd:
    print(f"Serving HTTP on port {PORT} from {DIRECTORY}...", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.", flush=True)
        sys.exit(0)
