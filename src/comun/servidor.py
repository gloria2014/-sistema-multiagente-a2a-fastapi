"""Armado de la aplicación FastAPI de un agente A2A.

Construye la app lista para correr con uvicorn: monta las rutas del
protocolo A2A (tarjeta, JSON-RPC y REST) sobre FastAPI y agrega una
ruta de salud.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from .executor import Executor


def crear_app(tarjeta: AgentCard, responder) -> FastAPI:
    """Arma y devuelve la aplicación FastAPI lista para correr.

    ``tarjeta`` es la Agent Card del agente y ``responder`` su función
    ``responder(texto, context_id)``.
    """
    executor = Executor(responder)
    almacen_tareas = InMemoryTaskStore()
    manejador = DefaultRequestHandler(
        agent_executor=executor,
        task_store=almacen_tareas,
        agent_card=tarjeta,
    )

    app = FastAPI()
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(tarjeta),
        jsonrpc_routes=create_jsonrpc_routes(manejador, rpc_url="/"),
        rest_routes=create_rest_routes(manejador),
    )

    class _FiltroRuidoScanner(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            mensaje = record.getMessage()
            if '"GET /health ' in mensaje or '"GET /v1/models ' in mensaje:
                return False
            if "_ProactorBasePipeTransport._call_connection_lost" in mensaje:
                return False
            if record.exc_info and record.exc_info[1] is not None:
                if isinstance(record.exc_info[1], ConnectionResetError):
                    return False
            return True

    logging.getLogger("uvicorn.access").addFilter(_FiltroRuidoScanner())
    logging.getLogger("asyncio").addFilter(_FiltroRuidoScanner())

    @app.get("/salud")
    @app.get("/health", include_in_schema=False)
    @app.get("/v1/models", include_in_schema=False)
    async def salud() -> dict[str, bool]:
        return {"ok": True}

    return app
