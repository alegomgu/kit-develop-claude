#!/usr/bin/env python3
"""Hook PreToolUse de Edit/Write para Claude Code.

Bloquea (saliendo con 2 y el motivo por stderr) escribir en:
  - cualquier carpeta .github/ (el CI y el despliegue son de otro equipo)
  - componentes marcados "readonly": true en .claude/project.json
  - cualquier ruta fuera del proyecto y de sus componentes (se permiten ~/.claude y la
    carpeta temporal del sistema)

Ante cualquier error propio deja pasar (sale con 0).
"""
import json
import os
import sys


def norm(path):
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def readonly_dirs(project_dir):
    dirs = []
    try:
        with open(os.path.join(project_dir, ".claude", "project.json"), encoding="utf-8") as fh:
            components = json.load(fh).get("components") or {}
        for name, comp in components.items():
            if isinstance(comp, dict) and comp.get("readonly") and comp.get("path"):
                dirs.append((name, norm(os.path.join(project_dir, comp["path"]))))
    except Exception:
        pass
    return dirs


def allowed_roots(project_dir):
    """Carpetas donde se puede escribir: el proyecto, sus componentes, ~/.claude y la temporal."""
    import tempfile
    roots = [project_dir, os.path.join(os.path.expanduser("~"), ".claude"), tempfile.gettempdir()]
    try:
        with open(os.path.join(project_dir, ".claude", "project.json"), encoding="utf-8") as fh:
            components = json.load(fh).get("components") or {}
        for comp in components.values():
            if isinstance(comp, dict) and comp.get("path"):
                roots.append(os.path.join(project_dir, comp["path"]))
    except Exception:
        pass
    return [os.path.normcase(os.path.normpath(os.path.abspath(r))) for r in roots]


def inside(full, roots):
    full = os.path.normcase(os.path.normpath(os.path.abspath(full)))
    return any(full == r or full.startswith(r.rstrip("\\/") + os.sep) for r in roots)


def check(file_path, project_dir, cwd):
    if not file_path:
        return None
    full = file_path if os.path.isabs(file_path) else os.path.join(cwd, file_path)
    full = norm(full)
    parts = [p.lower() for p in full.replace("\\", "/").split("/")]
    if ".github" in parts:
        return "No se toca .github/: el CI y el despliegue son de otro equipo."
    for name, base in readonly_dirs(project_dir):
        if full == base or full.startswith(base + os.sep):
            return "El componente '%s' es de solo lectura (project.json)." % name
    if not inside(full, allowed_roots(project_dir)):
        return ("Está fuera del proyecto: %s. Los temporales van a .claude/tmp/. Si es otro "
                "repo del proyecto, añádelo como componente en project.json." % file_path)
    return None


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
        reason = check(file_path, project_dir, data.get("cwd") or project_dir)
    except Exception:
        return 0
    if reason:
        sys.stderr.write("Bloqueado por el kit: " + reason + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
