"""Grafo del supervisor (LangGraph)."""

from __future__ import annotations

import os
import re
import uuid
from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field, create_model

from src.comun.llm import (
    crear_modelo_chat,
    ejecutar_con_respaldo,
    obtener_lista_modelos,
)

from . import catalogo
from .cliente import preguntar

load_dotenv(override=True)

MODELO = os.getenv("MODELO", "gemini-2.5-flash")
CLAVE_API = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or "pendiente-de-configurar"
)


class SubconsultaAgente(BaseModel):
    agente: str = Field(description="Nombre exacto del agente en el catálogo.")
    consulta: str = Field(
        description="Pregunta o instrucción específica para este agente, conservando todos los números, unidades y condiciones del usuario."
    )


class Estado(MessagesState):
    context_id: str
    agente: str
    agentes_elegidos: list[dict[str, str]]
    motivo: str
    faltan_datos: bool
    es_saludo: bool
    pregunta_aclaracion: str
    aportes: list[dict[str, str]]


def _extraer_texto_contenido(contenido: object) -> str:
    """Extrae texto limpio cuando Gemini devuelve un str o una lista de bloques dict."""
    if isinstance(contenido, str):
        return contenido.strip()
    if isinstance(contenido, list):
        partes = []
        for item in contenido:
            if isinstance(item, str):
                partes.append(item)
            elif isinstance(item, dict) and "text" in item:
                partes.append(str(item["text"]))
        return "".join(partes).strip()
    return str(contenido).strip()


def _texto_usuario(state: Estado) -> str:
    mensajes = state.get("messages", [])
    if mensajes:
        for msg in reversed(mensajes):
            if getattr(msg, "type", None) == "human" or isinstance(msg, HumanMessage):
                contenido = getattr(msg, "content", None)
                return _extraer_texto_contenido(contenido)
    return ""


def _historial_reciente(state: Estado) -> str:
    """Extrae un resumen breve de los mensajes previos para dar contexto en turnos seguidos."""
    mensajes = state.get("messages", [])
    if len(mensajes) <= 1:
        return ""
    previos = mensajes[:-1][-4:]
    lineas = []
    for m in previos:
        rol = "Usuario" if getattr(m, "type", None) == "human" else "Asistente"
        texto = getattr(m, "content", "")
        if isinstance(texto, str) and texto.strip():
            lineas.append(f"{rol}: {texto.strip()[:200]}")
    return "\n".join(lineas)


def _es_saludo_o_ayuda(texto: str) -> bool:
    """Detecta si el mensaje del usuario es un saludo general o solicitud de presentación."""
    t = re.sub(r"[¡!¿?.,;:]+", "", (texto or "").strip().lower())
    saludos_exactos = {
        "hola",
        "hola buenos dias",
        "hola buenas tardes",
        "hola buenas noches",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "buenas",
        "que tal",
        "hola que tal",
        "hola como estas",
        "como estas",
        "quien eres",
        "que eres",
        "que haces",
        "que puedes hacer",
        "en que me puedes ayudar",
        "ayuda",
        "menu",
        "agentes",
        "que agentes tienes",
        "cuales son tus agentes",
        "gracias",
        "muchas gracias",
    }
    if t in saludos_exactos:
        return True
    palabras = t.split()
    if len(palabras) <= 4 and any(p in ("hola", "buenos", "buenas", "saludos") for p in palabras):
        # Verificar que no venga acompañado ya de una pregunta de dominio
        palabras_dominio = ("receta", "brownie", "torta", "cancion", "musica", "madonna", "innovacion", "scamper", "ideacion", "porciones")
        if not any(d in t for d in palabras_dominio):
            return True
    return False


