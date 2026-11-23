"""Grafo del agente de música ochentera (LangGraph)."""

from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from src.comun.llm import (
    crear_modelo_chat,
    ejecutar_con_respaldo,
    obtener_lista_modelos,
)

from .prompts import SYSTEM_PROMPT
from .tools import (
    buscar_artista,
    buscar_canciones,
    listar_por_categoria,
    sugerir_cancion,
)

# Cargar .env desde la raíz del proyecto.
_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=_RAIZ_PROYECTO / ".env", override=True)

MODELO = os.getenv("MODELO", "gemini-2.5-flash")
CLAVE_API = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or "pendiente-de-configurar"
)

_MEMORIA = MemorySaver()
_HERRAMIENTAS = [
    buscar_canciones,
    buscar_artista,
    listar_por_categoria,
    sugerir_cancion,
]
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


def _rechazo_deterministico(texto: str) -> str | None:
    """Devuelve un mensaje de rechazo si el texto es claramente inaceptable.

    Cubre letras, enlaces/descargas, jailbreak y casos claros fuera de
    alcance. Devuelve None si no aplica.
    """
    t = (texto or "").lower()

    # Letras o fragmentos de canciones.
    if re.search(r"\bletra(s)?\b", t) or "lyrics" in t or "fragmento" in t or "estrofa" in t or "coro" in t:
        return (
            "No puedo reproducir letras ni fragmentos de canciones. "
            "Puedo darte datos del catálogo (año, artista, país, categoría)."
        )

    # Enlaces, descargas, streaming o disponibilidad.
    if (
        "http://" in t
        or "https://" in t
        or "link" in t
        or "enlace" in t
        or "descarg" in t
        or "streaming" in t
        or "spotify" in t
        or "youtube" in t
        or "disponible" in t
        or "dónde escuchar" in t
        or "donde escuchar" in t
    ):
        return (
            "No entrego enlaces, descargas ni información de disponibilidad. "
            "Solo informo metadatos del catálogo ochentero."
        )

    # Jailbreak o intento de cambiar reglas.
    if (
        "ignora" in t
        or "olvida tus reglas" in t
        or "revela tu prompt" in t
        or "system prompt" in t
        or "sal de tu rol" in t
        or "actúa como" in t
        or "actua como" in t
        or "jailbreak" in t
        or "dan mode" in t
        or "prompt injection" in t
    ):
        return (
            "No puedo cambiar mis reglas ni salir de mi rol de especialista en "
            "música de los años 80."
        )

    # Otras décadas: cualquier año de 4 dígitos fuera de 1980-1989.
    for coincidencia in re.finditer(r"\b(19\d{2}|20\d{2})\b", t):
        año = int(coincidencia.group(1))
        if año < 1980 or año > 1989:
            return "Solo cubro música de los años 80 (1980-1989)."
    if "años 90" in t or "años 70" in t or "años 60" in t or "década de 1990" in t or "decada de 1990" in t or "siglo xxi" in t:
        return "Solo cubro música de los años 80 (1980-1989)."

    # Programación.
    if "código" in t or "codigo" in t or "python" in t or "programar" in t or "algoritmo" in t or "programación" in t or "programacion" in t:
        return "No respondo temas de programación; solo música de los años 80."

    # Política.
    if "presidente" in t or "política" in t or "politica" in t or "gobierno" in t or "elecciones" in t:
        return "No respondo temas políticos; solo música de los años 80."

    # Asuntos ajenos claros.
    if "receta" in t or "cocina" in t or "matemática" in t or "matematica" in t or "física" in t or "fisica" in t or "clima" in t or "noticias" in t:
        return "Eso queda fuera de mi especialidad; solo música de los años 80."

    return None


def _extraer_ultimo_ai(resultado: dict) -> str:
    mensajes = resultado.get("messages", [])
    for mensaje in reversed(mensajes):
        if getattr(mensaje, "type", None) == "ai" and getattr(mensaje, "content", None):
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


async def responder(texto: str, context_id: str) -> str:
    """Manda el texto al grafo y devuelve la última respuesta del agente (con respaldo ante error 503/429)."""
    if not context_id:
        context_id = str(uuid.uuid4())

    rechazo = _rechazo_deterministico(texto)
    if rechazo is not None:
        return rechazo

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
        etiqueta="Agente música",
    )
    return _extraer_ultimo_ai(resultado)


async def saltos(texto: str) -> str:
    """Ejecuta el grafo mostrando nodos y herramientas por los que pasa."""
    rechazo = _rechazo_deterministico(texto)
    if rechazo is not None:
        print("Rechazo determinístico (sin herramientas).")
        return "Saltos: 0"

    config = {"configurable": {"thread_id": "saltos-cli"}}
    total = 0
    async for paso in graph.astream(
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
    return f"Saltos: {total}"


def diagrama() -> str:
    """Devuelve la estructura del grafo en Mermaid."""
    return graph.get_graph().draw_mermaid()
