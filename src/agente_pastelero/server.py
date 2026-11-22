"""Servidor A2A del agente pastelero."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder

load_dotenv(override=True)

URL_PASTELERO = os.getenv("URL_PASTELERO", "http://127.0.0.1:8002")

tarjeta = crear_tarjeta(
    "Agente pastelero",
    "Soy Gloria, chef pastelero: respondo sobre recetas dulces, técnicas de "
    "pastelería, ingredientes y decoración. No respondo sobre cocina salada, "
    "carnes, pescados ni platos principales.",
    URL_PASTELERO,
    [
        (
            "catalogo_postres",
            "Catálogo de postres",
            "Entrega receta, ingredientes, tiempos y técnicas de un postre.",
            "receta de brownie",
        ),
    ],
)

app = crear_app(tarjeta, responder)
