"""Grafo del agente pastelero (LangGraph)."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from src.comun.llm import (
    crear_modelo_chat,
    ejecutar_con_respaldo,
    obtener_lista_modelos,
)

from .prompts import SYSTEM_PROMPT
from .tools import catalogo_postres, escalar_receta, sustituto_ingrediente

load_dotenv(override=True)

MODELO = os.getenv("MODELO", "gemini-2.5-flash")
CLAVE_API = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or "pendiente-de-configurar"
)

_MEMORIA = MemorySaver()
_HERRAMIENTAS = [catalogo_postres, sustituto_ingrediente, escalar_receta]
_GRAFOS: dict[str, object] = {}


def _obtener_grafo(nombre_modelo: str):
    """Obtiene o construye el grafo del agente para un modelo dado, compartiendo la memoria."""
    if nombre_modelo not in _GRAFOS:
        llm = crear_modelo_chat(
            nombre_modelo=nombre_modelo,
            clave_api=CLAVE_API,
            timeout=60,
            max_retries=2,
        )
        _GRAFOS[nombre_modelo] = create_agent(
            model=llm,
            tools=_HERRAMIENTAS,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=_MEMORIA,
        )
    return _GRAFOS[nombre_modelo]


modelo = crear_modelo_chat(
    nombre_modelo=MODELO,
    clave_api=CLAVE_API,
    timeout=60,
    max_retries=2,
)
graph = _obtener_grafo(MODELO)


async def responder(texto: str, context_id: str) -> str:
    """Manda el texto al grafo y devuelve la última respuesta del agente (con respaldo ante error 503/429)."""
    config = {"configurable": {"thread_id": context_id}}
    modelos_disponibles = obtener_lista_modelos(MODELO)

    async def _invocar(nombre_modelo: str):
        grafo_actual = _obtener_grafo(nombre_modelo)
        return await grafo_actual.ainvoke(
            {"messages": [("user", texto)]}, config=config
        )

    resultado = await ejecutar_con_respaldo(
        modelos=modelos_disponibles,
        funcion_por_modelo=_invocar,
        etiqueta="Agente pastelero",
    )
    mensajes = resultado.get("messages", [])
    for mensaje in reversed(mensajes):
        if getattr(mensaje, "type", None) == "ai" and mensaje.content:
            contenido = mensaje.content
            if isinstance(contenido, str):
                return contenido
            if isinstance(contenido, list):
                partes = []
                for item in contenido:
                    if isinstance(item, str):
                        partes.append(item)
                    elif isinstance(item, dict) and "text" in item:
                        partes.append(item["text"])
                return "\n".join(partes).strip()
            return str(contenido)
    return ""


def saltos(texto: str) -> str:
    """Ejecuta el grafo mostrando nodos y herramientas por los que pasa."""
    config = {"configurable": {"thread_id": "saltos-cli"}}
    total = 0
    for paso in graph.stream(
        {"messages": [("user", texto)]}, config=config, stream_mode="updates"
    ):
        for nodo, actualizacion in paso.items():
            total += 1
            print(f"[{total}] Nodo: {nodo}")
            mensajes = []
            if isinstance(actualizacion, dict):
                mensajes = actualizacion.get("messages", []) or []
            for mensaje in mensajes:
                for llamada in getattr(mensaje, "tool_calls", None) or []:
                    nombre = llamada.get("name", "?")
                    argumentos = llamada.get("args", {})
                    print(f"     -> herramienta: {nombre}({argumentos})")
    return f"Total de saltos: {total}"


def diagrama() -> str:
    """Devuelve la estructura del grafo en Mermaid."""
    return graph.get_graph().draw_mermaid()
