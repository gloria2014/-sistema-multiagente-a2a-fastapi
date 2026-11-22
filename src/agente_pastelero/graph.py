"""Grafo del agente pastelero (LangGraph)."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from .prompts import SYSTEM_PROMPT
from .tools import catalogo_postres, escalar_receta, sustituto_ingrediente

load_dotenv(override=True)

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
CLAVE_API = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or "pendiente-de-configurar"
)
modelo = ChatGoogleGenerativeAI(model=MODELO, google_api_key=CLAVE_API)

graph = create_agent(
    model=modelo,
    tools=[catalogo_postres, sustituto_ingrediente, escalar_receta],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


async def responder(texto: str, context_id: str) -> str:
    """Manda el texto al grafo y devuelve la última respuesta del agente."""
    config = {"configurable": {"thread_id": context_id}}
    resultado = await graph.ainvoke(
        {"messages": [("user", texto)]}, config=config
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
