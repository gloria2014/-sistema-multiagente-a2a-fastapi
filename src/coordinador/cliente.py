"""Cliente A2A para hablar con otros agentes."""

from __future__ import annotations

import asyncio
import os
import uuid

import httpx
from a2a.client import Client, ClientConfig, create_client
from a2a.client.card_resolver import A2ACardResolver
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import (
    GetTaskRequest,
    Role,
    SendMessageRequest,
    TaskState,
)

# Clientes ya descargados: url -> cliente (para no bajar la ficha cada vez).
_CLIENTES: dict[str, Client] = {}

# Estados terminales de una tarea.
_ESTADOS_TERMINALES = {
    TaskState.TASK_STATE_COMPLETED,
    TaskState.TASK_STATE_FAILED,
    TaskState.TASK_STATE_CANCELED,
    TaskState.TASK_STATE_REJECTED,
}


async def obtener_cliente(url: str) -> Client:
    """Descarga la ficha del agente en ``url`` y arma un cliente (sin streaming, JSONRPC)."""
    if url in _CLIENTES:
        return _CLIENTES[url]

    # Descargar la ficha con A2ACardResolver.
    async with httpx.AsyncClient(timeout=120.0) as httpx_resolver:
        resolver = A2ACardResolver(httpx_resolver, url)
        tarjeta = await resolver.get_agent_card()

    # Usar siempre la URL de descubrimiento para hablar: es la dirección por
    # la que se pudo leer la ficha y evita quedarse con una URL pública
    # desactualizada (túnel caído) o una dirección local inalcanzable.
    try:
        if tarjeta.supported_interfaces:
            tarjeta.supported_interfaces[0].url = url
    except Exception:  # noqa: BLE001 - no bloquear por esto
        pass

    # Cliente sin streaming, protocolo JSONRPC, con timeout amplio (Gemini puede tardar).
    httpx_cliente = httpx.AsyncClient(timeout=120.0)
    config = ClientConfig(
        streaming=False,
        httpx_client=httpx_cliente,
        supported_protocol_bindings=["JSONRPC"],
    )
    cliente = await create_client(tarjeta, client_config=config)
    _CLIENTES[url] = cliente
    return cliente


async def preguntar(cliente: Client, texto: str, context_id: str) -> str:
    """Manda ``texto`` al agente y devuelve su respuesta como texto."""
    mensaje = new_text_message(texto, context_id=context_id, role=Role.ROLE_USER)
    request = SendMessageRequest(message=mensaje)

    textos: list[str] = []
    tarea_actual = None

    async for respuesta in cliente.send_message(request):
        if getattr(respuesta, "message", None):
            textos.append(get_message_text(respuesta.message))
        elif getattr(respuesta, "task", None):
            tarea_actual = respuesta.task
        elif getattr(respuesta, "status_update", None):
            if respuesta.status_update.status and respuesta.status_update.status.message:
                textos.append(get_message_text(respuesta.status_update.status.message))
        elif getattr(respuesta, "artifact_update", None):
            if respuesta.artifact_update.artifact:
                textos.append(get_artifact_text(respuesta.artifact_update.artifact))

    # Si la respuesta fue una tarea, esperar a que termine y juntar artifacts.
    if tarea_actual is not None and not textos:
        task_id = tarea_actual.id
        tarea = tarea_actual
        while getattr(tarea.status, "state", None) not in _ESTADOS_TERMINALES:
            await asyncio.sleep(0.5)
            tarea = await cliente.get_task(GetTaskRequest(id=task_id))
        for artifact in getattr(tarea, "artifacts", []) or []:
            textos.append(get_artifact_text(artifact))
        if not textos and getattr(tarea.status, "message", None):
            textos.append(get_message_text(tarea.status.message))

    return "\n".join(t for t in textos if t).strip()
