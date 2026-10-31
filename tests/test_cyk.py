"""Pruebas de CYK: tabla, conteos, testigos, árbol y derivación frente a G."""

import ast
import json
from pathlib import Path
import unittest

from recognizer.cyk import recognize
from recognizer.grammar import G, Gramatica, tokenizar


def anbn_cnf():
    """aⁿbⁿ, n ≥ 1, en CNF; gramática distinta de G para descartar reglas codificadas."""
    return Gramatica(
        variables=frozenset({"S", "T", "A", "B"}), terminales=frozenset({"a", "b"}),
        producciones={"S": (("A", "B"), ("A", "T")), "T": (("S", "B"),),
                      "A": (("a",),), "B": (("b",),)},
        inicial="S",
    )


def celdas(resultado):
    return {(c["inicio"], c["longitud"]): set(c["variables"]) for c in resultado.evidencia["tabla"]}


class PruebasCYK(unittest.TestCase):
    def assert_arbol_valido(self, resultado, gramatica=G):
        """Hojas = tokens en orden; cada nodo usa una producción de la gramática."""
        hojas = []

        def visitar(nodo):
            if "terminal" in nodo:
                self.assertEqual(set(nodo), {"terminal", "posicion"})
                self.assertEqual(nodo["posicion"], len(hojas))
                hojas.append(nodo["terminal"])
                return nodo["terminal"]
            produccion = tuple(nodo["produccion"])
            self.assertIn(produccion, gramatica.producciones[nodo["variable"]])
            self.assertEqual(tuple(visitar(hijo) for hijo in nodo["hijos"]), produccion)
            return nodo["variable"]

        self.assertEqual(visitar(resultado.evidencia["arbol"]), gramatica.inicial)
        self.assertEqual(hojas, resultado.tokens)

    def assert_derivacion_izquierda(self, resultado, gramatica=G):
        pasos = [paso.split() for paso in resultado.evidencia["derivacion"]]
        self.assertEqual(pasos[0], [gramatica.inicial])
        self.assertEqual(pasos[-1], resultado.tokens)
        for antes, despues in zip(pasos, pasos[1:]):
            i = next(k for k, s in enumerate(antes) if s in gramatica.variables)
            cuerpo = tuple(despues[i:len(despues) - (len(antes) - i - 1)])
            self.assertEqual(antes[:i], despues[:i])
            self.assertEqual(antes[i + 1:], despues[i + len(cuerpo):])
            self.assertIn(cuerpo, gramatica.producciones[antes[i]])
        self.assertEqual(len(pasos), 2 * resultado.n)  # n léxicas + (n-1) binarias + forma inicial

    def test_tabla_manual_he_cooks(self):
        resultado = recognize(["he", "cooks"])
        self.assertEqual(resultado.estado, "aceptada")
        self.assertEqual(resultado.evidencia["tabla"], [
            {"inicio": 0, "longitud": 1, "variables": ["NP"]},
            {"inicio": 1, "longitud": 1, "variables": ["V", "VP"]},
            {"inicio": 0, "longitud": 2, "variables": ["S"]},
        ])
        self.assertEqual(resultado.evidencia["testigos"], [
            {"inicio": 0, "longitud": 1, "variable": "NP", "produccion": ["he"], "corte": None},
            {"inicio": 1, "longitud": 1, "variable": "V", "produccion": ["cooks"], "corte": None},
            {"inicio": 1, "longitud": 1, "variable": "VP", "produccion": ["cooks"], "corte": None},
            {"inicio": 0, "longitud": 2, "variable": "S", "produccion": ["NP", "VP"], "corte": 1},
        ])
        self.assertEqual(resultado.evidencia["derivacion"], ["S", "NP VP", "he VP", "he cooks"])
        self.assertEqual(resultado.operaciones, {
            "celdas": 3, "consultas_lexicas": 50, "cortes": 1, "comprobaciones_binarias": 5,
            "reglas_satisfechas": 4, "variables_agregadas": 4,
        })

    def test_tabla_manual_she_drinks_a_beer(self):
        resultado = recognize(tokenizar("she drinks a beer"))
        self.assertEqual(celdas(resultado), {
            (0, 1): {"NP"}, (1, 1): {"V", "VP"}, (2, 1): {"Det"}, (3, 1): {"N"},
            (0, 2): {"S"}, (1, 2): set(), (2, 2): {"NP"},
            (0, 3): set(), (1, 3): {"VP"},
            (0, 4): {"S"},
        })
        testigos = {(t["inicio"], t["longitud"], t["variable"]): t for t in resultado.evidencia["testigos"]}
        self.assertEqual(testigos[(1, 3, "VP")]["produccion"], ["V", "NP"])
        self.assertEqual(testigos[(1, 3, "VP")]["corte"], 1)
        self.assertEqual(testigos[(0, 4, "S")]["corte"], 1)

    def test_casos_minimos_readme(self):
        aceptadas = ["he cooks", "she drinks a beer", "the cat eats the meat with a fork in the oven",
                     "a dog cuts she", " \the  cooks\n", "he cooks with she with he in a dog"]
        rechazadas = ["he", "cooks he", "he eats cake", "he cooks with", "he dances", "He cooks", "he cooks."]
        for frase in aceptadas:
            with self.subTest(frase=frase):
                resultado = recognize(tokenizar(frase))
                self.assertEqual(resultado.estado, "aceptada")
                self.assert_arbol_valido(resultado)
                self.assert_derivacion_izquierda(resultado)
        for frase in rechazadas:
            with self.subTest(frase=frase):
                resultado = recognize(tokenizar(frase))
                self.assertEqual(resultado.estado, "rechazada")
                self.assertNotIn("S", resultado.evidencia["celda_final"]["variables"])
                self.assertIsNone(resultado.evidencia["arbol"])
                self.assertEqual(resultado.evidencia["derivacion"], [])

    def test_conteos_cerrados_y_tabla_completa(self):
        """Los bucles recorren todas las reglas: el conteo depende solo de n."""
        frases = ["he", "cooks he", "he eats cake", "she eats the cake", "he dances x y z",
                  "she eats the cake with a fork", "a a a a a a a a"]
        for frase in frases:
            tokens = tokenizar(frase)
            n = len(tokens)
            with self.subTest(frase=frase):
                resultado = recognize(tokens)
                self.assertEqual(set(celdas(resultado)), {(i, l) for l in range(1, n + 1) for i in range(n - l + 1)})
                operaciones = resultado.operaciones
                self.assertEqual(operaciones["celdas"], n * (n + 1) // 2)
                self.assertEqual(operaciones["consultas_lexicas"], 25 * n)
                self.assertEqual(operaciones["cortes"], (n ** 3 - n) // 6)
                self.assertEqual(operaciones["comprobaciones_binarias"], 5 * (n ** 3 - n) // 6)
                self.assertEqual(operaciones["variables_agregadas"], len(resultado.evidencia["testigos"]))
                self.assertEqual(operaciones["variables_agregadas"],
                                 sum(len(c["variables"]) for c in resultado.evidencia["tabla"]))

    def test_entrada_vacia(self):
        for frase in ("", " \t\n"):
            resultado = recognize(tokenizar(frase))
            self.assertEqual(resultado.estado, "rechazada")
            self.assertEqual(resultado.n, 0)
            self.assertEqual(resultado.evidencia["tabla"], [])
            self.assertIsNone(resultado.evidencia["celda_final"])
            self.assertIsNone(resultado.evidencia["arbol"])
            self.assertTrue(all(valor == 0 for valor in resultado.operaciones.values()))
            self.assertIn("vacía", resultado.motivo)

    def test_palabras_desconocidas(self):
        resultado = recognize(tokenizar("he dances dances He"))
        self.assertEqual(resultado.estado, "rechazada")
        self.assertEqual(resultado.evidencia["palabras_desconocidas"], ["He", "dances"])
        self.assertEqual(celdas(resultado)[(1, 1)], set())
        self.assertIn("fuera del alfabeto", resultado.motivo)
        self.assertEqual(recognize(["he", "cooks"]).evidencia["palabras_desconocidas"], [])

    def test_testigos_son_coherentes_con_la_tabla(self):
        resultado = recognize(tokenizar("the cat eats the meat with a fork in the oven"))
        tabla = celdas(resultado)
        tokens = resultado.tokens
        for t in resultado.evidencia["testigos"]:
            with self.subTest(testigo=t):
                produccion = tuple(t["produccion"])
                self.assertIn(produccion, G.producciones[t["variable"]])
                self.assertIn(t["variable"], tabla[(t["inicio"], t["longitud"])])
                if t["corte"] is None:
                    self.assertEqual(t["longitud"], 1)
                    self.assertEqual(produccion, (tokens[t["inicio"]],))
                else:
                    self.assertTrue(0 < t["corte"] < t["longitud"])
                    self.assertIn(produccion[0], tabla[(t["inicio"], t["corte"])])
                    self.assertIn(produccion[1], tabla[(t["inicio"] + t["corte"], t["longitud"] - t["corte"])])

    def test_varios_pp_y_longitudes(self):
        for k in range(6):
            frase = "she eats the cake" + " with a fork" * k
            with self.subTest(k=k):
                aceptada = recognize(tokenizar(frase))
                self.assertEqual(aceptada.estado, "aceptada")
                self.assert_arbol_valido(aceptada)
                self.assert_derivacion_izquierda(aceptada)
                self.assertEqual(recognize(tokenizar(frase + " with")).estado, "rechazada")

    def test_gramatica_externa(self):
        gramatica = anbn_cnf()
        for k in range(1, 6):
            resultado = recognize(["a"] * k + ["b"] * k, gramatica=gramatica)
            self.assertEqual(resultado.estado, "aceptada")
            self.assert_arbol_valido(resultado, gramatica)
            self.assert_derivacion_izquierda(resultado, gramatica)
        for tokens in (["a"], ["b", "a"], ["a", "a", "b"], ["a", "b", "a", "b"]):
            self.assertEqual(recognize(tokens, gramatica=gramatica).estado, "rechazada")
        self.assertEqual(recognize(["a", "b"], gramatica=gramatica).operaciones["comprobaciones_binarias"], 3)

    def test_rechaza_gramatica_fuera_de_cnf(self):
        unitaria = Gramatica(frozenset({"S", "A"}), frozenset({"a"}),
                             {"S": (("A",),), "A": (("a",),)}, "S")
        vacia = Gramatica(frozenset({"S"}), frozenset({"a"}), {"S": ((), ("a",))}, "S")
        for gramatica in (unitaria, vacia):
            with self.assertRaises(ValueError):
                recognize(["a"], gramatica=gramatica)

    def test_evidencia_serializable_e_independiente(self):
        tokens = ["he", "cooks"]
        resultado = recognize(tokens)
        tokens.append("x")
        self.assertEqual(resultado.tokens, ["he", "cooks"])
        datos = json.loads(json.dumps(resultado.to_dict(), ensure_ascii=False))
        self.assertEqual(datos["metodo"], "cyk")
        self.assertEqual(datos["evidencia"]["arbol"]["variable"], "S")

    def test_no_depende_del_pda(self):
        fuente = (Path(__file__).resolve().parents[1] / "recognizer" / "cyk.py").read_text(encoding="utf-8")
        modulos = set()
        for nodo in ast.walk(ast.parse(fuente)):
            if isinstance(nodo, ast.ImportFrom):
                modulos.add(nodo.module)
            elif isinstance(nodo, ast.Import):
                modulos.update(alias.name for alias in nodo.names)
        self.assertFalse({m for m in modulos if m and ("pda" in m or "automata" in m)})


if __name__ == "__main__":
    unittest.main()