def _detectar_datos_faltantes(texto: str) -> str | None:
    """Verifica de forma determinística si el usuario pide escalar una receta sin indicar porciones."""
    t = (texto or "").lower()
    pide_escalar = any(
        palabra in t
        for palabra in ("escala", "escalar", "ajusta", "ajustar", "multiplica", "porciones", "personas")
    )
    tiene_numero = bool(re.search(r"\b\d+\b", t))
    if ("escala" in t or "escalar" in t or "para cuántas porciones" in t) and not tiene_numero:
        return (
            "Para escalar o calcular la receta con exactitud, necesito un dato faltante: "
            "¿para cuántas porciones o personas deseas preparar el postre?"
        )
    if pide_escalar and ("porciones" in t or "personas" in t) and not tiene_numero:
        return (
            "Por favor indícame la cantidad exacta de porciones o personas para poder "
            "calcular las cantidades e ingredientes sin alterar las proporciones."
        )
    return None


async def supervisor(state: Estado) -> dict:
    """Analiza la consulta, verifica si faltan datos y selecciona uno o varios agentes del catálogo."""
    if not catalogo.CATALOGO:
        await catalogo.descubrir()

    texto_usuario = _texto_usuario(state)
    context_id = state.get("context_id") or "sin-contexto"

    if not texto_usuario or not texto_usuario.strip():
        return {
            "agente": "ninguno",
            "agentes_elegidos": [],
            "motivo": "La consulta está vacía.",
            "faltan_datos": True,
            "es_saludo": False,
            "pregunta_aclaracion": "La consulta está vacía. Por favor escribe una pregunta o solicitud válida.",
        }

    # Detectar saludos o preguntas generales sobre qué hace el coordinador.
    if _es_saludo_o_ayuda(texto_usuario):
        print(f"[SUPERVISOR] context_id={context_id} -> Saludo o consulta de bienvenida detectada.")
        return {
            "agente": "Coordinador",
            "agentes_elegidos": [],
            "motivo": "Saludo o solicitud de bienvenida atendida por el Coordinador.",
            "faltan_datos": False,
            "es_saludo": True,
            "pregunta_aclaracion": "",
        }

    # Verificación rápida de datos faltantes para cálculos/escalado.
    aclaracion_deterministica = _detectar_datos_faltantes(texto_usuario)
    if aclaracion_deterministica:
        print(f"[SUPERVISOR] context_id={context_id} -> Solicita datos faltantes antes de concluir.")
        return {
            "agente": "ninguno",
            "agentes_elegidos": [],
            "motivo": "Faltan datos requeridos para el cálculo (número de porciones).",
            "faltan_datos": True,
            "es_saludo": False,
            "pregunta_aclaracion": aclaracion_deterministica,
        }

    nombres_catalogo = [a["nombre"] for a in catalogo.CATALOGO]
    if not nombres_catalogo:
        return {
            "agente": "ninguno",
            "agentes_elegidos": [],
            "motivo": "No hay agentes remotos disponibles en el catálogo.",
            "faltan_datos": False,
            "es_saludo": False,
            "pregunta_aclaracion": "",
        }

    opciones = nombres_catalogo + ["ninguno"]

    DecisionSupervisor = create_model(
        "DecisionSupervisor",
        agentes=(list[SubconsultaAgente], Field(default_factory=list, description="Lista de agentes que deben participar para responder la consulta completa.")),
        agente_principal=(Literal[*opciones], Field(description="Agente principal o 'ninguno' si ninguno aplica.")),
        motivo=(str, Field(description="Justificación breve de la selección.")),
        faltan_datos=(bool, Field(default=False, description="True solo si el usuario pide un cálculo o escalado pero omitió un dato numérico indispensable.")),
        pregunta_aclaracion=(str, Field(default="", description="Si faltan_datos es True, qué dato puntual se debe pedir al usuario.")),
    )

    catalogo_texto = "\n".join(
        f"- {a['nombre']}: {a['descripcion']}" for a in catalogo.CATALOGO
    )
    nombres_validos = ", ".join(f"'{n}'" for n in nombres_catalogo)
    historial = _historial_reciente(state)
    bloque_historial = f"\nContexto de conversación previa:\n{historial}\n" if historial else ""

    prompt_sistema = (
        "Eres el coordinador de un sistema multi-agente A2A. "
        "Usa las descripciones del catálogo como información para decidir qué agente o agentes deben responder.\n"
        f"Agentes disponibles (usa SOLO estos nombres exactos): {nombres_validos}.\n"
        "Reglas:\n"
        "1. Si la consulta abarca un solo tema del catálogo, inclúyelo en 'agentes' y en 'agente_principal'.\n"
        "2. Si la consulta combina varios temas (por ejemplo: pastelería + música de los 80 + innovación), "
        "incluye TODOS los agentes correspondientes en la lista 'agentes', asignando a cada uno su subconsulta específica "
        "sin alterar números, porciones, años ni condiciones.\n"
        "3. Si el usuario pide escalar o ajustar una receta a cierta cantidad de personas/porciones pero NO indica el número, "
        "marca 'faltan_datos'=True y redacta en 'pregunta_aclaracion' la solicitud del dato faltante.\n"
        "4. Si la consulta no corresponde a ningún agente del catálogo, deja 'agentes' vacío y 'agente_principal'='ninguno'.\n\n"
        f"Catálogo:\n{catalogo_texto}"
        f"{bloque_historial}"
    )

    modelos_disponibles = obtener_lista_modelos(MODELO)

    async def _invocar_decision(nombre_modelo: str):
        llm = crear_modelo_chat(
            nombre_modelo=nombre_modelo,
            clave_api=CLAVE_API,
            timeout=60,
            max_retries=2,
        )
        estructurado = llm.with_structured_output(DecisionSupervisor)
        return await estructurado.ainvoke(
            [("system", prompt_sistema), ("user", texto_usuario)]
        )

    try:
        decision = await ejecutar_con_respaldo(
            modelos=modelos_disponibles,
            funcion_por_modelo=_invocar_decision,
            etiqueta="Supervisor",
        )

        if decision.faltan_datos and decision.pregunta_aclaracion.strip():
            print(f"[SUPERVISOR] context_id={context_id} -> Datos faltantes detectados: {decision.motivo}")
            return {
                "agente": "ninguno",
                "agentes_elegidos": [],
                "motivo": decision.motivo,
                "faltan_datos": True,
                "es_saludo": False,
                "pregunta_aclaracion": decision.pregunta_aclaracion.strip(),
            }

        seleccionados: list[dict[str, str]] = []
        vistos: set[str] = set()
        for item in decision.agentes or []:
            if item.agente in nombres_catalogo and item.agente not in vistos:
                vistos.add(item.agente)
                seleccionados.append(
                    {
                        "nombre": item.agente,
                        "consulta": item.consulta.strip() or texto_usuario,
                    }
                )

        if not seleccionados and decision.agente_principal in nombres_catalogo:
            seleccionados.append(
                {
                    "nombre": decision.agente_principal,
                    "consulta": texto_usuario,
                }
            )

        agente_principal = seleccionados[0]["nombre"] if seleccionados else "ninguno"
        nombres_log = ", ".join(s["nombre"] for s in seleccionados) if seleccionados else "ninguno"
        print(
            f"[SUPERVISOR] context_id={context_id} | agentes=[{nombres_log}] | motivo={decision.motivo}"
        )

        return {
            "agente": agente_principal,
            "agentes_elegidos": seleccionados,
            "motivo": decision.motivo,
            "faltan_datos": False,
            "es_saludo": False,
            "pregunta_aclaracion": "",
        }
    except Exception as error:  # noqa: BLE001
        mensaje_err = str(error).replace(chr(10), " ").strip()[:120]
        print(f"[SUPERVISOR] Error al decidir agente: {mensaje_err}")
        return {
            "agente": "ninguno",
            "agentes_elegidos": [],
            "motivo": f"decisión no válida: {mensaje_err}",
            "faltan_datos": False,
            "es_saludo": False,
            "pregunta_aclaracion": "",
        }


