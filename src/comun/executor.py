"""Ejecutor A2A compartido por todos los agentes.

Recibe la función ``responder(texto, context_id)`` del agente y la conecta
con el protocolo A2A: cuando llega un mensaje por la red lo convierte en
una llamada a ``responder`` y publica la respuesta en la cola de salida.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Awaitable, Callable, Union

from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue


# Tipo de la función responder que cada agente implementa.
Responder = Callable[[str, str], Union[str, Awaitable[str]]]


class Executor(AgentExecutor):
    """Ejecutor que delega el trabajo en la función ``responder`` del agente."""

    def __init__(self, responder: Responder) -> None:
        self._responder = responder

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        # Texto que escribió el usuario en el mensaje entrante.
        texto = context.get_user_input()
        # Identificador de la conversación: el que viene o uno nuevo.
        context_id = context.context_id or str(uuid.uuid4())

        try:
            resultado = self._responder(texto, context_id)
            # responder puede ser sync o async; se admite cualquiera.
            if asyncio.iscoroutine(resultado):
                resultado = await resultado
            respuesta = str(resultado)
        except Exception as error:  # noqa: BLE001 - se informa sin romperse
            # Regla del proyecto: error en una sola línea, sin stack trace.
            respuesta = f"Error: {str(error).replace(chr(10), ' ').strip()}"

        mensaje = new_text_message(respuesta, context_id=context_id)
        await event_queue.enqueue_event(mensaje)

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        # La cancelación no está soportada en esta base.
        context_id = context.context_id or str(uuid.uuid4())
        mensaje = new_text_message(
            "Cancelación no soportada.", context_id=context_id
        )
        await event_queue.enqueue_event(mensaje)
