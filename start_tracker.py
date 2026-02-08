import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "docs"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

print(f"🚀 Live Robot Tracker Server Starting...")
print(f"📡 Access: http://localhost:{PORT}")
print(f"📁 Serving from: {DIRECTORY}/")
print(f"🤖 Multi-agent system ready!")
print()
print("Open your browser to: http://localhost:8000")
print("Or on your network: http://192.168.1.89:8000")
print()
print("Press Ctrl+C to stop")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()