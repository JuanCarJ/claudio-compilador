import os
import unittest

from lexer import Lexer
from parser_ll1 import ParserPredictivoLL1
from parser_rd import ParserDescendenteRecursivo
from programas import PROGRAMAS
from main import CodigoRequest, SugerenciasIARequest, analizar_ll1, analizar_recursivo, sugerencias_ia


class Quiz3DiagnosticsTest(unittest.TestCase):
    def test_programas_validos_siguen_pasando(self):
        validos = {
            nombre: codigo
            for nombre, codigo in PROGRAMAS.items()
            if not nombre.startswith("Quiz 3.")
        }
        self.assertEqual(len(validos), 15)

        for nombre, codigo in validos.items():
            with self.subTest(nombre=nombre):
                tokens = Lexer(codigo).analizar()

                rd = ParserDescendenteRecursivo(tokens)
                _, rd_ok = rd.analizar_con_recuperacion()
                self.assertTrue(rd_ok)
                self.assertEqual(rd.obtener_errores_sintacticos(), [])

                ll1 = ParserPredictivoLL1(tokens)
                _, _, ll1_ok = ll1.analizar()
                self.assertTrue(ll1_ok)
                self.assertEqual(ll1.obtener_errores_sintacticos(), [])

    def test_recursivo_reporta_errores_estructurados(self):
        codigo = PROGRAMAS["Quiz 3. Error: multiples fallos"]
        res = analizar_recursivo(CodigoRequest(codigo=codigo))

        self.assertFalse(res.valido)
        self.assertGreaterEqual(res.total_errores_sintacticos, 3)
        primero = res.errores_sintacticos[0]
        self.assertGreaterEqual(primero.fila, 1)
        self.assertTrue(primero.lexema_encontrado)
        self.assertTrue(primero.esperados)
        self.assertTrue(primero.sugerencia_deterministica)
        self.assertEqual(primero.estado_ia, "pendiente")

    def test_ll1_reporta_recuperacion_en_traza(self):
        codigo = PROGRAMAS["Quiz 3. Error: multiples fallos"]
        res = analizar_ll1(CodigoRequest(codigo=codigo))

        self.assertFalse(res.valido)
        self.assertGreaterEqual(res.total_errores_sintacticos, 3)
        self.assertTrue(any("ERROR" in paso.accion for paso in res.traza))
        self.assertTrue(any("RECUPERACION" in paso.accion for paso in res.traza))

    def test_cadena_sin_cerrar_no_genera_cascada_sintactica(self):
        codigo = '''var entero x = 10
var cadena nombre = "Mundo

si x > 5 entonces
    imprimir("Hola")
sino
    imprimir("x es menor o igual a 5")
fin_si

para i desde 1 hasta x paso 1 hacer
    imprimir(i)
fin_para
'''

        for analizar in (analizar_recursivo, analizar_ll1):
            with self.subTest(parser=analizar.__name__):
                res = analizar(CodigoRequest(codigo=codigo))
                self.assertFalse(res.valido)
                self.assertEqual(res.lexico.total_errores, 1)
                self.assertEqual(res.total_errores_sintacticos, 0)
                error = res.lexico.errores[0]
                self.assertIn("comilla doble de cierre", error.mensaje)
                self.assertIn("Comilla doble", error.esperado)
                self.assertEqual(error.simbolo_probable, '"')
                self.assertIn('`"`', error.sugerencia_deterministica)

    def test_sugerencias_ia_sin_api_key_no_rompe(self):
        previous = os.environ.pop("OPENAI_API_KEY", None)
        try:
            codigo = PROGRAMAS["Quiz 3. Error: falta entonces"]
            res = analizar_ll1(CodigoRequest(codigo=codigo))
            ia = sugerencias_ia(
                SugerenciasIARequest(
                    codigo=codigo,
                    diagnosticos=[d.model_dump() for d in res.errores_sintacticos],
                )
            )
            self.assertEqual(ia.estado, "no_disponible")
            self.assertEqual(len(ia.sugerencias), len(res.errores_sintacticos))
            self.assertTrue(all(s.estado_ia == "no_disponible" for s in ia.sugerencias))
        finally:
            if previous is not None:
                os.environ["OPENAI_API_KEY"] = previous


if __name__ == "__main__":
    unittest.main()
