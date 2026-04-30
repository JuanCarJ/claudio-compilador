"""
Sugerencias IA para diagnosticos sintacticos de Claudio.

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