async def agente_remoto(state: Estado) -> dict:
    """Consulta por A2A a cada agente seleccionado e integra los resultados conservando cifras, unidades y supuestos."""
    seleccionados = state.get("agentes_elegidos") or []
    if not seleccionados and state.get("agente") and state.get("agente") != "ninguno":
        seleccionados = [{"nombre": state["agente"], "consulta": _texto_usuario(state)}]

    context_id = state.get("context_id") or str(uuid.uuid4())
    aportes: list[dict[str, str]] = []

    for item in seleccionados:
        agente_nombre = item["nombre"]
        subconsulta = item.get("consulta") or _texto_usuario(state)
        cliente = None
        responder_local = None
        url_agente = ""
        for a in catalogo.CATALOGO:
            if a["nombre"] == agente_nombre:
                cliente = a.get("cliente")
                responder_local = a.get("responder_local")
                url_agente = a.get("url", "")
                break

        if cliente is None and responder_local is None:
            aportes.append(
                {
                    "agente": agente_nombre,
                    "respuesta": f"No se encontró el agente {agente_nombre} en el catálogo.",
                    "error": "true",
                }
            )
            continue

        print(
            f"[A2A] Enviando solicitud a '{agente_nombre}' ({url_agente}) | context_id={context_id} | consulta='{subconsulta}'"
        )
        try:
            if cliente is not None:
                respuesta = await preguntar(cliente, subconsulta, context_id)
            else:
                import asyncio as _asyncio

                res_local = responder_local(subconsulta, context_id)
                if _asyncio.iscoroutine(res_local):
                    res_local = await res_local
                respuesta = str(res_local)
            resumen_log = respuesta.replace(chr(10), " ").strip()[:100]
            print(f"[A2A] Respuesta recibida de '{agente_nombre}': {resumen_log}...")
            aportes.append(
                {
                    "agente": agente_nombre,
                    "consulta": subconsulta,
                    "respuesta": respuesta,
                    "error": "",
                }
            )
        except Exception as error:  # noqa: BLE001 - se avisa en una línea y se sigue
            detalle = str(error).replace(chr(10), " ").strip()
            print(f"[A2A] Error consultando a '{agente_nombre}': {detalle}")
            aportes.append(
                {
                    "agente": agente_nombre,
                    "consulta": subconsulta,
                    "respuesta": f"No se pudo consultar al agente {agente_nombre}: {detalle}",
                    "error": "true",
                }
            )

    # Si participó un solo agente, devolvemos su respuesta directa con su etiqueta para total fidelidad.
    if len(aportes) == 1:
        unico = aportes[0]
        return {
            "aportes": aportes,
            "messages": [AIMessage(content=f"[{unico['agente']}] {unico['respuesta']}")],
        }

    # Si participaron varios agentes, conservamos cada aporte íntegro con sus cifras, unidades y supuestos,
    # y añadimos una conclusión integrada fiel.
    bloques_aportes = []
    for ap in aportes:
        bloques_aportes.append(f"[{ap['agente']}]\n{ap['respuesta']}")

    texto_aportes = "\n\n".join(bloques_aportes)

    prompt_integracion = (
        "Eres el coordinador A2A. A continuación tienes las respuestas exactas entregadas por los agentes especialistas.\n"
        "Redacta una breve conclusión integradora al final que conecte los aportes para responder al usuario, "
        "cumpliendo estrictamente estas reglas de fidelidad:\n"
        "- CONSERVA intactos todos los datos, cálculos, factores de escalado, cantidades, unidades (g, ml, °C, min, horas), "
        "años (1980-1989), países, nombres de canciones/artistas y supuestos (ej. receta base 8 porciones).\n"
        "- NO inventes cifras ni modifiques las cantidades entregadas por los agentes.\n"
        "- Si algún agente reportó un error o límite, refléjalo con claridad sin ocultarlo."
    )

    try:
        modelos_disponibles = obtener_lista_modelos(MODELO)

        async def _invocar_sintesis(nombre_modelo: str):
            llm = crear_modelo_chat(
                nombre_modelo=nombre_modelo,
                clave_api=CLAVE_API,
                timeout=60,
                max_retries=2,
            )
            return await llm.ainvoke(
                [
                    ("system", prompt_integracion),
                    (
                        "user",
                        f"Solicitud original: {_texto_usuario(state)}\n\nAportes de los agentes:\n{texto_aportes}",
                    ),
                ]
            )

        sintesis = await ejecutar_con_respaldo(
            modelos=modelos_disponibles,
            funcion_por_modelo=_invocar_sintesis,
            etiqueta="Coordinador-Síntesis",
        )
        contenido_sintesis = _extraer_texto_contenido(getattr(sintesis, "content", ""))
        respuesta_final = (
            f"{texto_aportes}\n\n"
            f"[Conclusión integrada del Coordinador]\n{contenido_sintesis}"
        )
    except Exception:  # noqa: BLE001 - si falla el LLM de síntesis, devolvemos los aportes íntegros
        respuesta_final = texto_aportes

    return {
        "aportes": aportes,
        "messages": [AIMessage(content=respuesta_final)],
    }


