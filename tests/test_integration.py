"""Validación cruzada PDA–CYK sobre las mismas entradas; cada método decide por separado."""

from itertools import product
import random
import unittest

from recognizer import cyk, pda
from recognizer.grammar import G, tokenizar

ALFABETO_REDUCIDO = ("he", "cooks", "eats", "with", "the", "cat")
LONGITUD_MAXIMA = 5


def frase_aleatoria(generador: random.Random, profundidad: int = 0) -> list[str]:
    """Deriva desde S eligiendo producciones al azar; VP → VP PP se limita para terminar."""
    def expandir(simbolo, nivel):
        if simbolo in G.terminales:
            return [simbolo]
        alternativas = G.producciones[simbolo]
        if simbolo == "VP" and nivel >= 3:
            alternativas = tuple(a for a in alternativas if a[0] != "VP")
        return [t for s in generador.choice(alternativas) for t in expandir(s, nivel + 1)]
    return expandir(G.inicial, profundidad)


class PruebasIntegracion(unittest.TestCase):
    def assert_coinciden(self, tokens):
        r_pda, r_cyk = pda.recognize(tokens), cyk.recognize(tokens)
        self.assertNotEqual(r_pda.estado, "inconclusa", tokens)
        self.assertEqual(r_pda.estado, r_cyk.estado, tokens)
        self.assertEqual((r_pda.tokens, r_pda.n), (r_cyk.tokens, r_cyk.n))
        return r_pda.estado

    def test_casos_minimos_readme(self):
        esperados = {
            "he cooks": "aceptada", "she drinks a beer": "aceptada",
            "the cat eats the meat with a fork in the oven": "aceptada", "a dog cuts she": "aceptada",
            "": "rechazada", "he": "rechazada", "cooks he": "rechazada", "he eats cake": "rechazada",
            "he cooks with": "rechazada", "he dances": "rechazada", "He cooks": "rechazada",
            "he cooks.": "rechazada", "  he   cooks  ": "aceptada",
        }
        for frase, estado in esperados.items():
            with self.subTest(frase=frase):
                self.assertEqual(self.assert_coinciden(tokenizar(frase)), estado)

    def test_todas_las_cadenas_cortas_de_un_alfabeto_reducido(self):
        """Exhaustivo hasta la longitud indicada; no cubre longitudes mayores ni el alfabeto completo."""
        aceptadas = 0
        for longitud in range(LONGITUD_MAXIMA + 1):
            for tokens in product(ALFABETO_REDUCIDO, repeat=longitud):
                aceptadas += self.assert_coinciden(list(tokens)) == "aceptada"
        self.assertGreater(aceptadas, 10)

    def test_frases_generadas_y_perturbadas(self):
        """Frases de G con semilla fija; quitar o agregar una palabra suele producir rechazos."""
        generador = random.Random(2026)
        estados = set()
        for _ in range(60):
            tokens = frase_aleatoria(generador)
            self.assertEqual(self.assert_coinciden(tokens), "aceptada")
            posicion = generador.randrange(len(tokens))
            estados.add(self.assert_coinciden(tokens[:posicion] + tokens[posicion + 1:]))
            estados.add(self.assert_coinciden(tokens + [generador.choice(sorted(G.terminales))]))
        self.assertEqual(estados, {"aceptada", "rechazada"})

    def test_pda_inconcluso_no_es_desacuerdo(self):
        tokens = ["he", "cooks"]
        self.assertEqual(pda.recognize(tokens, limite_configuraciones=1).estado, "inconclusa")
        self.assertEqual(cyk.recognize(tokens).estado, "aceptada")


if __name__ == "__main__":
    unittest.main()
