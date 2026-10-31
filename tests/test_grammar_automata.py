"""Validación del enunciado, la extensión y la procedencia del código."""

from dataclasses import FrozenInstanceError
from pathlib import Path
import unittest

from recognizer.automata import AutomataPila, construir_pda
from recognizer.grammar import G, Gramatica, es_cnf, tokenizar
from recognizer.proyecto1.constants import EPSILON
from recognizer.proyecto1.errors import AutomataValidationError
from recognizer.proyecto1.models import AFN


class PruebasGramatica(unittest.TestCase):
    def test_gramatica_exacta_del_pdf(self):
        # Transcripción independiente del PDF, incluidas las alternativas de cada fila.
        esperado = {
            "S": "NP VP", "VP": "VP PP|V NP|cooks|drinks|eats|cuts", "PP": "P NP",
            "NP": "Det N|he|she", "V": "cooks|drinks|eats|cuts", "P": "in|with",
            "N": "cat|dog|beer|cake|juice|meat|soup|fork|knife|oven|spoon", "Det": "a|the",
        }
        reglas = {v: tuple(tuple(r.split()) for r in texto.split("|")) for v, texto in esperado.items()}
        self.assertEqual(dict(G.producciones), reglas)
        self.assertEqual(sum(map(len, G.producciones.values())), 30)
        self.assertEqual(G.variables, frozenset(esperado))
        terminales = {s for alternativas in reglas.values() for r in alternativas for s in r} - set(reglas)
        self.assertEqual(G.terminales, terminales)
        self.assertEqual(G.inicial, "S")
        self.assertTrue(es_cnf(G))

    def test_tokenizacion(self):
        self.assertEqual(tokenizar(" \the  cooks\n"), ["he", "cooks"])
        self.assertEqual(tokenizar(" \t\n"), [])
        self.assertEqual(tokenizar("He cooks."), ["He", "cooks."])

    def test_inmutabilidad_y_copia(self):
        reglas = {"S": [["a"]]}
        g = Gramatica(frozenset({"S"}), frozenset({"a"}), reglas, "S")
        reglas["S"][0].append("a")
        self.assertEqual(g.producciones["S"], (("a",),))
        with self.assertRaises(TypeError):
            g.producciones["S"] = ()
        with self.assertRaises(FrozenInstanceError):
            g.inicial = "X"

    def test_gramatica_invalida(self):
        for variables, terminales, reglas, inicial in (
            ({"S"}, {"a"}, {"S": (("b",),)}, "S"),
            ({"S"}, {"a"}, {"T": (("a",),)}, "S"),
            ({"S"}, {"S"}, {}, "S"),
            ({"S"}, {EPSILON}, {}, "S"),
            ({"S"}, {"a"}, {}, "T"),
        ):
            with self.subTest(reglas=reglas, inicial=inicial):
                with self.assertRaises(ValueError):
                    Gramatica(variables, terminales, reglas, inicial)

    def test_cnf_estricta(self):
        for regla in ((), ("S",), ("a", "a"), ("S", "S", "S")):
            g = Gramatica({"S"}, {"a"}, {"S": (regla,)}, "S")
            self.assertFalse(es_cnf(g))


class PruebasAutomata(unittest.TestCase):
    def datos(self):
        return dict(
            estados={0, 1}, alfabeto={"a"}, inicial=0, aceptacion={1},
            alfabeto_pila={"Z", "A"}, simbolo_inicial_pila="Z",
            transiciones_pila={(0, "a", "Z"): {(1, ("A", "Z"))}},
        )

    def test_herencia_real_y_congelado(self):
        pda = AutomataPila(**self.datos())
        self.assertIsInstance(pda, AFN)
        self.assertIsInstance(pda.estados, frozenset)
        self.assertFalse(pda.poda_longitud_segura)
        with self.assertRaises(FrozenInstanceError):
            pda.inicial = 1
        with self.assertRaises(TypeError):
            pda.transiciones_pila[(0, "a", "Z")] = frozenset()

    def test_validaciones_heredadas(self):
        for campo, valor in (("estados", set()), ("inicial", 9), ("aceptacion", {9}),
                             ("alfabeto", {EPSILON})):
            with self.subTest(campo=campo):
                datos = self.datos()
                datos[campo] = valor
                with self.assertRaises(AutomataValidationError):
                    AutomataPila(**datos)

    def test_validaciones_pila(self):
        variantes = [
            {"simbolo_inicial_pila": "X"}, {"alfabeto_pila": {"Z", EPSILON}},
            {"transiciones_pila": {(9, "a", "Z"): {(1, ())}}},
            {"transiciones_pila": {(0, "b", "Z"): {(1, ())}}},
            {"transiciones_pila": {(0, "a", "X"): {(1, ())}}},
            {"transiciones_pila": {(0, "a", "Z"): {(9, ())}}},
            {"transiciones_pila": {(0, "a", "Z"): {(1, ("X",))}}},
            {"transiciones": {(0, "a"): {1}}},
        ]
        for variante in variantes:
            with self.subTest(variante=variante):
                with self.assertRaises(AutomataValidationError):
                    AutomataPila(**(self.datos() | variante))

    def test_construccion_completa(self):
        pda = construir_pda(G)
        self.assertEqual(pda.transiciones_pila[(0, EPSILON, "Z0")], {(1, ("S", "Z0"))})
        self.assertEqual(pda.transiciones_pila[(1, EPSILON, "S")], {(1, ("NP", "VP"))})
        self.assertEqual(pda.transiciones_pila[(1, EPSILON, "Z0")], {(2, ("Z0",))})
        for variable, reglas in G.producciones.items():
            self.assertEqual(pda.transiciones_pila[(1, EPSILON, variable)], {(1, r) for r in reglas})
        for terminal in G.terminales:
            self.assertEqual(pda.transiciones_pila[(1, terminal, terminal)], {(1, ())})
        self.assertEqual(len(pda.transiciones_pila), 2 + len(G.variables) + len(G.terminales))
        self.assertTrue(pda.poda_longitud_segura)

    def test_fondo_sin_colision(self):
        g = Gramatica({"Z0"}, {"a"}, {"Z0": (("a",),)}, "Z0")
        self.assertEqual(construir_pda(g).simbolo_inicial_pila, "Z0_")

    def test_certificado_sin_epsilon(self):
        g = Gramatica({"S", "A"}, {"a"}, {"S": (("A",),), "A": ((), ("a",))}, "S")
        self.assertFalse(construir_pda(g).poda_longitud_segura)
        unitaria = Gramatica({"S", "A"}, {"a"}, {"S": (("A",),), "A": (("a",),)}, "S")
        self.assertTrue(construir_pda(unitaria).poda_longitud_segura)

    def test_vendorizado_sin_cambios_logicos(self):
        origen = Path("C:/Universidad/TDC/primer-proyecto-tdc/src/automatas")
        if not origen.is_dir():
            self.skipTest("El repositorio original del proyecto 1 no está disponible")
        destino = Path(__file__).resolve().parents[1] / "recognizer" / "proyecto1"
        for nombre in ("models.py", "constants.py", "errors.py"):
            with self.subTest(archivo=nombre):
                copia = (destino / nombre).read_text(encoding="utf-8")
                cabecera = copia.splitlines()[:2]
                self.assertIn("commit 750243e", cabecera[0])
                self.assertIn("Adaptación", cabecera[1])
                sin_cabecera = "\n".join(copia.split("\n")[2:])
                original = (origen / nombre).read_text(encoding="utf-8")
                self.assertEqual(sin_cabecera, original.replace("from automatas.", "from ."))


if __name__ == "__main__":
    unittest.main()
