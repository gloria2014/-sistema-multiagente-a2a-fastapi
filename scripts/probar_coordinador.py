"""Prueba el coordinador con dos preguntas seguidas (misma conversación)."""

from __future__ import annotations

import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(override=True)

from src.coordinador.cliente import obtener_cliente, preguntar

URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8007")


async def main() -> None:
    context_id = str(uuid.uuid4())
    cliente = await obtener_cliente(URL_COORDINADOR)

    pregunta_1 = "receta de brownie"
    respuesta_1 = await preguntar(cliente, pregunta_1, context_id)
    print(f"Pregunta 1: {pregunta_1}")
    print(f"Respuesta 1: {respuesta_1}\n")

    pregunta_2 = "y cupcake de vainilla?"
    respuesta_2 = await preguntar(cliente, pregunta_2, context_id)
    print(f"Pregunta 2: {pregunta_2}")
    print(f"Respuesta 2: {respuesta_2}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as error:  # noqa: BLE001 - error en una sola línea
        print(f"Error: {str(error).replace(chr(10), ' ').strip()}")
