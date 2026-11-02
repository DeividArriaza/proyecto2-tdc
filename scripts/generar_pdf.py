"""Convierte el informe Markdown a HTML autónomo y PDF APA mediante Chrome headless."""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

RAIZ = Path(__file__).resolve().parents[1]
CSS = """
@page {
  size: letter; margin: 1in;
  @top-right { content: counter(page); font: 12pt "Times New Roman"; color: black; }
}
* { box-sizing: border-box; }
body { font: 12pt/2 "Times New Roman", serif; color: black; margin: 0; text-align: left; }
h1, h2, h3, h4, h5, h6 { font-size: 12pt; line-height: 2; margin: 0; break-after: avoid; }
h1, h2 { text-align: center; font-weight: bold; }
h3 { text-align: left; font-weight: bold; }
h4 { text-align: left; font-weight: bold; font-style: italic; }
h5, h6 { text-indent: .5in; font-weight: bold; }
h6 { font-style: italic; }
p { margin: 0; text-indent: .5in; orphans: 2; widows: 2; }
.title-page { text-align: center; break-after: page; padding-top: .75in; }
.title-page p { text-align: center; text-indent: 0; }
.title-page .authors { margin-top: 24pt; }
.abstract { break-after: page; }
.abstract p { text-indent: 0; }
.abstract .keywords { text-indent: .5in; }
.body-title { break-before: page; }
.references, .appendix { break-before: page; }
.references p { padding-left: .5in; text-indent: -.5in; }
table { border-collapse: collapse; width: 100%; font-size: 12pt; line-height: 1; margin: 0; }
table { border-top: 1px solid black; border-bottom: 1px solid black; }
th, td { border: none; padding: 4pt 3pt; text-align: left; vertical-align: top; }
th { text-align: center; border-bottom: 1px solid black; font-weight: normal; }
thead { display: table-header-group; }
tr, pre, svg, figure, .table-block { break-inside: avoid; }
figure, .table-block { margin: 24pt 0; }
figure p, .table-block p { text-indent: 0; }
.trace td:nth-child(2) { font-family: Consolas, monospace; font-size: 10pt; }
pre { padding: 0; margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.5; }
code { font-family: Consolas, "Courier New", monospace; font-size: 10pt; }
td code { overflow-wrap: anywhere; }
a { color: black; text-decoration: none; overflow-wrap: anywhere; }
svg { display: block; width: 100%; height: auto; margin: 0; }
.toc { break-before: page; break-after: page; }
.toc h2 { break-before: auto; }
.toc ul { list-style: none; padding-left: .25in; margin: 0; }
.toc > ul { padding-left: 0; }
.toc li { margin: 0; }
.formula { text-indent: 0; }
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome", type=Path, help="Ruta al ejecutable de Chrome o Chromium")
    args = parser.parse_args()
    try:
        import markdown
    except ImportError as error:
        raise SystemExit("Instale requirements-docs.txt con el Python que ejecuta este script.") from error
    chrome = args.chrome or Path(os.environ.get(
        "CHROME_PATH", "C:/Program Files/Google/Chrome/Application/chrome.exe"))
    if not chrome.is_file():
        encontrado = shutil.which("google-chrome") or shutil.which("chromium")
        if not encontrado:
            raise SystemExit("Chrome no encontrado: use --chrome RUTA o CHROME_PATH.")
        chrome = Path(encontrado)
    docs = RAIZ / "docs"
    fuente = (docs / "informe.md").read_text(encoding="utf-8")
    conversor = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "md_in_html"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    cuerpo = conversor.convert(fuente)
    cuerpo = cuerpo.replace('<div class="toc">', '<div class="toc"><h2>Índice</h2>')

    def embeber(coincidencia: re.Match) -> str:
        ruta = (docs / coincidencia.group(1)).resolve()
        if not ruta.is_relative_to(docs.resolve()) or ruta.suffix != ".svg":
            raise ValueError("Se esperaba una figura SVG dentro de docs")
        return ruta.read_text(encoding="utf-8")

    cuerpo = re.sub(r'<img[^>]*src="([^"]+\.svg)"[^>]*/*>', embeber, cuerpo)
    html = '<!doctype html><html lang="es"><meta charset="utf-8">'
    html += '<title>Proyecto 2 — PDA y CYK</title><style>' + CSS + '</style><body>'
    html += cuerpo + '</body></html>\n'
    salida_html = docs / "informe.html"
    salida_html.write_text(html, encoding="utf-8", newline="\n")
    salida_pdf = docs / "informe.pdf"
    # Se conserva el perfil temporal; el coordinador puede limpiarlo tras revisar la entrega.
    perfil = tempfile.mkdtemp(prefix="tdc-informe-chrome-")
    comando = [str(chrome), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
               "--disable-extensions", "--no-first-run", f"--user-data-dir={perfil}",
               f"--print-to-pdf={salida_pdf}", salida_html.as_uri()]
    resultado = subprocess.run(comando, capture_output=True, timeout=90)
    if resultado.returncode or not salida_pdf.is_file():
        raise SystemExit(resultado.stderr.decode("utf-8", errors="replace"))
    print(f"HTML: {salida_html}\nPDF: {salida_pdf}")


if __name__ == "__main__":
    main()