async def pedir_datos(state: Estado) -> dict:
    """Solicita al usuario los datos faltantes antes de invocar a los agentes."""
    pregunta = (
        state.get("pregunta_aclaracion")
        or "Faltan datos en tu consulta. Por favor especifica los detalles o cantidades necesarias."
    )
    return {
        "messages": [AIMessage(content=f"[Coordinador - Datos faltantes] {pregunta}")]
    }


async def responder_saludo(state: Estado) -> dict:
    """Responde cordialmente a saludos o consultas generales indicando los agentes A2A disponibles."""
    if not catalogo.CATALOGO:
        await catalogo.descubrir()
    detalles = []
    for a in catalogo.CATALOGO:
        detalles.append(f"• {a['nombre']}: {a['descripcion']}")
    bloque_agentes = "\n".join(detalles) if detalles else "• (Verifica que los agentes especialistas estén activos)"
    mensaje = (
        "[Coordinador] ¡Hola! Soy el Coordinador del sistema multi-agente A2A.\n"
        "Puedo ayudarte conectando tu consulta con uno o varios de nuestros agentes especialistas:\n\n"
        f"{bloque_agentes}\n\n"
        "Puedes hacerme una consulta para un agente o combinar varios temas en una misma solicitud. ¿En qué te puedo ayudar hoy?"
    )
    return {"messages": [AIMessage(content=mensaje)]}


