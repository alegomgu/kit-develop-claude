#!/usr/bin/env python3
"""Instala o actualiza idener-claude-kit en un repo git.

    python install.py <repo> [--role main|secondary] [--exclude-local] [--update] [--dry-run]

Todo lo que copia queda fuera de git (.claude/, CLAUDE.md, TASKS.md).
"""
import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
BEGIN = "# >>> idener-claude-kit"
KIT_FOLDERS = ("agents", "skills", "scripts")
KIT_TEMPLATES = ("spec.md", "pr.md")


def say(msg):
    print(msg)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text, dry):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)


def git_dir(repo):
    out = git(repo, "rev-parse", "--git-dir")
    if out.returncode != 0:
        return None
    path = out.stdout.strip()
    return path if os.path.isabs(path) else os.path.join(repo, path)


def exclusions(repo, local, dry):
    block = read(os.path.join(KIT, "templates", "gitignore-block.txt"))
    target = os.path.join(git_dir(repo), "info", "exclude") if local \
        else os.path.join(repo, ".gitignore")
    current = read(target) if os.path.exists(target) else ""
    shown = os.path.relpath(target, repo)
    if BEGIN in current:
        say("  = exclusiones ya presentes en " + shown)
        return
    sep = "" if current == "" or current.endswith("\n") else "\n"
    write(target, current + sep + ("\n" if current else "") + block, dry)
    say("  + exclusiones en " + shown)


def tracked(repo):
    out = git(repo, "ls-files", "--", ".claude", "CLAUDE.md", "TASKS.md")
    return [line for line in out.stdout.splitlines() if line.strip()]


def copy_tree(src, dst, dry):
    """Copia los ficheros del kit sobre el destino. No borra lo que el proyecto haya añadido."""
    changed = 0
    for base, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            if name.endswith(".pyc"):
                continue
            s = os.path.join(base, name)
            d = os.path.join(dst, os.path.relpath(s, src))
            if os.path.exists(d) and filecmp.cmp(s, d, shallow=False):
                continue
            changed += 1
            say("  %s %s" % ("~" if os.path.exists(d) else "+", os.path.relpath(d, os.path.dirname(dst))))
            if not dry:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copyfile(s, d)
    return changed


def create_if_missing(src, dst, repo, name, dry):
    if os.path.exists(dst):
        say("  = se conserva " + os.path.relpath(dst, repo))
        return
    text = read(src).replace("<Proyecto>", name)
    if dst.endswith("project.json"):
        data = json.loads(text)
        data["name"] = name
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    write(dst, text, dry)
    say("  + " + os.path.relpath(dst, repo))


def settings(repo, update, dry):
    dst = os.path.join(repo, ".claude", "settings.json")
    kit_settings = json.loads(read(os.path.join(KIT, "templates", "settings.json")))
    if not os.path.exists(dst):
        write(dst, json.dumps(kit_settings, indent=2, ensure_ascii=False) + "\n", dry)
        say("  + .claude/settings.json")
        return
    if not update:
        say("  = se conserva .claude/settings.json")
        return
    try:
        current = json.loads(read(dst))
    except ValueError:
        say("  ! .claude/settings.json no es JSON válido; no se toca")
        return
    if current.get("hooks") == kit_settings["hooks"]:
        say("  = hooks de settings.json al día")
        return
    current["hooks"] = kit_settings["hooks"]
    write(dst, json.dumps(current, indent=2, ensure_ascii=False) + "\n", dry)
    say("  ~ hooks de .claude/settings.json (los permisos se conservan)")


