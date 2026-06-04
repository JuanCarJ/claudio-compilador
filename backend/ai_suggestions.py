"""
Sugerencias IA para diagnosticos sintacticos y semanticos de Claudio.

La integracion esta aislada del analizador: si OpenAI no esta
configurado o falla, el compilador sigue reportando los errores
deterministicos.
"""

from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, Field

from diagnostics import diagnosticos_para_ia


class SugerenciaIA(BaseModel):
    indice: int
    explicacion_usuario: str
    correccion_sugerida: str
    mini_ejemplo: str
    confianza: float = Field(ge=0, le=1)


class RespuestaSugerenciasIA(BaseModel):
    sugerencias: list[SugerenciaIA]


class RespuestaSugerenciasIASemantica(BaseModel):
    sugerencias: list[SugerenciaIA]


class RespuestaValidacionSwiftIA(BaseModel):
    valido: bool
    resumen: str
    problemas: list[str] = []
    sugerencias: list[str] = []


def _sugerencias_estado(
    diagnosticos: list[dict[str, Any]],
    estado: str,
    mensaje: str,
) -> list[dict[str, Any]]:
    sugerencias = []
    for diag in diagnosticos:
        sugerencias.append({
            "indice": int(diag.get("indice") or 0),
            "explicacion_usuario": mensaje,
            "correccion_sugerida": "",
            "mini_ejemplo": "",
            "confianza": 0.0,
            "estado_ia": estado,
        })
    return sugerencias


def generar_sugerencias_ia(
    codigo: str,
    diagnosticos: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not diagnosticos:
        return "lista", []
    if not api_key:
        return "no_disponible", _sugerencias_estado(
            diagnosticos,
            "no_disponible",
            "Configura OPENAI_API_KEY en el backend para activar la sugerencia IA.",
        )

    try:
        from openai import OpenAI
    except Exception:
        return "error", _sugerencias_estado(
            diagnosticos,
            "error",
            "La dependencia openai no esta instalada en el backend.",
        )

    max_errors = int(os.getenv("OPENAI_MAX_ERRORS", "8"))
    timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "8"))
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    compactos = diagnosticos_para_ia(codigo, diagnosticos[:max_errors])

    system_prompt = (
        "Eres un asistente educativo para estudiantes de compiladores. "
        "Explica errores sintacticos del lenguaje Claudio con base en el "
        "diagnostico gramatical entregado. No contradigas los tokens esperados. "
        "Usa el contexto cercano para evitar sugerencias en cascada; si una linea "
        "anterior muestra una cadena o comentario sin cierre, menciona primero ese "
        "origen probable. "
        "Indica explicitamente cual es el siguiente token o fragmento que deberia "
        "aparecer segun la gramatica. Devuelve sugerencias breves, concretas, "
        "en espanol y orientadas a corregir codigo."
    )
    user_payload = {
        "lenguaje": "Claudio",
        "regla": "Cada sugerencia debe complementar, no reemplazar, la sugerencia deterministica.",
        "diagnosticos": compactos,
    }

    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            text_format=RespuestaSugerenciasIA,
        )
        parsed: RespuestaSugerenciasIA = response.output_parsed
        sugerencias = []
        for item in parsed.sugerencias:
            data = item.model_dump()
            data["estado_ia"] = "lista"
            sugerencias.append(data)

        # Si el modelo devolvio menos elementos, conservar fallback por indice faltante.
        presentes = {s["indice"] for s in sugerencias}
        for diag in compactos:
            indice = int(diag.get("indice") or 0)
            if indice not in presentes:
                sugerencias.append({
                    "indice": indice,
                    "explicacion_usuario": "No se genero una sugerencia IA para este error.",
                    "correccion_sugerida": "",
                    "mini_ejemplo": "",
                    "confianza": 0.0,
                    "estado_ia": "error",
                })
        return "lista", sugerencias
    except Exception as exc:
        return "error", _sugerencias_estado(
            compactos,
            "error",
            f"No fue posible generar la sugerencia IA: {exc}",
        )


