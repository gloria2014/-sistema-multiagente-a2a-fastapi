"""Servidor A2A del agente de innovación."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder

load_dotenv(override=True)

URL_INNOVACION = os.getenv("URL_INNOVACION", "http://127.0.0.1:8004")

tarjeta = crear_tarjeta(
    "Agente Innovacion",
    "Agente especializado exclusivamente en metodologías de innovación, "
    "experimentación y modelos de negocio. Solo entrega información verificada.",
    URL_INNOVACION,
    [
        (
            "metodologias_innovacion",
            "Metodologías de innovación",
            "Consulta y aplicación de frameworks de innovación.",
            "metodologías de innovación centradas en el usuario",
        ),
        (
            "tecnicas_ideacion",
            "Técnicas de ideación",
            "Selección de dinámicas de generación de ideas.",
            "técnicas de divergencia para idear",
        ),
        (
            "experimentacion_negocio",
            "Experimentación y negocio",
            "Diseño de experimentos y validación de hipótesis de negocio.",
            "validar una hipótesis de negocio",
        ),
    ],
)

app = crear_app(tarjeta, responder)