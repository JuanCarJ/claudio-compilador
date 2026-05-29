import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from ai_suggestions import generar_sugerencias_ia_semantico
from lexer import Lexer
from main import app
from parser_rd import ParserDescendenteRecursivo
from semantico import AnalizadorSemantico


def analizar(codigo: str):
    lexer = Lexer(codigo)
    tokens = lexer.analizar()
    parser = ParserDescendenteRecursivo(tokens)
    arbol, aceptado = parser.analizar_con_recuperacion()
    errores, tabla = AnalizadorSemantico().analizar(arbol)
    return aceptado, parser.obtener_errores_sintacticos(), errores, tabla


class Quiz4SemanticoTests(unittest.TestCase):
    def test_detecta_las_siete_reglas_semanticas(self):
        codigo = """
var entero x = "hola"
var entero x = 2
x = "texto"
sea entero c = 1
c = 2
imprimir(fantasma)
si x entonces
    imprimir(x)
fin_si
para i desde "a" hasta 10 paso falso hacer
    imprimir(i)
fin_para
""".strip()

        aceptado, sintacticos, errores, tabla = analizar(codigo)

        self.assertTrue(aceptado)
        self.assertEqual([], sintacticos)
        reglas = [e.regla for e in errores]
        for regla in ["SEM-1", "SEM-2", "SEM-3", "SEM-4", "SEM-5", "SEM-6", "SEM-7"]:
            self.assertIn(regla, reglas)
        self.assertGreaterEqual(len(errores), 7)
        self.assertTrue(all(e.fila > 0 and e.columna > 0 and e.lexema for e in errores))
        simbolos = tabla.como_lista()
        self.assertTrue(any(s["nombre"] == "x" and s["tipo"] == "entero" for s in simbolos))
        self.assertTrue(any(s["nombre"] == "c" and s["inmutable"] for s in simbolos))

    def test_programa_semanticamente_valido(self):
        codigo = """
funcion entero suma(entero a, entero b) hacer
    var entero resultado = a + b
    retornar resultado
fin_funcion

var entero total = 10
total = 20
si total > 0 entonces
    imprimir(total)
fin_si
""".strip()

        aceptado, sintacticos, errores, tabla = analizar(codigo)

        self.assertTrue(aceptado)
        self.assertEqual([], sintacticos)
        self.assertEqual([], errores)
        nombres = {s["nombre"] for s in tabla.como_lista()}
        self.assertTrue({"suma", "a", "b", "resultado", "total"}.issubset(nombres))

    def test_endpoint_semantico_reporta_tabla_y_errores(self):
        client = TestClient(app)
        res = client.post("/api/semantico", json={"codigo": 'var entero x = "hola"\n'})

        self.assertEqual(200, res.status_code)
        data = res.json()
        self.assertFalse(data["valido"])
        self.assertEqual(1, data["total_errores_semanticos"])
        self.assertEqual("SEM-4", data["errores_semanticos"][0]["regla"])
        self.assertEqual("x", data["tabla_simbolos"][0]["nombre"])

    def test_ia_semantica_sigue_siendo_openai_y_tiene_fallback_sin_key(self):
        diag = [{"indice": 1, "regla": "SEM-4", "mensaje": "Tipo incompatible"}]
        clean_env = {
            key: value
            for key, value in os.environ.items()
            if key != "OPENAI_API_KEY"
        }
        with patch.dict(os.environ, clean_env, clear=True):
            estado, sugerencias = generar_sugerencias_ia_semantico("var entero x = \"hola\"", diag)

        self.assertEqual("no_disponible", estado)
        self.assertEqual("no_disponible", sugerencias[0]["estado_ia"])
        self.assertIn("OPENAI_API_KEY", sugerencias[0]["explicacion_usuario"])


if __name__ == "__main__":
    unittest.main()