def generar_sugerencias_ia_semantico(
    codigo: str,
    diagnosticos: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    """
    Bonus IA del Quiz 4, modalidad A.

    Los errores semanticos clasicos ya detectados por SEM-1..SEM-7 se envian
    a OpenAI para enriquecerlos con una explicacion y una propuesta concreta.
    La IA no reemplaza las reglas deterministicas.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not diagnosticos:
        return "lista", []
    if not api_key:
        return "no_disponible", _sugerencias_estado(
            diagnosticos,
            "no_disponible",
            "Configura OPENAI_API_KEY en el backend para activar sugerencias IA semanticas.",
        )

    try:
        from openai import OpenAI
    except Exception:
        return "error", _sugerencias_estado(
            diagnosticos,
            "error",
            "La dependencia openai no esta instalada en el backend.",
        )

    max_errors = int(os.getenv("OPENAI_MAX_ERRORS", "8"))
    timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "8"))
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    compactos = diagnosticos[:max_errors]

    system_prompt = (
        "Eres un asistente educativo para estudiantes de compiladores. "
        "Explica errores semanticos del lenguaje Claudio con base en el diagnostico "
        "entregado. Los errores posibles son: SEM-1 declaracion duplicada, "
        "SEM-2 identificador no declarado, SEM-3 reasignacion de constante, "
        "SEM-4 incompatibilidad de tipo en declaracion, SEM-5 incompatibilidad "
        "de tipo en asignacion, SEM-6 condicion no booleana y SEM-7 limites "
        "no numericos en un ciclo para. Devuelve sugerencias breves, concretas, "
        "en espanol y orientadas a corregir el codigo. No inventes reglas que "
        "contradigan el diagnostico deterministico."
    )
    user_payload = {
        "lenguaje": "Claudio",
        "regla": "Cada sugerencia complementa, no reemplaza, la sugerencia deterministica.",
        "codigo_fuente": codigo[:1200],
        "errores_semanticos": compactos,
    }

    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            text_format=RespuestaSugerenciasIASemantica,
        )
        parsed: RespuestaSugerenciasIASemantica = response.output_parsed
        sugerencias = []
        for item in parsed.sugerencias:
            data = item.model_dump()
            data["estado_ia"] = "lista"
            sugerencias.append(data)

        presentes = {s["indice"] for s in sugerencias}
        for diag in compactos:
            indice = int(diag.get("indice") or 0)
            if indice not in presentes:
                sugerencias.append({
                    "indice": indice,
                    "explicacion_usuario": "No se genero una sugerencia IA para este error semantico.",
                    "correccion_sugerida": "",
                    "mini_ejemplo": "",
                    "confianza": 0.0,
                    "estado_ia": "error",
                })
        return "lista", sugerencias
    except Exception as exc:
        return "error", _sugerencias_estado(
            compactos,
            "error",
            f"No fue posible generar la sugerencia IA semantica: {exc}",
        )


def generar_validacion_swift_ia(codigo_claudio: str, codigo_swift: str) -> dict[str, Any]:
    """
    Bonus IA de la entrega final.

    Valida el codigo Swift generado a partir de un programa Claudio ya aceptado
    por las fases lexica, sintactica y semantica. La respuesta es solo
    complementaria: si OpenAI no esta disponible, el compilador conserva la
    salida deterministica.
    """
    if not codigo_swift.strip():
        return {
            "estado_ia": "omitida",
            "valido": None,
            "resumen": "La validacion IA se omite porque no hay codigo Swift generado.",
            "problemas": [],
            "sugerencias": [],
        }

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "estado_ia": "no_disponible",
            "valido": None,
            "resumen": "Configura OPENAI_API_KEY en el backend para activar la validacion IA del Swift generado.",
            "problemas": [],
            "sugerencias": [],
        }

    try:
        from openai import OpenAI
    except Exception:
        return {
            "estado_ia": "error",
            "valido": None,
            "resumen": "La dependencia openai no esta instalada en el backend.",
            "problemas": [],
            "sugerencias": [],
        }

    timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "8"))
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    system_prompt = (
        "Eres un revisor de codigo Swift para una entrega de compiladores. "
        "Evalua si el codigo Swift generado es sintacticamente razonable, "
        "mantiene la intencion del programa Claudio y no contradice las fases "
        "deterministicas del compilador. No inventes errores del lenguaje fuente; "
        "solo revisa la salida destino. Responde breve y en espanol."
    )
    user_payload = {
        "lenguaje_fuente": "Claudio",
        "lenguaje_destino": "Swift",
        "codigo_claudio": codigo_claudio[:1800],
        "codigo_swift": codigo_swift[:2400],
        "criterios": [
            "La salida debe parecer Swift valido.",
            "Las estructuras si/mientras/para deben estar balanceadas con llaves.",
            "Los literales booleanos y operadores logicos deben estar en sintaxis Swift.",
            "No debe recomendar cambios al programa fuente si la traduccion ya es coherente.",
        ],
    }

    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            text_format=RespuestaValidacionSwiftIA,
        )
        parsed: RespuestaValidacionSwiftIA = response.output_parsed
        data = parsed.model_dump()
        data["estado_ia"] = "lista"
        return data
    except Exception as exc:
        return {
            "estado_ia": "error",
            "valido": None,
            "resumen": f"No fue posible validar el Swift con IA: {exc}",
            "problemas": [],
            "sugerencias": [],
        }
