"""Genera gráficas SVG reproducibles con biblioteca estándar, sin medir tiempos."""

import csv
from html import escape
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
COLORES = ("#176b96", "#b14b22", "#6248a0", "#24774d")


def grafica(filas: list[dict[str, str]], log: bool = False) -> str:
    ancho, alto = 960, 590
    x0, y0, w, h = 100, 80, 810, 350
    series = []
    for familia in ("F", "R"):
        datos = [f for f in filas if f["familia"] == familia]
        for campo, nombre in (("pda_simbolos_copiados_pila", "PDA: símbolos copiados"),
                              ("cyk_comprobaciones_binarias", "CYK: reglas comprobadas")):
            series.append((f"{nombre} · {familia}",
                           [(int(f["n"]), int(f[campo])) for f in datos]))
    transformar = math.log10 if log else float
    xmin = transformar(4) if log else 0
    xmax = transformar(50)
    ymax = 6 if log else 350000

    def punto(n: float, valor: float) -> tuple[float, float]:
        return (x0 + w * (transformar(n) - xmin) / (xmax - xmin),
                y0 + h * (1 - transformar(valor) / ymax))

    titulo = "Operaciones por longitud · " + ("escala log–log" if log else "escala lineal")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" '
           f'role="img" aria-label="{titulo}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="Segoe UI,Arial,sans-serif" font-size="17" fill="#203040">',
           f'<text x="100" y="35" font-size="25" font-weight="bold">{titulo}</text>']
    yticks = [10 ** i for i in range(7)] if log else list(range(0, 350001, 50000))
    for valor in yticks:
        y = punto(4, valor)[1]
        etiqueta = f"10^{int(math.log10(valor))}" if log else f"{valor:,}".replace(",", " ")
        svg += [f'<path d="M{x0},{y:.2f} h{w}" stroke="#dce2e8"/>',
                f'<text x="90" y="{y + 6:.2f}" text-anchor="end">{etiqueta}</text>']
    for n in ([4, 7, 10, 20, 30, 50] if log else [0, 10, 20, 30, 40, 50]):
        x = punto(n, 1)[0]
        svg.append(f'<text x="{x:.2f}" y="455" text-anchor="middle">{n}</text>')
    svg += [f'<path d="M{x0},{y0} v{h} h{w}" fill="none" stroke="#203040"/>',
            '<text x="505" y="485" text-anchor="middle">n (palabras)</text>',
            '<text transform="translate(25,255) rotate(-90)" text-anchor="middle">'
            'Operaciones contadas</text>']
    for indice, (nombre, datos) in enumerate(series):
        color = COLORES[indice]
        puntos = " ".join(f"{x:.2f},{y:.2f}" for x, y in (punto(n, v) for n, v in datos))
        trazo = ' stroke-dasharray="8 5"' if indice >= 2 else ""
        svg.append(f'<polyline points="{puntos}" fill="none" stroke="{color}" '
                   f'stroke-width="3"{trazo}/>')
        for n, valor in datos:
            x, y = punto(n, valor)
            svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{color}"/>')
        lx, ly = 110 + (indice % 2) * 440, 520 + (indice // 2) * 28
        svg += [f'<path d="M{lx},{ly - 6} h30" stroke="{color}" stroke-width="3"{trazo}/>',
                f'<text x="{lx + 40}" y="{ly}">{escape(nombre)}</text>']
    svg.append('<text x="100" y="582" font-size="15">'
               'F: aceptadas · R: rechazadas con PP incompleto. Las unidades difieren entre métodos.</text>')
    return "\n".join(svg + ["</g></svg>", ""])


def main() -> None:
    with (RAIZ / "docs/operaciones.csv").open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    destino = RAIZ / "docs/figuras"
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, log in (("operaciones-lineal.svg", False), ("operaciones-log.svg", True)):
        (destino / nombre).write_text(grafica(filas, log), encoding="utf-8", newline="\n")
        print(destino / nombre)


if __name__ == "__main__":
    main()
