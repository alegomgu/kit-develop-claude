import json
import os
import subprocess
import sys

import pytest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD = os.path.join(KIT, "scripts", "guard_commands.py")
PATHS = os.path.join(KIT, "scripts", "guard_paths.py")


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo)] + list(args), check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "proyecto con espacios"
    r.mkdir()
    git(r, "init", "-b", "main")
    git(r, "config", "user.email", "t@example.com")
    git(r, "config", "user.name", "t")
    (r / "a.txt").write_text("a", encoding="utf-8")
    git(r, "add", "a.txt")
    git(r, "commit", "-m", "inicial")
    return r


def run(script, payload, repo):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    out = subprocess.run([sys.executable, script], input=json.dumps(payload),
                         capture_output=True, text=True, env=env)
    return out.returncode, out.stderr


def bash(repo, command):
    return run(CMD, {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(repo)}, repo)[0]


def edit(repo, path):
    return run(PATHS, {"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": str(repo)}, repo)[0]


@pytest.mark.parametrize("command", [
    "git commit -m x",
    "git add a.txt && git commit -m x",
    "git status; git commit -m x",
    "git merge feature/1-x",
    "git push",
    "git push origin main",
    "git -c user.name=x commit -m x",
])
def test_bloquea_en_main(repo, command):
    assert bash(repo, command) == 2


@pytest.mark.parametrize("command", [
    "git tag v0.0.1",
    "git tag -a v1 -m x",
    "git tag -d v1",
    "git push --tags",
    "git push origin feature/1-x --force",
    "git push -f origin feature/1-x",
    "git push origin feature/1-x:main",
    "git reset --hard HEAD~1",
    "git add -f CLAUDE.md",
    "git add --force .claude/project.json",
    "gh release create v1.0.0",
    "echo hola && gh release delete v1",
])
def test_bloquea_en_rama_de_trabajo(repo, command):
    git(repo, "checkout", "-b", "feature/1-x")
    assert bash(repo, command) == 2


@pytest.mark.parametrize("command", [
    "git commit -m 'feat: x'",
    "git push -u origin feature/1-x",
    "git push --force-with-lease origin feature/1-x",
    "git tag",
    "git tag -l 'v*'",
    "git status",
    "git add src/main.py",
    "git add -f build/salida.txt",
    "python -m pytest",
    "echo 'git commit en main' > nota.txt",
    "gh pr create --title x --body y",
    "git reset HEAD a.txt",
])
def test_permite_en_rama_de_trabajo(repo, command):
    git(repo, "checkout", "-b", "feature/1-x")
    assert bash(repo, command) == 0


def test_permite_lectura_en_main(repo):
    assert bash(repo, "git status && git log --oneline -3") == 0
    assert bash(repo, "git checkout -b feature/2-y") == 0


def test_cd_a_otro_repo_en_main(repo, tmp_path):
    otro = tmp_path / "otro"
    otro.mkdir()
    git(otro, "init", "-b", "main")
    git(repo, "checkout", "-b", "feature/1-x")
    assert bash(repo, 'cd "%s" && git commit -m x' % otro) == 2
    assert bash(repo, 'git -C "%s" commit -m x' % otro) == 2


def test_ramas_protegidas_configurables(repo):
    (repo / ".claude").mkdir()
    (repo / ".claude" / "project.json").write_text(
        json.dumps({"protected_branches": ["develop"]}), encoding="utf-8")
    assert bash(repo, "git commit -m x") == 0
    git(repo, "checkout", "-b", "develop")
    assert bash(repo, "git commit -m x") == 2


def test_entrada_rara_no_bloquea(repo):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    out = subprocess.run([sys.executable, CMD], input="esto no es json",
                         capture_output=True, text=True, env=env)
    assert out.returncode == 0
    assert bash(repo, "echo 'comilla sin cerrar") == 0


def test_mensaje_explica_el_motivo(repo):
    code, err = run(CMD, {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"},
                          "cwd": str(repo)}, repo)
    assert code == 2 and "main" in err


def test_paths_github(repo):
    assert edit(repo, ".github/workflows/ci.yml") == 2
    assert edit(repo, str(repo / ".github" / "x.yml")) == 2
    assert edit(repo, "src/main.py") == 0
    assert edit(repo, "docs/github.md") == 0


def test_paths_readonly(repo, tmp_path):
    modelos = tmp_path / "modelos"
    modelos.mkdir()
    (repo / ".claude").mkdir()
    (repo / ".claude" / "project.json").write_text(json.dumps({"components": {
        "backend": {"path": "."},
        "models": {"path": "../modelos", "readonly": True}}}), encoding="utf-8")
    assert edit(repo, str(modelos / "modelo.py")) == 2
    assert edit(repo, "src/main.py") == 0


@pytest.mark.parametrize("command", [
    "cp src/Page.razor /tmp_ref_backup.razor",
    "echo hola > /tmp_ref_backup.razor",
    "cat a.txt >> /etc/nota.txt",
    "echo x | tee /opt/salida.log",
    "git status && touch /fuera.txt",
    'cp a.txt "/Program Files/copia.txt"',
])
def test_bloquea_escritura_fuera_del_proyecto(repo, command):
    git(repo, "checkout", "-b", "feature/1-x")
    assert bash(repo, command) == 2


@pytest.mark.parametrize("command", [
    "cp a.txt .claude/tmp/copia.txt",
    "echo hola > salida.txt",
    "python -m pytest > /dev/null 2>&1",
    "dotnet test 2>&1 | tee .claude/tmp/test.log",
    "echo 'a > /etc/b' > nota.txt",
    "cp a.txt $TMPDIR/copia.txt",
    "mkdir -p .claude/tmp && cp a.txt .claude/tmp/",
    "cat /etc/hostname",
    "ls /",
])
def test_permite_escritura_dentro_o_lectura_fuera(repo, command):
    git(repo, "checkout", "-b", "feature/1-x")
    assert bash(repo, command) == 0


def test_permite_escribir_en_el_propio_repo_con_ruta_absoluta(repo):
    git(repo, "checkout", "-b", "feature/1-x")
    assert bash(repo, 'cp a.txt "%s"' % (repo / "b.txt")) == 0


def test_paths_fuera_del_proyecto(repo, tmp_path):
    assert edit(repo, "/tmp_ref_backup.razor") == 2
    assert edit(repo, "/etc/x.conf") == 2
    assert edit(repo, ".claude/tmp/nota.md") == 0
    assert edit(repo, os.path.join(os.path.expanduser("~"), ".claude", "plans", "p.md")) == 0


def test_paths_componente_en_otro_repo(repo, tmp_path):
    front = tmp_path / "front"
    front.mkdir()
    (repo / ".claude").mkdir()
    (repo / ".claude" / "project.json").write_text(json.dumps({"components": {
        "backend": {"path": "."}, "frontend": {"path": "../front"}}}), encoding="utf-8")
    assert edit(repo, str(front / "Page.razor")) == 0
