"""Imprime conteos reproducibles; no mide tiempos ni ejecuta CYK."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recognizer.grammar import tokenizar
from recognizer.pda import recognize


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    frases = ["he cooks", "she eats the cake"]
    for k in (1, 2, 3):
        frase = "she eats the cake" + " with a fork" * k
        frases.extend((frase, frase + " with"))
    escritor = None
    for frase in frases:
        resultado = recognize(tokenizar(frase))
        fila = {"frase": frase, "n": resultado.n, "estado": resultado.estado, **resultado.operaciones}
        if escritor is None:
            escritor = csv.DictWriter(sys.stdout, fieldnames=list(fila), lineterminator="\n")
            escritor.writeheader()
        escritor.writerow(fila)


if __name__ == "__main__":
    main()
