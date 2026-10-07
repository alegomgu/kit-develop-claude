#!/usr/bin/env python3
"""Hook PreToolUse de Bash para Claude Code.

Bloquea (saliendo con 2 y el motivo por stderr):
  - git commit, merge y push estando en una rama protegida (main/master)
  - git push a una rama protegida, con --force/-f o con --tags
  - git tag que cree o borre etiquetas
  - git reset --hard
  - git add -f de material del kit (.claude/, CLAUDE.md, TASKS.md)
  - gh release create/edit/delete
  - escribir con >, >>, tee, cp, mv o touch en una ruta absoluta fuera del proyecto

Lee por stdin el JSON que envía Claude Code. Ante cualquier error propio deja pasar
(sale con 0): un guard roto no debe parar el trabajo.
"""
import json
import os
import re
import shlex
import subprocess
import sys

KIT_PATHS = (".claude", "claude.md", "tasks.md")
DEFAULT_PROTECTED = ["main", "master"]


def protected_branches(project_dir):
    try:
        with open(os.path.join(project_dir, ".claude", "project.json"), encoding="utf-8") as fh:
            value = json.load(fh).get("protected_branches")
        if isinstance(value, list) and value:
            return [str(v) for v in value]
    except Exception:
        pass
    return DEFAULT_PROTECTED


def current_branch(cwd):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "symbolic-ref", "--short", "-q", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def split_segments(command):
    """Trocea por && || ; | y saltos de línea, respetando comillas de forma aproximada."""
    parts, buf, quote = [], "", ""
    i = 0
    while i < len(command):
        ch = command[i]
        if quote:
            buf += ch
            if ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
            buf += ch
        elif command[i:i + 2] in ("&&", "||"):
            parts.append(buf)
            buf = ""
            i += 1
        elif ch in ";|\n":
            parts.append(buf)
            buf = ""
        else:
            buf += ch
        i += 1
    parts.append(buf)
    return [p.strip() for p in parts if p.strip()]


def tokens_of(segment):
    try:
        return shlex.split(segment, posix=True)
    except ValueError:
        return segment.split()


def git_parts(tokens):
    """Devuelve (subcomando, argumentos, directorio de -C) o None si no es git."""
    idx = None
    for i, tok in enumerate(tokens):
        name = os.path.basename(tok).lower()
        if name in ("git", "git.exe"):
            idx = i
            break
        if "=" in tok and not tok.startswith("-"):
            continue  # VAR=valor delante del comando
        break
    if idx is None:
        return None
    rest, cdir = tokens[idx + 1:], None
    j = 0
    while j < len(rest):
        tok = rest[j]
        if tok == "-C" and j + 1 < len(rest):
            cdir = rest[j + 1]
            j += 2
        elif tok == "-c" and j + 1 < len(rest):
            j += 2
        elif tok.startswith("-"):
            j += 1
        else:
            return tok, rest[j + 1:], cdir
    return None


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


def write_targets(segment, tokens):
    """Rutas en las que el comando escribe: redirecciones y destinos de cp, mv, tee y touch."""
    targets = []
    try:
        lexer = shlex.shlex(segment, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        parts = list(lexer)
    except ValueError:
        parts = []
    for i, tok in enumerate(parts[:-1]):
        if tok in (">", ">>", ">|"):
            targets.append(parts[i + 1])
    if tokens:
        first = os.path.basename(tokens[0]).lower()
        args = [t for t in tokens[1:] if not t.startswith("-")]
        if first in ("cp", "mv") and len(args) >= 2:
            targets.append(args[-1])
        elif first in ("tee", "touch"):
            targets.extend(args)
    return targets


def outside_project(target, cwd, roots):
    """True si el destino es una ruta absoluta fuera de las carpetas permitidas."""
    if not target or "$" in target or "`" in target or target.startswith(("~", "&")):
        return False
    if target.lower() in ("nul", "/dev/null") or target.startswith(("/dev/", "/tmp/")):
        return False
    path = target
    drive = re.match(r"^/([a-zA-Z])(/.*)?$", target)
    if os.name == "nt":
        if drive:
            path = drive.group(1) + ":" + (drive.group(2) or "/")
        elif target.startswith("/"):
            return True  # en Git Bash, / es la carpeta de instalación de Git
    if not os.path.isabs(path):
        return False  # las rutas relativas se quedan en el directorio de trabajo
    return not inside(path, roots)


def check(command, cwd, protected, roots=None):
    """Devuelve el motivo del bloqueo, o None si el comando puede ejecutarse."""
    for segment in split_segments(command):
        tokens = tokens_of(segment)
        if not tokens:
            continue
        first = os.path.basename(tokens[0]).lower()

        if roots:
            for target in write_targets(segment, tokens):
                if outside_project(target, cwd, roots):
                    return ("Escribir fuera del proyecto no está permitido (%s). Los ficheros "
                            "temporales van a .claude/tmp/." % target)

        if first == "cd" and len(tokens) > 1:
            cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(tokens[1])))
            continue

        if first in ("gh", "gh.exe") and len(tokens) > 2 and tokens[1] == "release" \
                and tokens[2] in ("create", "edit", "delete"):
            return "Las releases las publica una persona en GitHub, no un agente."

        git = git_parts(tokens)
        if not git:
            continue
        sub, args, cdir = git
        where = os.path.normpath(os.path.join(cwd, cdir)) if cdir else cwd
        branch = current_branch(where)
        on_protected = branch in protected

        if sub == "tag":
            listing = (not args) or any(a in ("-l", "--list", "-n", "--contains", "--points-at")
                                        for a in args)
            if not listing:
                return "Crear o borrar etiquetas es cosa de una persona (prepara la release)."
        elif sub == "reset" and "--hard" in args:
            return "git reset --hard puede perder trabajo. Pide al usuario que lo haga."
        elif sub in ("commit", "merge") and on_protected:
            return "Estás en la rama protegida '%s'. Crea una rama de trabajo antes de git %s." \
                   % (branch, sub)
        elif sub == "push":
            if "--tags" in args or "--follow-tags" in args:
                return "No se suben etiquetas desde un agente."
            if any(a in ("--force", "-f") or re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", a)
                   for a in args):
                return "git push --force no está permitido."
            targets = [a.split(":")[-1].lstrip("+") for a in args if not a.startswith("-")]
            if on_protected and len(targets) < 2:
                return "Estás en la rama protegida '%s'. No se hace push desde ella." % branch
            if any(t in protected or t.replace("refs/heads/", "") in protected
                   for t in targets[1:]):
                return "No se hace push a una rama protegida. Abre un PR."
        elif sub == "add" and any(a in ("-f", "--force") for a in args):
            for a in args:
                norm = a.replace("\\", "/").lower().strip("/")
                if any(norm == k or norm.startswith(k + "/") or norm.endswith("/" + k)
                       or ("/" + k + "/") in ("/" + norm + "/") for k in KIT_PATHS):
                    return "El material del kit (.claude/, CLAUDE.md, TASKS.md) no se versiona."
    return None


def main():
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") not in (None, "Bash"):
            return 0
        command = (data.get("tool_input") or {}).get("command") or ""
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
        cwd = data.get("cwd") or project_dir
        reason = check(command, cwd, protected_branches(project_dir), allowed_roots(project_dir))
    except Exception:
        return 0
    if reason:
        sys.stderr.write("Bloqueado por el kit: " + reason + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
