import json
import os
import subprocess
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def frontmatter(path):
    raw = open(path, "rb").read()
    assert not raw.startswith(b"\xef\xbb\xbf"), "BOM en " + path
    text = raw.decode("utf-8")
    assert text.startswith("---\n"), "el --- no es la primera línea: " + path
    head = text.split("\n---\n", 1)[0].splitlines()[1:]
    return dict(line.split(":", 1) for line in head if ":" in line)


def test_agentes():
    folder = os.path.join(KIT, "agents")
    names = sorted(os.listdir(folder))
    assert names == ["backend-dev.md", "frontend-dev.md", "reviewer.md", "spec-writer.md",
                     "test-writer.md"]
    for name in names:
        fm = frontmatter(os.path.join(folder, name))
        assert fm["name"].strip() == name[:-3]
        assert fm["description"].strip()
    assert "Write" not in frontmatter(os.path.join(folder, "reviewer.md"))["tools"]
    assert "Bash" not in frontmatter(os.path.join(folder, "spec-writer.md"))["tools"]


def test_skills():
    folder = os.path.join(KIT, "skills")
    assert sorted(os.listdir(folder)) == ["adopt", "feature", "fix", "resume"]
    for name in os.listdir(folder):
        fm = frontmatter(os.path.join(folder, name, "SKILL.md"))
        assert fm["name"].strip() == name
        assert fm["description"].strip()
        assert fm["disable-model-invocation"].strip() == "true"


def test_plantillas_json():
    for name in ("project.json", "settings.json"):
        with open(os.path.join(KIT, "templates", name), encoding="utf-8") as fh:
            json.load(fh)


def test_a_markdown_docx_y_xlsx(tmp_path):
    import zipfile
    openpyxl = __import__("pytest").importorskip("openpyxl")
    script = os.path.join(KIT, "scripts", "a_markdown.py")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "inputs"
    ws.append(["variable", "unidad"])
    ws.append(["feed_rate", "kg/h"])
    xlsx = tmp_path / "p.xlsx"
    wb.save(str(xlsx))
    out = tmp_path / "sub" / "p.md"
    subprocess.run([sys.executable, script, str(xlsx), "-o", str(out)], check=True)
    text = out.read_text(encoding="utf-8")
    assert "## Hoja: inputs" in text and "| feed_rate | kg/h |" in text

    doc = ('<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/'
           'wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Hola</w:t></w:r></w:p>'
           '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>a</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r>'
           '<w:t>b</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>')
    docx = tmp_path / "d.docx"
    with zipfile.ZipFile(str(docx), "w") as zf:
        zf.writestr("word/document.xml", doc)
    res = subprocess.run([sys.executable, script, str(docx)], check=True, capture_output=True)
    md = res.stdout.decode("utf-8")
    assert "Hola" in md and "| a | b |" in md


def test_reglas_del_kit():
    def text(*parts):
        return open(os.path.join(KIT, "templates", *parts), encoding="utf-8").read()
    rules = text("kit-rules.md")
    assert "## Preferencias del proyecto" in rules and ".claude/kit/director.md" in rules
    assert len(rules) < 5500, "kit-rules.md se carga en cada sesión y en cada agente: mantenlo corto"
    director = text("kit", "director.md")
    assert "Sin flujo" in rules and "nunca edites estando en" in rules
    for section in ("## Gastar menos", "## Modos de /feature", "## Modelos",
                    "## El tablero", "## Cerrar una tarea"):
        assert section in director, section
    assert "## `none`" in text("kit", "pruebas.md")
    assert "max_criteria" in text("kit", "specs.md")
    assert "@.claude/kit-rules.md" in text("CLAUDE.main.md")
    prefs = json.loads(text("project.json"))["preferences"]
    assert prefs["tests"] == "critical" and prefs["close_tests"] == "touched"


def test_a_markdown_pdf(tmp_path):
    pytest = __import__("pytest")
    pytest.importorskip("pypdf")
    reportlab = pytest.importorskip("reportlab.pdfgen.canvas")
    pdf = tmp_path / "ga.pdf"
    c = reportlab.Canvas(str(pdf))
    c.drawString(72, 720, "Grant Agreement RENEUMA")
    c.save()
    script = os.path.join(KIT, "scripts", "a_markdown.py")
    res = subprocess.run([sys.executable, script, str(pdf)], check=True, capture_output=True)
    md = res.stdout.decode("utf-8")
    assert "## Página 1" in md and "Grant Agreement RENEUMA" in md
