"""Genera docs/operaciones.csv con conteos de PDA y CYK; no mide tiempos de reloj."""

import argparse
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from recognizer import cyk, pda
from recognizer.grammar import tokenizar

BASE = "she eats the cake"
FAMILIAS = {
    # familia: (descripción, constructor de la frase a partir de k, valores de k)
    "F": ("aceptada: BASE + k veces ' with a fork'", lambda k: BASE + " with a fork" * k, range(16)),
    "R": ("rechazo tardío: F_k + ' with' (PP incompleto)", lambda k: BASE + " with a fork" * k + " with", range(16)),
    "E": ("rechazo temprano: 'cooks ' + F_k (orden inválido)", lambda k: "cooks " + BASE + " with a fork" * k, (0, 5, 10, 15)),
    "D": ("palabra desconocida: F_k + ' dances'", lambda k: BASE + " with a fork" * k + " dances", (0, 5, 10, 15)),
}


def filas():
    for familia, (_, construir, valores) in FAMILIAS.items():
        for k in valores:
            frase = construir(k)
            tokens = tokenizar(frase)
            r_pda, r_cyk = pda.recognize(tokens), cyk.recognize(tokens)
            agotamiento = r_pda.evidencia["agotamiento"]
            yield {
                "familia": familia, "k": k, "n": len(tokens), "frase": frase,
                "coinciden": r_pda.estado == r_cyk.estado,
                "pda_estado": r_pda.estado,
                "pda_causa": agotamiento["causa"] if agotamiento else "",
                "pda_limite": r_pda.evidencia["limite_configuraciones"] or "",
                **{f"pda_{clave}": valor for clave, valor in r_pda.operaciones.items()},
                "cyk_estado": r_cyk.estado,
                **{f"cyk_{clave}": valor for clave, valor in r_cyk.operaciones.items()},
            }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", default=str(RAIZ / "docs" / "operaciones.csv"),
                        help="Ruta del CSV; '-' imprime en stdout")
    argumentos = parser.parse_args()
    datos = list(filas())

    def escribir(destino):
        escritor = csv.DictWriter(destino, fieldnames=list(datos[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(datos)

    if argumentos.salida == "-":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        escribir(sys.stdout)
    else:
        with open(argumentos.salida, "w", encoding="utf-8", newline="") as archivo:
            escribir(archivo)
        print(f"{len(datos)} filas escritas en {argumentos.salida}")
    discrepancias = [fila["frase"] for fila in datos if not fila["coinciden"]]
    for frase in discrepancias:
        print(f"Discrepancia PDA/CYK: {frase}", file=sys.stderr)
    return 1 if discrepancias else 0


if __name__ == "__main__":
    raise SystemExit(main())
