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
    "Agente especializado en innovación: noticias y tendencias actuales de innovación, "
    "metodologías ágiles (Design Thinking, Lean Startup), técnicas de ideación, "
    "experimentación de MVPs y modelos de negocio (Business Model Canvas).",
    URL_INNOVACION,
    [
        (
            "noticias_tendencias_innovacion",
            "Noticias y tendencias de innovación",
            "Informa sobre noticias recientes y tendencias actuales en innovación, tecnología, IA agéntica, sostenibilidad y startups.",
            "cuáles son las noticias y tendencias actuales de innovación",
        ),
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
