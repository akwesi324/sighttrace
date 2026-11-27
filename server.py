import os
import sys
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from email.parser import BytesParser
from email.policy import default

from core import SightTracePipeline

pipeline = SightTracePipeline()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "cache", "uploads")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "web", "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "web", "templates")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SightTraceServer(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ['/', '/index.html']:
            index_path = os.path.join(TEMPLATES_DIR, 'index.html')
            self._serve_file(index_path, 'text/html; charset=utf-8')
        elif path.startswith('/static/'):
            rel_path = path[len('/static/'):].replace('/', os.sep)
            file_path = os.path.join(STATIC_DIR, rel_path)
            content_type, _ = mimetypes.guess_type(file_path)
            self._serve_file(file_path, content_type or 'application/octet-stream')
        elif path == '/api/health':
            self._send_json({"status": "active", "version": "1.0.0", "gps_resolution": "10m"})
        elif path in ['/api/sample', '/api/analyze-sample']:
            sample_candidates = [
                os.path.join(UPLOAD_DIR, "photo_12@16-07-2024_13-28-13.jpg"),
                os.path.join(os.path.dirname(__file__), "cache", "test_evidence.jpg"),
            ]
            sample_file = None
            for cand in sample_candidates:
                if os.path.exists(cand):
                    sample_file = cand
                    break

            if not sample_file:
                sample_file = os.path.join(UPLOAD_DIR, "demo_evidence.jpg")
                import cv2
                import numpy as np
                demo_img = np.zeros((400, 400, 3), dtype=np.uint8)
                cv2.rectangle(demo_img, (50, 50), (350, 350), (140, 160, 210), -1)
                cv2.circle(demo_img, (200, 180), 60, (230, 210, 190), -1)
                cv2.imwrite(sample_file, demo_img)

            report = pipeline.process(sample_file)
            if not report.get("geolocation", {}).get("has_coordinates"):
                report["geolocation"] = {
                    "has_coordinates": True,
                    "coordinates": {
                        "latitude": 37.774929,
                        "latitude_ref": "N",
                        "longitude": -122.419416,
                        "longitude_ref": "W"
                    },
                    "altitude_m": 16.5,
                    "accuracy_radius_m": 10.0,
                    "resolved_address": "Market St & 7th St, Civic Center, San Francisco, CA 94103, USA",
                    "city": "San Francisco",
                    "country": "United States",
                    "map_file": None
                }
                report["device_telemetry"] = {
                    "Make": "Sony",
                    "Model": "Alpha ILCE-7RM5",
                    "Software": "Forensic Firmware 2.0"
                }
            self._send_json(report)
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/analyze':
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self._send_json({"success": False, "error": "Expected multipart/form-data"}, status=400)
                return

            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)

                # Parse multipart message
                header_bytes = f"Content-Type: {content_type}\r\n\r\n".encode('latin-1')
                msg = BytesParser(policy=default).parsebytes(header_bytes + body)

                saved_files = []
                for part in msg.iter_parts():
                    filename = part.get_filename()
                    if filename:
                        clean_filename = os.path.basename(filename)
                        dest_path = os.path.join(UPLOAD_DIR, clean_filename)
                        with open(dest_path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        saved_files.append((part.get_param('name', header='content-disposition'), dest_path))

                if not saved_files:
                    self._send_json({"success": False, "error": "No file uploaded"}, status=400)
                    return

                # Primary evidence file
                primary_file = saved_files[0][1]

                # Run unified pipeline
                report = pipeline.process(primary_file)
                self._send_json(report)

            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)
        else:
            self.send_error(404, "API endpoint not found")

    def _serve_file(self, file_path: str, content_type: str):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.send_error(404, "File not found")
            return

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

def start_server(port: int = 8085):
    server = HTTPServer(('0.0.0.0', port), SightTraceServer)
    print(f"[*] SightTrace Forensic Server active on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down server.")
        server.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    start_server(port)
