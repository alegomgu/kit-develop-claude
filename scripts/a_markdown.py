#!/usr/bin/env python3
"""Convierte un Excel (.xlsx), un Word (.docx) o un PDF a Markdown para que lo lean los agentes.

Uso: python a_markdown.py <fichero> [-o salida.md]

.xlsx necesita openpyxl. .docx se lee directamente del XML, sin dependencias: saca párrafos y
tablas, sin formato. .pdf necesita pypdf y saca solo el texto, página a página. Sin -o escribe
por la salida estándar.
"""
import argparse
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def cell(value):
    if value is None:
        return ""
    text = str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")
    return text.strip()


def table_md(rows):
    rows = [r for r in rows if any(c != "" for c in r)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [list(r) + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def xlsx_md(path):
    try:
        import openpyxl
    except ImportError:
        sys.exit("Falta openpyxl: pip install openpyxl")
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    out = ["# " + os.path.basename(path)]
    for ws in wb.worksheets:
        rows = [[cell(c) for c in row] for row in ws.iter_rows(values_only=True)]
        used = max((i + 1 for r in rows for i, c in enumerate(r) if c != ""), default=0)
        rows = [r[:used] for r in rows]
        out.append("\n## Hoja: " + ws.title + "\n")
        out.append(table_md(rows) or "_(vacía)_")
    return "\n".join(out) + "\n"


def docx_md(path):
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find(W + "body")
    out = ["# " + os.path.basename(path), ""]

    def text_of(node):
        return "".join(t.text or "" for t in node.iter(W + "t")).strip()

    for node in list(body):
        if node.tag == W + "p":
            text = text_of(node)
            if text:
                style = node.find(W + "pPr/" + W + "pStyle")
                name = (style.get(W + "val") or "") if style is not None else ""
                if name.lower().startswith(("heading", "ttulo", "titulo")):
                    level = "".join(ch for ch in name if ch.isdigit()) or "1"
                    text = "#" * (min(int(level), 5) + 1) + " " + text
                out += [text, ""]
        elif node.tag == W + "tbl":
            rows = [[cell(text_of(tc)) for tc in tr.findall(W + "tc")]
                    for tr in node.findall(W + "tr")]
            out += [table_md(rows), ""]
    return "\n".join(out) + "\n"


def pdf_md(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("Falta pypdf: pip install pypdf")
    reader = PdfReader(path)
    out = ["# " + os.path.basename(path)]
    for number, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        out.append("\n## Página %d\n" % number)
        out.append(text or "_(sin texto: puede ser una página escaneada)_")
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("fichero")
    parser.add_argument("-o", "--salida")
    args = parser.parse_args()
    ext = os.path.splitext(args.fichero)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        text = xlsx_md(args.fichero)
    elif ext == ".docx":
        text = docx_md(args.fichero)
    elif ext == ".pdf":
        text = pdf_md(args.fichero)
    else:
        sys.exit("Formato no soportado: " + ext + " (solo .xlsx, .docx y .pdf)")
    if args.salida:
        folder = os.path.dirname(os.path.abspath(args.salida))
        os.makedirs(folder, exist_ok=True)
        with open(args.salida, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("Escrito: " + args.salida)
    else:
        sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
