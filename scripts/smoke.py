#!/usr/bin/env python3
"""Comprueba la conectividad del proyecto con el stack levantado.

Uso: python smoke.py [--wait SEGUNDOS] [--project RUTA]

Lee `run.health` de .claude/project.json. Cada entrada puede ser:
  - una URL:               "http://localhost:8010/health"   (vale cualquier respuesta < 400)
  - un puerto:             "tcp://localhost:5432"           (vale si acepta la conexión)
  - una llamada completa:  {"name": "simulación", "url": "http://localhost:8010/runs",
                            "method": "POST", "json": {"feed_rate": 500}, "expect": 200,
                            "contains": "oil_yield"}

Reintenta hasta --wait segundos, porque los contenedores tardan en arrancar. Sale con 0 si todo
responde y con 1 si algo falla. Solo usa la biblioteca estándar.
"""
import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request


def load_checks(project_dir):
    path = os.path.join(project_dir, ".claude", "project.json")
    with open(path, encoding="utf-8") as fh:
        run = json.load(fh).get("run") or {}
    return run.get("health") or []


def check_tcp(target, timeout):
    host, _, port = target[len("tcp://"):].rpartition(":")
    with socket.create_connection((host or "localhost", int(port)), timeout=timeout):
        return True, "acepta conexión"


def check_http(check, timeout):
    url = check["url"]
    method = (check.get("method") or ("POST" if "json" in check else "GET")).upper()
    data, headers = None, dict(check.get("headers") or {})
    if "json" in check:
        data = json.dumps(check["json"]).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status, body = response.status, response.read(200000).decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        status, body = err.code, err.read(200000).decode("utf-8", "replace")
    expect = check.get("expect")
    if expect is not None and status != int(expect):
        return False, "respondió %s, se esperaba %s" % (status, expect)
    if expect is None and status >= 400:
        return False, "respondió %s" % status
    text = check.get("contains")
    if text and text not in body:
        return False, "respondió %s pero falta '%s' en la respuesta" % (status, text)
    return True, "respondió %s" % status


def run_check(check, timeout):
    if isinstance(check, str):
        check = {"url": check}
    target = check.get("url") or ""
    try:
        if target.startswith("tcp://"):
            return check_tcp(target, timeout)
        if target.startswith(("http://", "https://")):
            return check_http(check, timeout)
        return False, "entrada no reconocida (usa http://, https:// o tcp://)"
    except Exception as err:  # conexión rechazada, tiempo agotado, DNS...
        return False, "%s: %s" % (type(err).__name__, err)


def label(check):
    if isinstance(check, str):
        return check
    return check.get("name") or "%s %s" % ((check.get("method") or "GET").upper(), check.get("url"))


def main():
    parser = argparse.ArgumentParser(description="Comprueba la conectividad con el stack levantado.")
    parser.add_argument("--wait", type=float, default=0, help="segundos máximos de reintento")
    parser.add_argument("--timeout", type=float, default=10, help="segundos por intento")
    parser.add_argument("--project", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    args = parser.parse_args()

    try:
        checks = load_checks(args.project)
    except Exception as err:
        print("No se puede leer .claude/project.json: %s" % err)
        return 1
    if not checks:
        print("run.health está vacío en .claude/project.json: no hay nada que comprobar.")
        return 1

    deadline = time.time() + args.wait
    pending = list(range(len(checks)))
    results = {}
    while True:
        for i in list(pending):
            ok, detail = run_check(checks[i], args.timeout)
            results[i] = (ok, detail)
            if ok:
                pending.remove(i)
        if not pending or time.time() >= deadline:
            break
        time.sleep(3)

    for i, check in enumerate(checks):
        ok, detail = results[i]
        print("%s  %s  (%s)" % ("OK   " if ok else "FALLA", label(check), detail))
    if pending:
        print("\n%d de %d comprobaciones fallan." % (len(pending), len(checks)))
        return 1
    print("\nTodo responde (%d comprobaciones)." % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
