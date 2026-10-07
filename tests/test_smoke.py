import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(KIT, "scripts", "smoke.py")


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"detail": "no"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length) or b"{}")
        if payload.get("feed_rate", 0) > 0:
            self._send(200, {"oil_yield": 40.0, "mock": True})
        else:
            self._send(422, {"detail": [{"variable": "feed_rate"}]})

    def log_message(self, *args):
        pass


@pytest.fixture
def server():
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "127.0.0.1:%d" % httpd.server_address[1]
    httpd.shutdown()


def smoke(tmp_path, health, *args):
    (tmp_path / ".claude").mkdir(exist_ok=True)
    (tmp_path / ".claude" / "project.json").write_text(
        json.dumps({"run": {"health": health}}), encoding="utf-8")
    return subprocess.run([sys.executable, SMOKE, "--project", str(tmp_path), "--timeout", "3"]
                          + list(args), capture_output=True, text=True)


def test_todo_responde(tmp_path, server):
    out = smoke(tmp_path, [
        "http://%s/health" % server,
        "tcp://%s" % server,
        {"name": "simulación", "url": "http://%s/runs" % server, "json": {"feed_rate": 500},
         "expect": 200, "contains": "oil_yield"},
        {"name": "validación", "url": "http://%s/runs" % server, "json": {"feed_rate": -1},
         "expect": 422},
    ])
    assert out.returncode == 0, out.stdout
    assert out.stdout.count("OK") == 4


def test_falla_si_algo_no_responde(tmp_path, server):
    out = smoke(tmp_path, ["http://%s/health" % server, "http://%s/no-existe" % server,
                           "tcp://127.0.0.1:1"])
    assert out.returncode == 1
    assert out.stdout.count("FALLA") == 2 and "OK" in out.stdout


def test_falla_si_falta_el_texto(tmp_path, server):
    out = smoke(tmp_path, [{"url": "http://%s/health" % server, "contains": "base de datos"}])
    assert out.returncode == 1


def test_sin_comprobaciones(tmp_path):
    assert smoke(tmp_path, []).returncode == 1


def test_sin_project_json(tmp_path):
    out = subprocess.run([sys.executable, SMOKE, "--project", str(tmp_path)],
                         capture_output=True, text=True)
    assert out.returncode == 1
