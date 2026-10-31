"""Consola de reconocimiento y exportación de evidencia UTF-8."""

import argparse
import importlib
import json
import sys
from pathlib import Path

from recognizer.grammar import tokenizar
from recognizer.pda import describir, recognize


def _positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except ValueError as error:
        raise argparse.ArgumentTypeError("El límite debe ser un entero positivo") from error
    if numero <= 0:
        raise argparse.ArgumentTypeError("El límite debe ser mayor que cero")
    return numero


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Reconoce palabras separadas por espacios en blanco sin cambiar mayúsculas ni signos.",
        epilog="Vacía/desconocidas: rechazo. Salidas: 0 aceptada, 1 rechazada, 2 inconclusa/error.",
    )
    parser.add_argument("frase")
    parser.add_argument("--metodo", choices=("pda", "cyk", "ambos"), default="ambos")
    parser.add_argument("--traza", action="store_true")
    parser.add_argument("--json", type=Path, metavar="RUTA")
    parser.add_argument("--limite", type=_positivo, metavar="N", help="Máximo de expansiones PDA")
    argumentos = parser.parse_args(argv)
    tokens = tokenizar(argumentos.frase)
    resultados = []
    falta_cyk = False
    if argumentos.metodo in ("pda", "ambos"):
        resultados.append(recognize(tokens, limite_configuraciones=argumentos.limite))
    if argumentos.metodo in ("cyk", "ambos"):
        try:
            cyk = importlib.import_module("recognizer.cyk")
        except ModuleNotFoundError as error:
            if error.name != "recognizer.cyk":
                raise
            print("CYK no disponible todavía (tarea C2 de Carlos)")
            falta_cyk = True
        else:
            resultados.append(cyk.recognize(tokens))
    for resultado in resultados:
        print(f"{resultado.metodo.upper()}: {resultado.estado}. {resultado.motivo}")
        print("Operaciones:", json.dumps(resultado.operaciones, ensure_ascii=False, sort_keys=True))
        if argumentos.traza:
            if resultado.metodo == "pda":
                recorrido = resultado.evidencia.get("recorrido_aceptante", [])
                if recorrido:
                    descripciones = [describir(recorrido[0]["antes"], tokens)]
                    descripciones.extend(describir(paso["despues"], tokens) for paso in recorrido)
                    print(" ⊢ ".join(descripciones))
                else:
                    print("Agotamiento:", json.dumps(resultado.evidencia["agotamiento"], ensure_ascii=False))
            else:
                print("Tabla CYK:", json.dumps(resultado.evidencia.get("tabla", []), ensure_ascii=False))
    if argumentos.json:
        try:
            argumentos.json.parent.mkdir(parents=True, exist_ok=True)
            argumentos.json.write_text(
                json.dumps([r.to_dict() for r in resultados], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n",
            )
        except OSError as error:
            print(f"Error al exportar JSON: {error}", file=sys.stderr)
            return 2
    if falta_cyk and argumentos.metodo == "cyk":
        return 2
    estados = {resultado.estado for resultado in resultados}
    if "inconclusa" in estados or len(estados) > 1:
        if len(estados) > 1:
            print("Los métodos difieren o alguno quedó inconcluso; revisar la evidencia")
        return 2
    return 0 if estados == {"aceptada"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
