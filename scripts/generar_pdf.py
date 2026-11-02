"""Convierte el informe Markdown a HTML autónomo y PDF A4 mediante Chrome headless."""

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
  size: A4; margin: 2cm;
  @bottom-center { content: "Proyecto 2 · TDC  |  " counter(page); font-size: 9pt; color: #526170; }
}
@page:first { @bottom-center { content: none; } }
* { box-sizing: border-box; }
body { font: 11pt/1.42 "Segoe UI", Arial, sans-serif; color: #172635; margin: 0; }
h1, h2, h3 { line-height: 1.2; color: #174e70; break-after: avoid; }
h1 { font-size: 27pt; margin-top: 26mm; }
h2 { font-size: 18pt; margin: 0 0 8mm; }
.major { break-before: page; }
h3 { font-size: 13pt; margin-top: 7mm; }
p { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 5mm 0; }
th, td { border: 1px solid #b4c2cb; padding: 2mm; text-align: left; vertical-align: top; }
th { background: #eaf1f5; }
thead { display: table-header-group; }
tr, pre, svg, figure { break-inside: avoid; }
figure { margin: 0; }
figure + figure { break-before: page; }
pre { background: #f1f4f6; padding: 3mm; white-space: pre-wrap; overflow-wrap: anywhere; }
code { font-family: Consolas, "DejaVu Sans Mono", monospace; font-size: 9pt; }
td code { font-size: 8pt; overflow-wrap: anywhere; }
a { color: #174e70; text-decoration: none; overflow-wrap: anywhere; }
svg { display: block; width: 100%; height: auto; margin: 5mm 0; }
.toc { break-before: page; break-after: page; }
.toc h2 { break-before: auto; }
h3[id^="33-"], h3[id^="62-"] { break-before: page; }
.toc ul { list-style: none; padding-left: 0; }
.toc li { margin: 4mm 0; }
.caption { font-size: 9pt; color: #465968; }
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
        extensions=["tables", "fenced_code", "toc"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    cuerpo = conversor.convert(fuente)
    cuerpo = cuerpo.replace('<div class="toc">', '<div class="toc"><h2>Índice</h2>')
    cuerpo = re.sub(r'<h2 id="([^\"]+)">([3-9]|10)\.',
                    r'<h2 class="major" id="\1">\2.', cuerpo)
    cuerpo = re.sub(r'<p>(<img[^>]+>)</p>\s*<p>(Figura [12]\..*?)</p>',
                    r'<figure>\1<figcaption class="caption">\2</figcaption></figure>',
                    cuerpo, flags=re.DOTALL)

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
