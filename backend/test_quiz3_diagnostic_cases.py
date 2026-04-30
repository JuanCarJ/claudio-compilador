import unittest
from dataclasses import dataclass
from typing import Callable

from main import CodigoRequest, analizar_ll1, analizar_recursivo


@dataclass(frozen=True)
class DiagnosticCase:
    nombre: str
    parser: str
    codigo: str
    debe_contener: str
    errores_sintacticos: int | None = None


PARSERS: dict[str, Callable[[CodigoRequest], object]] = {
    "rd": analizar_recursivo,
    "ll1": analizar_ll1,
}


CASOS_DIAGNOSTICO = [
    DiagnosticCase("rd_asignacion_sin_valor_antes_de_var", "rd", "var entero x =\nvar entero total = 1", "falta el valor", 1),
    DiagnosticCase("ll1_asignacion_sin_valor_antes_de_var", "ll1", "var entero x =\nvar entero total = 1", "falta una expresion", 1),
    DiagnosticCase("rd_asignacion_id_sin_valor", "rd", "x =\nimprimir(x)", "falta el valor", 1),
    DiagnosticCase("rd_sea_sin_valor", "rd", "sea real pi =\nimprimir(pi)", "falta el valor", 1),
    DiagnosticCase("rd_cadena_sin_valor", "rd", "var cadena nombre =\nimprimir(nombre)", "falta el valor", 1),
    DiagnosticCase("rd_booleano_sin_valor", "rd", "var booleano ok =\nimprimir(ok)", "falta el valor", 1),
    DiagnosticCase("rd_suma_sin_operando", "rd", "var entero x = 1 +\nvar entero total = 2", "falta un operando", 1),
    DiagnosticCase("rd_resta_sin_operando", "rd", "var entero x = 1 -\nimprimir(x)", "falta un operando", 1),
    DiagnosticCase("rd_multiplicacion_sin_operando", "rd", "var entero x = 2 *\nimprimir(x)", "falta un operando", 1),
    DiagnosticCase("rd_division_sin_operando", "rd", "var entero x = 2 /\nimprimir(x)", "falta un operando", 1),
    DiagnosticCase("rd_modulo_sin_operando", "rd", "var entero x = 2 %\nimprimir(x)", "falta un operando", 1),
    DiagnosticCase("rd_potencia_sin_operando", "rd", "var entero x = 2 **\nimprimir(x)", "falta un operando", 1),
    DiagnosticCase("rd_y_sin_operando", "rd", "var booleano ok = verdadero y\nimprimir(ok)", "falta un operando", 1),
    DiagnosticCase("rd_o_sin_operando", "rd", "var booleano ok = falso o\nimprimir(ok)", "falta un operando", 1),
    DiagnosticCase("rd_no_sin_operando", "rd", "var booleano ok = no\nimprimir(ok)", "operando", 1),
    DiagnosticCase("rd_menos_unario_sin_operando", "rd", "var entero x = -\nimprimir(x)", "operando", 1),
    DiagnosticCase("rd_si_mayor_sin_operando", "rd", "var entero x = 1\nsi x > entonces\n imprimir(x)\nfin_si", "si x > 5 entonces", 1),
    DiagnosticCase("ll1_si_mayor_sin_operando", "ll1", "var entero x = 1\nsi x > entonces\n imprimir(x)\nfin_si", "si x > 5 entonces", 1),
    DiagnosticCase("rd_si_igual_sin_operando", "rd", "var entero x = 1\nsi x == entonces\n imprimir(x)\nfin_si", "falta un operando", 1),
    DiagnosticCase("rd_si_menor_igual_sin_operando", "rd", "var entero x = 1\nsi x <= entonces\n imprimir(x)\nfin_si", "falta un operando", 1),
    DiagnosticCase("rd_mientras_relacional_sin_operando", "rd", "var entero x = 1\nmientras x < hacer\n imprimir(x)\nfin_mientras", "falta un operando", 1),
    DiagnosticCase("rd_para_desde_sin_expresion", "rd", "para i desde hasta 10 hacer\n imprimir(i)\nfin_para", "falta un operando", 1),
    DiagnosticCase("rd_para_hasta_sin_expresion", "rd", "para i desde 1 hasta paso 1 hacer\n imprimir(i)\nfin_para", "falta un operando", 1),
    DiagnosticCase("rd_para_paso_sin_expresion", "rd", "para i desde 1 hasta 10 paso hacer\n imprimir(i)\nfin_para", "falta un operando", 1),
    DiagnosticCase("rd_falta_entonces", "rd", "si verdadero\n imprimir(\"x\")\nfin_si", "entonces", 1),
    DiagnosticCase("ll1_falta_entonces", "ll1", "si verdadero\n imprimir(\"x\")\nfin_si", "entonces", 1),
    DiagnosticCase("rd_falta_hacer_mientras", "rd", "mientras verdadero\n imprimir(\"x\")\nfin_mientras", "hacer", 1),
    DiagnosticCase("ll1_falta_hacer_mientras", "ll1", "mientras verdadero\n imprimir(\"x\")\nfin_mientras", "hacer", 1),
    DiagnosticCase("rd_falta_hacer_para", "rd", "para i desde 1 hasta 3 paso 1\n imprimir(i)\nfin_para", "hacer", 1),
    DiagnosticCase("ll1_falta_hacer_para", "ll1", "para i desde 1 hasta 3 paso 1\n imprimir(i)\nfin_para", "hacer", 1),
    DiagnosticCase("rd_falta_hacer_funcion", "rd", "funcion entero f()\n retornar 1\nfin_funcion", "hacer", 1),
    DiagnosticCase("rd_parentesis_imprimir", "rd", "imprimir(\"Hola\"\nvar entero total = 1", "parentesis", 1),
    DiagnosticCase("ll1_parentesis_imprimir", "ll1", "imprimir(\"Hola\"\nvar entero total = 1", "parentesis", 1),
    DiagnosticCase("rd_parentesis_expresion", "rd", "var entero x = (1 + 2\nimprimir(x)", "parentesis", 1),
    DiagnosticCase("rd_parentesis_llamada", "rd", "foo(1, 2\nvar entero total = 1", "parentesis", 1),
    DiagnosticCase("rd_variable_sin_tipo", "rd", "var = 1", "tipo", 1),
    DiagnosticCase("rd_variable_sin_identificador", "rd", "var entero = 1", "identificador", 1),
    DiagnosticCase("ll1_variable_sin_identificador", "ll1", "var entero = 1", "identificador", 1),
    DiagnosticCase("rd_parametro_sin_identificador", "rd", "funcion entero f(entero) hacer\n retornar 1\nfin_funcion", "identificador", 1),
    DiagnosticCase("rd_importar_sin_identificador", "rd", "importar", "identificador", 1),
    DiagnosticCase("rd_importar_numero", "rd", "importar 123", "identificador", 1),
    DiagnosticCase("rd_clase_sin_identificador", "rd", "clase hacer\nfin_clase", "identificador", 1),
    DiagnosticCase("rd_atributo_sin_identificador", "rd", "clase A hacer\n atributo cadena\nfin_clase", "identificador", 1),
    DiagnosticCase("rd_metodo_sin_identificador", "rd", "clase A hacer\n metodo () hacer\n fin_funcion\nfin_clase", "identificador", None),
    DiagnosticCase("rd_falta_fin_si", "rd", "si verdadero entonces\n imprimir(\"x\")", "fin_si", 1),
    DiagnosticCase("ll1_falta_fin_si", "ll1", "si verdadero entonces\n imprimir(\"x\")", "fin_si", 1),
    DiagnosticCase("rd_falta_fin_para", "rd", "para i desde 1 hasta 3 hacer\n imprimir(i)", "fin_para", 1),
    DiagnosticCase("ll1_falta_fin_para", "ll1", "para i desde 1 hasta 3 hacer\n imprimir(i)", "fin_para", 1),
    DiagnosticCase("rd_falta_fin_mientras", "rd", "mientras verdadero hacer\n imprimir(\"x\")", "fin_mientras", 1),
    DiagnosticCase("ll1_falta_fin_mientras", "ll1", "mientras verdadero hacer\n imprimir(\"x\")", "fin_mientras", 1),
    DiagnosticCase("rd_falta_fin_funcion", "rd", "funcion entero f() hacer\n retornar 1", "fin_funcion", 1),
    DiagnosticCase("rd_falta_fin_clase", "rd", "clase A hacer\n atributo entero x", "fin_clase", 1),
    DiagnosticCase("lex_cadena_sin_cerrar", "ll1", "var cadena nombre = \"Mundo", "comilla doble", None),
    DiagnosticCase("lex_comentario_sin_cerrar", "ll1", "/* comentario abierto", "comentario de bloque", None),
    DiagnosticCase("lex_caracter_no_reconocido", "ll1", "var entero x = 1 @", "token valido", None),
    DiagnosticCase("rd_nuevo_sin_identificador", "rd", "var Persona p = nuevo ()", "identificador", 1),
    DiagnosticCase("rd_miembro_sin_identificador", "rd", "obj. = 1", "identificador", 1),
    DiagnosticCase("rd_falta_asignacion_variable", "rd", "var entero total 1", "asignacion", 1),
    DiagnosticCase("ll1_falta_asignacion_variable", "ll1", "var entero total 1", "asignacion", 1),
]