async def sin_agente(state: Estado) -> dict:
    """Responde cuando ningún agente aplica o no hay agentes activos."""
    nombres = [a["nombre"] for a in catalogo.CATALOGO]
    if not nombres:
        mensaje = (
            "Error: No hay agentes especialistas disponibles en este momento. "
            "Verifica que los servidores de los agentes estén encendidos."
        )
    else:
        lista = ", ".join(nombres)
        mensaje = (
            f"Fuera de alcance: No tengo un agente especialista para esa consulta. "
            f"Agentes disponibles: {lista}."
        )
    return {"messages": [AIMessage(content=mensaje)]}


def _elegir_ruta(state: Estado) -> str:
    if state.get("es_saludo"):
        return "responder_saludo"
    if state.get("faltan_datos"):
        return "pedir_datos"
    if state.get("agente") == "ninguno" and not state.get("agentes_elegidos"):
        return "sin_agente"
    return "agente_remoto"


def _construir_grafo():
    grafo = StateGraph(Estado)
    grafo.add_node("supervisor", supervisor)
    grafo.add_node("agente_remoto", agente_remoto)
    grafo.add_node("pedir_datos", pedir_datos)
    grafo.add_node("responder_saludo", responder_saludo)
    grafo.add_node("sin_agente", sin_agente)
    grafo.add_edge(START, "supervisor")
    grafo.add_conditional_edges(
        "supervisor",
        _elegir_ruta,
        {
            "agente_remoto": "agente_remoto",
            "pedir_datos": "pedir_datos",
            "responder_saludo": "responder_saludo",
            "sin_agente": "sin_agente",
        },
    )
    grafo.add_edge("agente_remoto", END)
    grafo.add_edge("pedir_datos", END)
    grafo.add_edge("responder_saludo", END)
    grafo.add_edge("sin_agente", END)
    return grafo.compile(checkpointer=MemorySaver())


