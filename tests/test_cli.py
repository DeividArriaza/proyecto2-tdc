"""Consola con el módulo CYK real: selección de método, trazas, exportación y códigos de salida."""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import main


class PruebasConsolaCYK(unittest.TestCase):
    def ejecutar(self, argumentos):
        salida = StringIO()
        with redirect_stdout(salida):
            codigo = main.main(argumentos)
        return codigo, salida.getvalue()

    def test_ambos_aceptan(self):
        codigo, salida = self.ejecutar(["he cooks"])
        self.assertEqual(codigo, 0)
        self.assertIn("PDA: aceptada", salida)
        self.assertIn("CYK: aceptada", salida)
        self.assertNotIn("no disponible", salida)

    def test_ambos_rechazan(self):
        for frase in ("he eats cake", "", "he dances", "He cooks"):
            with self.subTest(frase=frase):
                codigo, salida = self.ejecutar([frase])
                self.assertEqual(codigo, 1)
                self.assertIn("PDA: rechazada", salida)
                self.assertIn("CYK: rechazada", salida)

    def test_solo_cyk_con_traza(self):
        codigo, salida = self.ejecutar(["he cooks", "--metodo", "cyk", "--traza"])
        self.assertEqual(codigo, 0)
        self.assertNotIn("PDA", salida)
        self.assertIn("Tabla CYK", salida)
        self.assertIn('{"inicio": 0, "longitud": 2, "variables": ["S"]}', salida)
        self.assertEqual(self.ejecutar(["cooks he", "--metodo", "cyk"])[0], 1)

    def test_traza_de_ambos_metodos(self):
        codigo, salida = self.ejecutar(["he cooks", "--metodo", "ambos", "--traza"])
        self.assertEqual(codigo, 0)
        self.assertIn("(q2, ε, Z0)", salida)
        self.assertIn("Tabla CYK", salida)

    def test_limite_pda_produce_inconclusion_y_no_rechazo(self):
        codigo, salida = self.ejecutar(["he cooks", "--limite", "1"])
        self.assertEqual(codigo, 2)
        self.assertIn("PDA: inconclusa", salida)
        self.assertIn("CYK: aceptada", salida)

    def test_json_exporta_ambas_evidencias(self):
        with TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "salidas" / "ambos.json"
            self.assertEqual(self.ejecutar(["she drinks a beer", "--json", str(ruta)])[0], 0)
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertEqual([d["metodo"] for d in datos], ["pda", "cyk"])
        evidencia = datos[1]["evidencia"]
        self.assertEqual(len(evidencia["tabla"]), 10)
        self.assertEqual(evidencia["derivacion"][-1], "she drinks a beer")
        self.assertEqual(evidencia["arbol"]["produccion"], ["NP", "VP"])
        self.assertEqual(datos[1]["operaciones"]["cortes"], 10)

    def test_subprocess_ambos(self):
        raiz = Path(__file__).resolve().parents[1]
        proceso = subprocess.run(
            [sys.executable, str(raiz / "main.py"), "the cat eats the meat with a fork in the oven", "--traza"],
            cwd=raiz, capture_output=True, encoding="utf-8", check=False,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("CYK: aceptada", proceso.stdout)
        self.assertIn("⊢", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
