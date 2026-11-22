"""Servidor A2A del supervisor."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from . import catalogo
from .graph import responder

load_dotenv(override=True)

URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8007")

tarjeta = crear_tarjeta(
    "Coordinador",
    "Supervisor multi-agente A2A que analiza consultas, solicita datos faltantes "
    "y delega o integra respuestas de los agentes especialistas (pastelería, "
    "música de los años 80 e innovación).",
    URL_COORDINADOR,
    [
        (
            "supervisor",
            "Supervisor Multi-Agente",
            "Elige uno o varios agentes especialistas por A2A e integra sus respuestas conservando datos, cifras y unidades.",
            "receta de brownie para 16 porciones y 2 canciones bailables de los 80",
        ),
    ],
)

app = crear_app(tarjeta, responder)


@app.on_event("startup")
async def al_arrancar() -> None:
    await catalogo.descubrir()
    print(f"Supervisor con {len(catalogo.CATALOGO)} agentes")
