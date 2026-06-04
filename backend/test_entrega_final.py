import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from traductor import traducir_claudio_a_swift


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "final"


def read_case(name: str) -> str:
    return (CASES / name).read_text(encoding="utf-8")


class EntregaFinalTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.clean_env = {
            key: value
            for key, value in os.environ.items()
            if key != "OPENAI_API_KEY"
        }

    def post_final(self, filename: str):
        with patch.dict(os.environ, self.clean_env, clear=True):
            return self.client.post("/api/compilar", json={"codigo": read_case(filename)})

    def test_caso_valido_genera_swift_y_mapeo(self):
        res = self.post_final("caso_valido.claudio")

        self.assertEqual(200, res.status_code)
        data = res.json()
        self.assertTrue(data["valido"])
        self.assertEqual(0, data["total_errores"])
        self.assertIn("func doble", data["swift"])
        self.assertIn("for i in stride", data["swift"])
        self.assertGreater(len(data["mapeo"]), 0)
        self.assertGreater(len(data["tabla_simbolos"]), 0)
        self.assertEqual("no_disponible", data["validacion_ia"]["estado_ia"])

    def test_operadores_logicos_no_se_traducen_dentro_de_cadenas(self):
        swift = traducir_claudio_a_swift(
            'imprimir("x es menor o igual y no cambia")\n'
            'var booleano ok = verdadero y no falso o falso'
        )

        self.assertIn('print("x es menor o igual y no cambia")', swift)
        self.assertIn("var ok: Bool = true && !false || false", swift)

    def test_error_semantico_bloquea_swift(self):
        res = self.post_final("caso_semantico.claudio")

        self.assertEqual(200, res.status_code)
        data = res.json()
        self.assertFalse(data["valido"])
        self.assertEqual("", data["swift"])
        self.assertEqual([], data["mapeo"])
        fases = {error["fase"] for error in data["errores"]}
        reglas = {error["regla"] for error in data["errores"] if error["regla"]}
        self.assertEqual({"semantico"}, fases)
        self.assertTrue({"SEM-3", "SEM-4", "SEM-6"}.issubset(reglas))

    def test_error_lexico_o_sintactico_bloquea_semantica_y_swift(self):
        res = self.post_final("caso_lexico_sintactico.claudio")

        self.assertEqual(200, res.status_code)
        data = res.json()
        self.assertFalse(data["valido"])
        self.assertEqual("", data["swift"])
        self.assertEqual([], data["mapeo"])
        self.assertEqual([], data["tabla_simbolos"])
        self.assertEqual(0, data["semantico"]["total_errores_semanticos"])
        fases = {error["fase"] for error in data["errores"]}
        self.assertIn("lexico", fases)
        self.assertIn("sintactico", fases)


if __name__ == "__main__":
    unittest.main()
