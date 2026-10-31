"""Contrato de consola, importación diferida y exportación; no implementa CYK."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import main
from recognizer.resultado import Resultado


class PruebasConsola(unittest.TestCase):
    def ejecutar(self, argumentos):
        salida = StringIO()
        with redirect_stdout(salida):
            codigo = main.main(argumentos)
        return codigo, salida.getvalue()

    def test_pda_y_traza(self):
        codigo, salida = self.ejecutar(["he cooks", "--metodo", "pda", "--traza"])
        self.assertEqual(codigo, 0)
        self.assertIn("aceptada", salida)
        self.assertIn("⊢", salida)
        self.assertIn("(q2, ε, Z0)", salida)

    def test_rechazo_e_inconclusion(self):
        self.assertEqual(self.ejecutar(["he eats cake", "--metodo", "pda"])[0], 1)
        self.assertEqual(self.ejecutar(["he cooks", "--metodo", "pda", "--limite", "1"])[0], 2)
        self.assertEqual(self.ejecutar(["", "--metodo", "pda"])[0], 1)

    def test_cyk_ausente_y_ambos_por_defecto(self):
        error = ModuleNotFoundError("Ausente", name="recognizer.cyk")
        with patch.object(main.importlib, "import_module", side_effect=error):
            codigo, salida = self.ejecutar(["he cooks"])
            self.assertEqual(codigo, 0)
            self.assertIn("CYK no disponible todavía (tarea C2 de Carlos)", salida)
            self.assertEqual(self.ejecutar(["he cooks", "--metodo", "cyk"])[0], 2)

    def test_contrato_cyk_disponible(self):
        def reconocer(tokens):
            return Resultado("cyk", "aceptada", tokens, len(tokens), {"reglas": 1},
                             {"tabla": [{"inicio": 0, "longitud": 2, "variables": ["S"]}]}, "Prueba")
        with patch.object(main.importlib, "import_module", return_value=SimpleNamespace(recognize=reconocer)):
            codigo, salida = self.ejecutar(["he cooks", "--metodo", "ambos", "--traza"])
        self.assertEqual(codigo, 0)
        self.assertIn("Tabla CYK", salida)
        self.assertIn('"S"', salida)

    def test_no_ocultar_dependencia_rota_cyk(self):
        error = ModuleNotFoundError("Dependencia rota", name="otra_dependencia")
        with patch.object(main.importlib, "import_module", side_effect=error):
            with self.assertRaises(ModuleNotFoundError):
                self.ejecutar(["he cooks", "--metodo", "cyk"])

    def test_json_crea_carpeta_y_guarda_evidencia_completa(self):
        with TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "nueva" / "salida.json"
            self.assertEqual(self.ejecutar(["he cooks", "--metodo", "pda", "--json", str(ruta)])[0], 0)
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            self.assertIsInstance(datos, list)
            self.assertEqual(datos[0]["estado"], "aceptada")
            self.assertEqual(len(datos[0]["evidencia"]["recorrido_aceptante"]), 7)

    def test_error_exportacion(self):
        with TemporaryDirectory() as carpeta:
            with redirect_stderr(StringIO()):
                codigo, _ = self.ejecutar(["he cooks", "--metodo", "pda", "--json", carpeta])
            self.assertEqual(codigo, 2)

    def test_argumentos_invalidos(self):
        for argumentos in (["he cooks", "--limite", "0"], ["he cooks", "--limite", "-1"],
                           ["he cooks", "--limite", "x"], ["he cooks", "--metodo", "otro"], []):
            with redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    self.ejecutar(argumentos)
            self.assertEqual(error.exception.code, 2)

    def test_subprocess_stdout_utf8(self):
        raiz = Path(__file__).resolve().parents[1]
        proceso = subprocess.run(
            [sys.executable, str(raiz / "main.py"), "he cooks", "--metodo", "pda", "--traza"],
            cwd=raiz, capture_output=True, encoding="utf-8", check=False,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("⊢", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
