import json
import os
import subprocess
import sys

import pytest

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL = os.path.join(KIT, "install.py")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo)] + list(args), check=True,
                          capture_output=True, text=True).stdout


def install(repo, *args):
    return subprocess.run([sys.executable, INSTALL, str(repo)] + list(args),
                          capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "mi proyecto"
    r.mkdir()
    git(r, "init", "-b", "main")
    git(r, "config", "user.email", "t@example.com")
    git(r, "config", "user.name", "t")
    (r / "README.md").write_text("hola\n", encoding="utf-8")
    git(r, "add", ".")
    git(r, "commit", "-m", "inicial")
    return r


def test_no_es_repo(tmp_path):
    assert install(tmp_path).returncode != 0


def test_dry_run_no_toca_nada(repo):
    out = install(repo, "--dry-run", "--exclude-local")
    assert out.returncode == 0
    assert not (repo / ".claude").exists()
    assert not (repo / "CLAUDE.md").exists()
    assert git(repo, "status", "--porcelain") == ""


def test_instalacion_local_deja_git_limpio(repo):
    out = install(repo, "--exclude-local")
    assert out.returncode == 0, out.stderr
    assert git(repo, "status", "--porcelain") == ""
    for rel in ["CLAUDE.md", "TASKS.md", ".claude/project.json", ".claude/settings.json",
                ".claude/kit-version", ".claude/agents/reviewer.md",
                ".claude/skills/feature/SKILL.md", ".claude/scripts/guard_commands.py",
                ".claude/templates/spec.md", ".claude/kit-rules.md",
                ".claude/kit/director.md", ".claude/kit/pruebas.md", ".claude/kit/specs.md"]:
        assert (repo / rel).exists(), rel
    assert json.loads((repo / ".claude/project.json").read_text(encoding="utf-8"))["name"] == "mi proyecto"
    claude_md = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    assert "# mi proyecto" in claude_md and "@.claude/kit-rules.md" in claude_md


def test_instalacion_con_gitignore(repo):
    assert install(repo).returncode == 0
    assert git(repo, "status", "--porcelain").strip() == "?? .gitignore"
    assert install(repo, "--update").returncode == 0
    assert (repo / ".gitignore").read_text(encoding="utf-8").count("idener-claude-kit") == 2


def test_no_se_instala_dos_veces(repo):
    assert install(repo, "--exclude-local").returncode == 0
    assert install(repo, "--exclude-local").returncode != 0


def test_update_sin_instalar(repo):
    assert install(repo, "--update").returncode != 0


def test_update_conserva_lo_del_proyecto(repo):
    install(repo, "--exclude-local")
    (repo / "CLAUDE.md").write_text("mio\n", encoding="utf-8")
    (repo / "TASKS.md").write_text("tablero\n", encoding="utf-8")
    (repo / ".claude/project.json").write_text('{"name": "x"}', encoding="utf-8")
    (repo / ".claude/agents/propio.md").write_text("---\nname: propio\n---\n", encoding="utf-8")
    settings = json.loads((repo / ".claude/settings.json").read_text(encoding="utf-8"))
    settings["permissions"]["allow"].append("Bash(make test:*)")
    settings["hooks"] = {}
    (repo / ".claude/settings.json").write_text(json.dumps(settings), encoding="utf-8")
    (repo / ".claude/agents/reviewer.md").write_text("roto", encoding="utf-8")
    (repo / ".claude/kit-rules.md").write_text("viejo", encoding="utf-8")

    out = install(repo, "--update", "--exclude-local")
    assert out.returncode == 0, out.stderr
    assert (repo / "CLAUDE.md").read_text(encoding="utf-8") == "mio\n"
    assert (repo / "TASKS.md").read_text(encoding="utf-8") == "tablero\n"
    assert (repo / ".claude/project.json").read_text(encoding="utf-8") == '{"name": "x"}'
    assert (repo / ".claude/agents/propio.md").exists()
    assert (repo / ".claude/agents/reviewer.md").read_text(encoding="utf-8").startswith("---")
    assert (repo / ".claude/kit-rules.md").read_text(encoding="utf-8").startswith("# Reglas del kit")
    assert "anterior a la 0.1.3" in out.stdout
    after = json.loads((repo / ".claude/settings.json").read_text(encoding="utf-8"))
    assert "Bash(make test:*)" in after["permissions"]["allow"]
    assert "PreToolUse" in after["hooks"]
    assert git(repo, "status", "--porcelain") == ""


def test_secondary(repo):
    out = install(repo, "--role", "secondary", "--exclude-local")
    assert out.returncode == 0
    assert (repo / "CLAUDE.md").exists()
    assert not (repo / ".claude").exists()
    assert git(repo, "status", "--porcelain") == ""


def test_avisa_si_ya_esta_versionado(repo):
    (repo / "CLAUDE.md").write_text("x\n", encoding="utf-8")
    git(repo, "add", "CLAUDE.md")
    git(repo, "commit", "-m", "claude")
    out = install(repo, "--exclude-local")
    assert "ya están versionados" in out.stdout