class Quiz3DiagnosticCasesTest(unittest.TestCase):
    def test_hay_al_menos_50_casos(self):
        self.assertGreaterEqual(len(CASOS_DIAGNOSTICO), 50)

    def test_casos_invalidos_tienen_mensajes_contextuales(self):
        for caso in CASOS_DIAGNOSTICO:
            with self.subTest(caso=caso.nombre, parser=caso.parser):
                res = PARSERS[caso.parser](CodigoRequest(codigo=caso.codigo))
                total = res.lexico.total_errores + res.total_errores_sintacticos

                self.assertFalse(res.valido)
                self.assertGreater(total, 0)
                if caso.errores_sintacticos is not None:
                    self.assertEqual(res.total_errores_sintacticos, caso.errores_sintacticos)

                texto = self._texto_diagnostico(res)
                self.assertIn(caso.debe_contener.lower(), texto)

                for error in res.lexico.errores:
                    self.assertGreaterEqual(error.fila, 1)
                    self.assertGreaterEqual(error.columna, 1)
                    self.assertGreater(len(error.mensaje), 20)
                    self.assertGreater(len(error.sugerencia_deterministica), 20)

                for diag in res.errores_sintacticos:
                    self.assertGreaterEqual(diag.fila, 1)
                    self.assertGreaterEqual(diag.columna, 1)
                    self.assertTrue(diag.lexema_encontrado)
                    self.assertTrue(diag.tipo_encontrado)
                    self.assertTrue(diag.esperados)
                    self.assertIn("Siguiente esperado", diag.sugerencia_deterministica)
                    self.assertGreater(len(diag.sugerencia_deterministica), 45)
                    self.assertNotIn("Revisa este punto", diag.sugerencia_deterministica)

    def _texto_diagnostico(self, res) -> str:
        partes: list[str] = []
        for error in res.lexico.errores:
            partes.extend([
                error.mensaje,
                getattr(error, "esperado", ""),
                getattr(error, "simbolo_probable", ""),
                error.sugerencia_deterministica,
            ])
        for diag in res.errores_sintacticos:
            partes.extend([
                diag.lexema_encontrado,
                diag.tipo_encontrado,
                " ".join(diag.esperados),
                diag.contexto,
                diag.recuperacion,
                diag.sugerencia_deterministica,
            ])
        return " ".join(partes).lower()


if __name__ == "__main__":
    unittest.main()
