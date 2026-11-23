"""Utilidades compartidas de modelos LLM con reintentos y respaldo (fallback) ante alta demanda (503/429)."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Callable

from langchain_google_genai import ChatGoogleGenerativeAI

MODELOS_RESPALDO_DEFECTO = (
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
)


def obtener_lista_modelos(modelo_principal: str | None = None) -> list[str]:
    """Devuelve la lista ordenada de modelos a probar (principal + respaldos sin duplicados)."""
    principal = (modelo_principal or os.getenv("MODELO") or "gemini-2.5-flash").strip()
    configurados = os.getenv("MODELOS_RESPALDO", "")
    if configurados.strip():
        extras = [m.strip() for m in configurados.split(",") if m.strip()]
    else:
        extras = list(MODELOS_RESPALDO_DEFECTO)

    lista: list[str] = []
    for candidato in [principal, *extras]:
        if candidato and candidato not in lista:
            lista.append(candidato)
    return lista


def crear_modelo_chat(
    nombre_modelo: str,
    clave_api: str,
    timeout: int = 60,
    max_retries: int = 2,
) -> ChatGoogleGenerativeAI:
    """Crea una instancia de ChatGoogleGenerativeAI con timeout explícito y reintentos."""
    return ChatGoogleGenerativeAI(
        model=nombre_modelo,
        google_api_key=clave_api,
        timeout=timeout,
        max_retries=max_retries,
    )


def es_error_saturacion_o_temporal(error: Exception) -> bool:
    """Detecta si el error proviene de alta demanda (503), cuota/rate-limit (429) o caída temporal."""
    texto = str(error).upper()
    indicadores = (
        "503",
        "UNAVAILABLE",
        "HIGH DEMAND",
        "429",
        "RESOURCE_EXHAUSTED",
        "RATE LIMIT",
        "OVERLOADED",
        "DEADLINE_EXCEEDED",
        "500",
        "502",
        "504",
        "NOT_FOUND",
        "404",
    )
    return any(ind in texto for ind in indicadores)


async def ejecutar_con_respaldo(
    modelos: list[str],
    funcion_por_modelo: Callable[[str], Any],
    etiqueta: str = "LLM",
) -> Any:
    """Ejecuta una corrutina probando el modelo principal y, si hay saturación (503/429), rota a los de respaldo."""
    ultimo_error: Exception | None = None
    for indice, nombre_modelo in enumerate(modelos):
        try:
            resultado = funcion_por_modelo(nombre_modelo)
            if asyncio.iscoroutine(resultado):
                return await resultado
            return resultado
        except Exception as error:  # noqa: BLE001
            ultimo_error = error
            es_recuperable = es_error_saturacion_o_temporal(error)
            tiene_siguiente = indice + 1 < len(modelos)
            detalle = str(error).replace(chr(10), " ").strip()[:140]
            if es_recuperable and tiene_siguiente:
                siguiente = modelos[indice + 1]
                print(
                    f"[{etiqueta}] Modelo '{nombre_modelo}' saturado o no disponible ({detalle}). "
                    f"Cambiando automáticamente a modelo de respaldo '{siguiente}'..."
                )
                await asyncio.sleep(1.0)
                continue
            raise
    if ultimo_error is not None:
        raise ultimo_error
    raise RuntimeError(f"[{etiqueta}] No se configuraron modelos para ejecutar la consulta.")