graph = _construir_grafo()


async def decidir(texto: str) -> tuple[str, str]:
    """Devuelve (agente, motivo) para una pregunta, sin ejecutar al agente."""
    estado_temp: Estado = {
        "messages": [HumanMessage(content=texto)],
        "context_id": "decidir",
        "agente": "",
        "agentes_elegidos": [],
        "motivo": "",
        "faltan_datos": False,
        "pregunta_aclaracion": "",
        "aportes": [],
    }
    resultado = await supervisor(estado_temp)
    elegidos = resultado.get("agentes_elegidos") or []
    if len(elegidos) > 1:
        nombres = " + ".join(e["nombre"] for e in elegidos)
        return nombres, resultado.get("motivo", "")
    return resultado.get("agente", "ninguno"), resultado.get("motivo", "")


async def consultar_detallado(texto: str, context_id: str) -> dict:
    """Ejecuta el grafo del coordinador y devuelve la respuesta junto con los metadatos A2A."""
    if not catalogo.CATALOGO:
        await catalogo.descubrir()
    config = {"configurable": {"thread_id": context_id}}
    estado_inicial = {
        "messages": [HumanMessage(content=texto)],
        "context_id": context_id,
        "agente": "",
        "agentes_elegidos": [],
        "motivo": "",
        "faltan_datos": False,
        "es_saludo": False,
        "pregunta_aclaracion": "",
        "aportes": [],
    }
    resultado = await graph.ainvoke(estado_inicial, config=config)
    respuesta_texto = ""
    mensajes = resultado.get("messages", [])
    for mensaje in reversed(mensajes):
        if getattr(mensaje, "type", None) == "ai" and mensaje.content:
            respuesta_texto = _extraer_texto_contenido(mensaje.content)
            break

    agentes_participantes = [
        a["nombre"] for a in (resultado.get("agentes_elegidos") or [])
    ]
    return {
        "context_id": context_id,
        "respuesta": respuesta_texto,
        "agentes": agentes_participantes,
        "motivo": resultado.get("motivo", ""),
        "faltan_datos": bool(resultado.get("faltan_datos", False)),
        "aportes": resultado.get("aportes", []),
    }


async def responder(texto: str, context_id: str) -> str:
    detalle = await consultar_detallado(texto, context_id)
    return detalle["respuesta"]


async def saltos(texto: str) -> str:
    if not catalogo.CATALOGO:
        await catalogo.descubrir()
    config = {"configurable": {"thread_id": "saltos-cli"}}
    total = 0
    async for paso in graph.astream(
        {
            "messages": [HumanMessage(content=texto)],
            "context_id": "saltos-cli",
            "agente": "",
            "agentes_elegidos": [],
            "motivo": "",
            "faltan_datos": False,
            "pregunta_aclaracion": "",
            "aportes": [],
        },
        config=config,
        stream_mode="updates",
    ):
        for nodo, actualizacion in paso.items():
            total += 1
            print(f"[{total}] Nodo: {nodo}")
            if nodo == "supervisor" and isinstance(actualizacion, dict):
                elegidos = actualizacion.get("agentes_elegidos") or []
                nombres = ", ".join(e["nombre"] for e in elegidos) or actualizacion.get("agente")
                print(f"     agentes elegidos: {nombres}")
                print(f"     motivo: {actualizacion.get('motivo')}")
                if actualizacion.get("faltan_datos"):
                    print(f"     datos faltantes: {actualizacion.get('pregunta_aclaracion')}")
    return f"Total de saltos: {total}"


def diagrama() -> str:
    return graph.get_graph().draw_mermaid()
