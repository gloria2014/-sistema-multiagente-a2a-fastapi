"""Descubrimiento del catálogo de agentes remotos y respaldo integrado para nube (Azure)."""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

load_dotenv(override=True)

import httpx
from a2a.client.card_resolver import A2ACardResolver

from .cliente import obtener_cliente

# Catálogo en memoria: lista de {nombre, descripcion, cliente, responder_local, url}.
CATALOGO: list[dict] = []

URL_PASTELERO = os.getenv("URL_PASTELERO", "http://127.0.0.1:8002")
URL_MUSICA = os.getenv("URL_MUSICA", "http://127.0.0.1:8003")
URL_INNOVACION = os.getenv("URL_INNOVACION", "http://127.0.0.1:8004")

# Otros agentes remotos que pueden estar configurados con nombres propios.
URL_INVERSIONES = (
    os.getenv("URL_INVERSIONES")
    or os.getenv("URL_AGENTE_INVERSIONES")
    or os.getenv("URLS_AGENTE_INVERSIONES")
    or ""
)

# Direcciones de agentes de otros computadores (separadas por comas).
_urls_agentes = [u.strip() for u in os.getenv("URLS_AGENTES", "").split(",") if u.strip()]
_urls_inversiones = [u.strip() for u in URL_INVERSIONES.split(",") if u.strip()]

# Evitar duplicados si un agente ya está en alguna lista.
URLS = []
for _url in [URL_PASTELERO, URL_MUSICA, URL_INNOVACION] + _urls_agentes + _urls_inversiones:
    if _url and _url not in URLS:
        URLS.append(_url)


def _cargar_agentes_integrados() -> list[dict]:
    """Carga las Agent Cards y funciones responder de los 3 agentes cuando corren en contenedor único (Azure)."""
    integrados: list[dict] = []
    modulos = [
        ("src.agente_pastelero.server", "src.agente_pastelero.graph", URL_PASTELERO),
        ("src.agente_musica.server", "src.agente_musica.graph", URL_MUSICA),
        ("src.agente_innovacion.server", "src.agente_innovacion.graph", URL_INNOVACION),
    ]
    import importlib

    for mod_server, mod_graph, url_ref in modulos:
        try:
            srv = importlib.import_module(mod_server)
            grp = importlib.import_module(mod_graph)
            tarjeta = getattr(srv, "tarjeta")
            fn_responder = getattr(grp, "responder")
            integrados.append(
                {
                    "nombre": tarjeta.name,
                    "descripcion": tarjeta.description,
                    "cliente": None,
                    "responder_local": fn_responder,
                    "url": url_ref,
                }
            )
        except Exception as error:  # noqa: BLE001
            print(f"No se pudo cargar agente integrado {mod_server}: {error}")
    return integrados


async def descubrir() -> list[dict]:
    """Descarga la ficha de cada agente por red A2A, o usa el modo integrado si corre en instancia única (Azure)."""
    global CATALOGO
    resultado: list[dict] = []

    # Si estamos en Azure App Service (WEBSITE_SITE_NAME), usar timeout corto para detección rápida
    timeout_red = 2.5 if os.getenv("WEBSITE_SITE_NAME") else 15.0

    for url in URLS:
        try:
            async with httpx.AsyncClient(timeout=timeout_red) as httpx_resolver:
                resolver = A2ACardResolver(httpx_resolver, url)
                tarjeta = await resolver.get_agent_card()
            cliente = await obtener_cliente(url)
            resultado.append(
                {
                    "nombre": tarjeta.name,
                    "descripcion": tarjeta.description,
                    "cliente": cliente,
                    "responder_local": None,
                    "url": url,
                }
            )
        except Exception as error:  # noqa: BLE001 - se avisa y se sigue
            print(
                f"Agente en {url} no responde por puerto separado: "
                f"{str(error).replace(chr(10), ' ').strip()}"
            )

    # Si ningún puerto separado respondió (ej. contenedor único en Azure App Service Free/Basic),
    # registramos las Agent Cards de los 3 agentes especialistas en el mismo proceso.
    if not resultado:
        resultado = _cargar_agentes_integrados()
        if resultado:
            print(
                f"[CATALOGO A2A] Modo contenedor único activo: {len(resultado)} agentes A2A cargados."
            )

    CATALOGO = resultado
    return resultado


def cargar() -> list[dict]:
    """Versión síncrona para usar fuera del event loop."""
    if not CATALOGO:
        try:
            asyncio.run(descubrir())
        except Exception as error:  # noqa: BLE001
            print(f"Error descubriendo agentes: {str(error).replace(chr(10), ' ').strip()}")
    return CATALOGO
