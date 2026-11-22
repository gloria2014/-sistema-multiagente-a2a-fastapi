"""Creación de la Agent Card de un agente A2A.

La Agent Card es la "ficha" del agente: nombre, descripción, dirección
donde vive, versión, capacidades y habilidades (skills).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from a2a.types import AgentCard, AgentCapabilities, AgentInterface, AgentSkill
from a2a.utils.constants import PROTOCOL_VERSION_1_0, TransportProtocol

load_dotenv(override=True)


def crear_tarjeta(
    nombre: str,
    descripcion: str,
    url: str,
    skills: list[tuple[str, str, str, str]],
) -> AgentCard:
    """Devuelve la Agent Card del agente.

    ``skills`` es una lista de tuplas ``(id, nombre, descripcion, ejemplo)``.
    """
    url_publica = os.getenv("URL_PUBLICA")
    if url_publica:
        url = url_publica

    habilidades = [
        AgentSkill(
            id=identificador,
            name=nombre_skill,
            description=descripcion_skill,
            tags=[nombre_skill],
            examples=[ejemplo] if ejemplo else [],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
        for identificador, nombre_skill, descripcion_skill, ejemplo in skills
    ]

    return AgentCard(
        name=nombre,
        description=descripcion,
        version="1.0.0",
        supported_interfaces=[
            AgentInterface(
                url=url,
                protocol_binding=TransportProtocol.JSONRPC.value,
                protocol_version=PROTOCOL_VERSION_1_0,
            )
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=habilidades,
    )
