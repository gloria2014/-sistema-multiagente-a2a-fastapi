"""Descubrimiento del catálogo de agentes remotos."""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

load_dotenv(override=True)

import httpx
from a2a.client.card_resolver import A2ACardResolver

from .cliente import obtener_cliente

# Catálogo en memoria: lista de {nombre, descripcion, cliente}.
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


async def descubrir() -> list[dict]:
    """Descarga la ficha de cada agente y arma el cliente. Devuelve el catálogo."""
    global CATALOGO
    resultado: list[dict] = []
    for url in URLS:
        try:
            async with httpx.AsyncClient(timeout=120.0) as httpx_resolver:
                resolver = A2ACardResolver(httpx_resolver, url)
                tarjeta = await resolver.get_agent_card()
            cliente = await obtener_cliente(url)
            resultado.append(
                {
                    "nombre": tarjeta.name,
                    "descripcion": tarjeta.description,
                    "cliente": cliente,
                    "url": url,
                }
            )
        except Exception as error:  # noqa: BLE001 - se avisa y se sigue
            print(
                f"Agente en {url} no responde: "
                f"{str(error).replace(chr(10), ' ').strip()}"
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