def main():
    parser = argparse.ArgumentParser(description="Instala o actualiza idener-claude-kit en un repo.")
    parser.add_argument("repo")
    parser.add_argument("--role", choices=("main", "secondary"), default="main",
                        help="secondary: repo adicional de un proyecto con varios repos")
    parser.add_argument("--exclude-local", action="store_true",
                        help="exclusiones en .git/info/exclude en lugar de .gitignore")
    parser.add_argument("--update", action="store_true", help="actualiza un repo ya instalado")
    parser.add_argument("--dry-run", action="store_true", help="enseña lo que haría sin tocar nada")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    dry = args.dry_run
    if not os.path.isdir(repo) or git_dir(repo) is None:
        sys.exit("No es un repo git: " + repo + "\nCrea el repo antes (git init) o revisa la ruta.")

    name = os.path.basename(repo.rstrip("\\/"))
    version = read(os.path.join(KIT, "VERSION")).strip()
    marker = os.path.join(repo, ".claude", "kit-version")
    installed = os.path.exists(marker) or (
        args.role == "secondary" and os.path.exists(os.path.join(repo, "CLAUDE.md")))

    if args.update and not installed:
        sys.exit("El kit no está instalado en este repo. Ejecuta primero sin --update.")
    if not args.update and installed and args.role == "main":
        sys.exit("El kit ya está instalado aquí (versión %s). Usa --update." % read(marker).strip())

    say("%s idener-claude-kit %s en %s%s" % (
        "Actualizando" if args.update else "Instalando", version, repo,
        "  [simulación: no se toca nada]" if dry else ""))

    exclusions(repo, args.exclude_local, dry)
    already = tracked(repo)
    if already:
        say("  ! Estos ficheros del kit ya están versionados en el repo:")
        for line in already[:10]:
            say("      " + line)
        say("    Para dejar de versionarlos sin borrarlos: git rm -r --cached <ruta>")

    if args.role == "secondary":
        create_if_missing(os.path.join(KIT, "templates", "CLAUDE.secondary.md"),
                          os.path.join(repo, "CLAUDE.md"), repo, name, dry)
        say("Hecho. Abre Claude Code desde el repo principal con: claude --add-dir \"%s\"" % repo)
        return 0

    for folder in KIT_FOLDERS:
        copy_tree(os.path.join(KIT, folder), os.path.join(repo, ".claude", folder), dry)
    for tpl in KIT_TEMPLATES:
        src = os.path.join(KIT, "templates", tpl)
        dst = os.path.join(repo, ".claude", "templates", tpl)
        if not (os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)):
            say("  %s .claude/templates/%s" % ("~" if os.path.exists(dst) else "+", tpl))
            if not dry:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)

    copy_tree(os.path.join(KIT, "templates", "kit"), os.path.join(repo, ".claude", "kit"), dry)

    rules_src = os.path.join(KIT, "templates", "kit-rules.md")
    rules_dst = os.path.join(repo, ".claude", "kit-rules.md")
    if not (os.path.exists(rules_dst) and filecmp.cmp(rules_src, rules_dst, shallow=False)):
        say("  %s .claude/kit-rules.md" % ("~" if os.path.exists(rules_dst) else "+"))
        if not dry:
            os.makedirs(os.path.dirname(rules_dst), exist_ok=True)
            shutil.copyfile(rules_src, rules_dst)

    create_if_missing(os.path.join(KIT, "templates", "project.json"),
                      os.path.join(repo, ".claude", "project.json"), repo, name, dry)
    create_if_missing(os.path.join(KIT, "templates", "CLAUDE.main.md"),
                      os.path.join(repo, "CLAUDE.md"), repo, name, dry)
    create_if_missing(os.path.join(KIT, "templates", "TASKS.md"),
                      os.path.join(repo, "TASKS.md"), repo, name, dry)
    settings(repo, args.update, dry)
    write(marker, version + "\n", dry)

    claude_md = os.path.join(repo, "CLAUDE.md")
    if os.path.exists(claude_md) and "kit-rules.md" not in read(claude_md):
        say("  ! Tu CLAUDE.md es anterior a la 0.1.3 y no importa las reglas del kit.")
        say("    Abre claude y pide: \"Sustituye en CLAUDE.md las secciones Tu papel, Flujos,")
        say("    Reglas, Entorno local y Cerrar una tarea por la línea @.claude/kit-rules.md,")
        say("    y conserva lo propio de este proyecto.\"")

    if not dry:
        status = git(repo, "status", "--porcelain", "--", ".claude", "CLAUDE.md", "TASKS.md")
        leaked = [line for line in status.stdout.splitlines() if line.strip()]
        if leaked:
            say("  ! git ve ficheros del kit como cambios. Revisa las exclusiones:")
            for line in leaked[:10]:
                say("      " + line)
        else:
            say("  ok: git no ve nada del kit")

    if args.update:
        say("Hecho. Reinicia Claude Code en el proyecto para que cargue los cambios.")
    else:
        say("Hecho. Siguiente paso: abre `claude` dentro del repo y escribe /adopt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
