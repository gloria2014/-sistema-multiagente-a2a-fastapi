"""Servidor A2A del agente de música ochentera."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder

load_dotenv(override=True)

URL_MUSICA = os.getenv("URL_MUSICA", "http://127.0.0.1:8003")

tarjeta = crear_tarjeta(
    "Agente de música ochentera",
    "Agente especializado en música de los años 80. Solo informa sobre "
    "canciones, artistas, años, países y estilos; no reproduce letras ni "
    "entrega descargas ni enlaces.",
    URL_MUSICA,
    [
        (
            "buscar_canciones_cantantes",
            "Buscar canciones y cantantes",
            "Busca canciones por título o artista en el catálogo ochentero.",
            "canciones de Madonna",
        ),
        (
            "listas_por_categoria",
            "Listas por categoría",
            "Lista canciones por categoría (pop, rock, synth-pop, etc.).",
            "5 temas de synth-pop",
        ),
        (
            "sugerencias_segun_interes",
            "Sugerencias según interés",
            "Sugiere canciones según el interés del usuario.",
            "quiero algo bailable",
        ),
    ],
)

app = crear_app(tarjeta, responder)