from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs
from pathlib import Path
import json
import uuid

try:
    from modules.batch import handle_batch, reset_session
except ImportError:
    from server.modules.batch import handle_batch, reset_session

HOST = "127.0.0.1"
PORT = 8080

BASE = Path(__file__).resolve().parent
CAPTURE_DIR = BASE / "data" / "captures"
RESPONSE_DIR = BASE / "data" / "responses"
ASSET_DIR = BASE / "data" / "assets"
ROUTES_FILE = BASE / "config" / "routes.json"

CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
RESPONSE_DIR.mkdir(parents=True, exist_ok=True)
ASSET_DIR.mkdir(parents=True, exist_ok=True)

ASSET_PREFIX = "/assets/"
CONTENT_TYPES = {
    ".big": "application/octet-stream",
    ".xml": "application/xml",
    ".db": "application/x.binary",
    ".zip": "application/zip",
}

MAX_BODY = 1024 * 1024

SENSITIVE_KEYS = {
    "authorization", "cookie", "set-cookie",
    "password", "token", "access_token",
    "refresh_token", "androidid", "hwid",
    "deviceid", "eadeviceid", "uid"
}


def redact(value):
    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if key.lower().replace("-", "_") in SENSITIVE_KEYS
                else redact(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def load_routes():
    try:
        return json.loads(ROUTES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


class RevivalServer(BaseHTTPRequestHandler):

    def send_bytes(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, data):
        self.send_bytes(status, "application/json", json.dumps(data, indent=2).encode("utf-8"))

    def resolve_asset(self, path):
        """Map a /assets/<rel> URL to a file inside ASSET_DIR, or None.

        /assets/manifest.db is a configured route, so it is left to the route
        table and never served from here.
        """
        if not path.startswith(ASSET_PREFIX):
            return None

        rel = path[len(ASSET_PREFIX):]
        if not rel or rel == "manifest.db":
            return None

        try:
            target = (ASSET_DIR / rel).resolve()
            target.relative_to(ASSET_DIR.resolve())
        except (OSError, ValueError):
            return None

        return rel, target

    def serve_asset(self, path):
        """Serve an asset with byte-range support. Returns False if not an asset URL."""
        resolved = self.resolve_asset(path)
        if resolved is None:
            return False

        rel, target = resolved

        if not target.is_file():
            print(f"[ASSET MISS] {rel}")
            self.send_json(404, {"error": "asset not found", "name": rel})
            return True

        data = target.read_bytes()
        total = len(data)
        content_type = CONTENT_TYPES.get(target.suffix.lower(), "application/octet-stream")

        range_header = self.headers.get("Range", "")
        if range_header.startswith("bytes="):
            spec = range_header[len("bytes="):].split(",")[0].strip()
            start_text, _, end_text = spec.partition("-")
            try:
                start = int(start_text) if start_text else 0
                end = int(end_text) if end_text else total - 1
            except ValueError:
                start, end = 0, total - 1

            if start >= total:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{total}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return True

            end = min(end, total - 1)
            chunk = data[start:end + 1]
            self.send_response(206)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
            self.send_header("Content-Length", str(len(chunk)))
            self.end_headers()
            self.wfile.write(chunk)
            return True

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(total))
        self.end_headers()
        self.wfile.write(data)
        return True

    def capture_request(self):
        length = int(self.headers.get("Content-Length", 0))

        if length > MAX_BODY:
            self.send_json(413, {"error": "Request too large"})
            return

        raw = self.rfile.read(length) if length else b""

        try:
            body = json.loads(raw) if raw else None
            body_type = "json"
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = raw.decode("utf-8", errors="replace") if raw else None
            body_type = "text"

        parsed = urlsplit(self.path)

        allowed_headers = {
            "content-type", "accept", "user-agent",
            "content-length"
        }

        safe_headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() in allowed_headers
        }

        capture_id = str(uuid.uuid4())

        record = {
            "capture_id": capture_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": self.command,
            "path": parsed.path,
            "query": parse_qs(parsed.query),
            "headers": safe_headers,
            "body_type": body_type,
            "body": redact(body),
            "body_hex": raw.hex() if (raw and body_type == "text") else None,
            "analysis_status": "unreviewed"
        }

        filename = CAPTURE_DIR / f"{capture_id}.json"
        filename.write_text(json.dumps(record, indent=2), encoding="utf-8")

        if self.command == "POST" and parsed.path == "/g/game/batch":
            resp_bytes, _ = handle_batch(raw)
            self.send_bytes(200, "application/x.binary", resp_bytes)
            return

        if self.command == "GET" and parsed.path.startswith("/config/Android/") and parsed.path.endswith("/config.ini"):
            reset_session()

        route_key = f"{self.command} {parsed.path}" 
        routes = load_routes()
        route = routes.get(route_key)
        if not route and self.command == "GET" and parsed.path.startswith("/config/Android/") and parsed.path.endswith("/config.ini"):
            route = routes.get("GET /config/Android/default/config.ini")

        if route:
            template_name = route.get("file", "")
            if Path(template_name).name != template_name:
                self.send_json(500, {"error": "Invalid template filename"})
                return

            template_path = RESPONSE_DIR / template_name
            ctype = route.get("content_type", "application/json")

            try:
                status = int(route.get("status", 200))
                if not 200 <= status <= 599:
                    raise ValueError("Invalid response status")
                if ctype == "application/x.binary":
                    self.send_bytes(status, ctype, template_path.read_bytes())
                else:
                    text = template_path.read_text(encoding="utf-8")
                    if ctype.startswith("application/json"):
                        self.send_json(status, json.loads(text))
                    else:
                        self.send_bytes(status, ctype, text.encode("utf-8"))
            except (OSError, json.JSONDecodeError, ValueError):
                self.send_json(500, {
                    "error": "Response template unavailable",
                    "capture_id": capture_id
                })
            return

        self.send_json(202, {
            "status": "captured",
            "capture_id": capture_id,
            "message": "No response template configured."
        })

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {
                "status": "online",
                "project": "FIFA Revival",
                "version": "0.4.0",
                "time": datetime.now(timezone.utc).isoformat()
            })
        elif self.path == "/project":
            self.send_json(200, {
                "game": "FIFA Mobile",
                "client_version": "18.1.03",
                "build_number": 40214,
                "environment": "local-development"
            })
        else:
            if not self.serve_asset(urlsplit(self.path).path):
                self.capture_request()

    def do_POST(self):
        self.capture_request()

    def do_PUT(self):
        self.capture_request()

    def do_PATCH(self):
        self.capture_request()

    def do_DELETE(self):
        self.capture_request()

    def log_message(self, format, *args):
        pass


print(f"FIFA Revival server: http://{HOST}:{PORT}")
print(f"Captures: {CAPTURE_DIR}")
print(f"Responses: {RESPONSE_DIR}")
print(f"Assets: {ASSET_DIR}")

HTTPServer((HOST, PORT), RevivalServer).serve_forever()
