"""Prueba el supervisor con 6 preguntas y muestra una tabla."""

from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(override=True)

from src.coordinador.catalogo import descubrir
from src.coordinador.cliente import obtener_cliente, preguntar
from src.coordinador.graph import decidir

URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8007")

PREGUNTAS = [
    "receta de brownie",
    "torta de chocolate",
    "cupcake de vainilla",
    "canciones de Madonna",
    "5 temas de synth-pop",
    "quiero algo bailable",
    "¿qué hago en Roma?",
    "¿cuál es la capital de Francia?",
]


async def main() -> None:
    await descubrir()
    cliente = await obtener_cliente(URL_COORDINADOR)

    filas = []
    for i, pregunta in enumerate(PREGUNTAS):
        agente, motivo = await decidir(pregunta)
        respuesta = await preguntar(cliente, pregunta, f"supervisor-prueba-{i}")
        inicio = respuesta.replace("\n", " ")[:60]
        filas.append((pregunta, agente, motivo, inicio))

    # Tabla
    print(f"{'Pregunta':<32}{'Agente':<22}{'Motivo':<40}{'Inicio respuesta':<62}")
    print("-" * 156)
    for pregunta, agente, motivo, inicio in filas:
        print(f"{pregunta:<32}{agente:<22}{motivo:<40}{inicio:<62}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as error:  # noqa: BLE001 - error en una sola línea
        print(f"Error: {str(error).replace(chr(10), ' ').strip()}")
