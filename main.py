"""
Punto de entrada por terminal para los agentes del proyecto.

Uso:
    python main.py {pastelero|coordinador} "pregunta"
    python main.py {pastelero|coordinador} "pregunta" --saltos
    python main.py {pastelero|coordinador} --diagrama
"""

from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import asyncio
import importlib
from types import ModuleType

# Agente -> paquete donde va a vivir su código.
PAQUETES: dict[str, str] = {
    "coordinador": "src.coordinador",
    "pastelero": "src.agente_pastelero",
    "musica": "src.agente_musica",
    "innovacion": "src.agente_innovacion",
}

# Por ahora cada agente puede implementarse con un grafo (graph.py)
# o con una tripulación de agentes (crew.py). Se prueba primero graph.py.
MODULOS: tuple[str, ...] = ("graph", "crew")


def cargar_agente(nombre: str) -> ModuleType | None:
    """Importa el módulo del agente; devuelve None si todavía no existe."""
    paquete = PAQUETES[nombre]
    for modulo in MODULOS:
        ruta = f"{paquete}.{modulo}"
        try:
            return importlib.import_module(ruta)
        except ModuleNotFoundError as error:
            # Solo se ignora el caso "todavía no existe ese archivo".
            # Un import roto por otra razón sí debe informarse.
            if error.name != ruta:
                raise
    return None


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        description="Ejecuta un agente del proyecto desde la terminal."
    )
    analizador.add_argument(
        "agente",
        choices=sorted(PAQUETES),
        help="Agente que se quiere ejecutar.",
    )
    analizador.add_argument(
        "pregunta",
        nargs="?",
        help="Pregunta para el agente (no hace falta con --diagrama).",
    )
    analizador.add_argument(
        "--saltos",
        action="store_true",
        help="Muestra por qué nodos y herramientas pasó el agente.",
    )
    analizador.add_argument(
        "--diagrama",
        action="store_true",
        help="Imprime la estructura del agente en Mermaid, sin ejecutarlo.",
    )
    analizador.add_argument(
        "--context-id",
        default=None,
        help="Identificador de conversación para conservar memoria entre llamadas.",
    )
    analizador.add_argument(
        "--segunda",
        default=None,
        help="Segunda pregunta en el mismo proceso (prueba de memoria).",
    )
    args = analizador.parse_args(argv)

    try:
        modulo = cargar_agente(args.agente)
        if modulo is None:
            print(f"Ese agente todavía no existe: {args.agente}.")
            return 1

        if args.diagrama:
            print(modulo.diagrama())
            return 0

        context_id = args.context_id or "cli"

        if not args.pregunta and not args.segunda:
            print(
                'Falta la pregunta. Ejemplo: python main.py '
                f'{args.agente} "¿Qué me recomiendas?"'
            )
            return 2

        # Dos turnos en el mismo proceso (prueba de memoria).
        if args.segunda:
            if args.pregunta:
                if args.saltos:
                    resultado_saltos = modulo.saltos(args.pregunta)
                    if asyncio.iscoroutine(resultado_saltos):
                        resultado_saltos = asyncio.run(resultado_saltos)
                    print(resultado_saltos)
                else:
                    resultado = modulo.responder(args.pregunta, context_id)
                    if asyncio.iscoroutine(resultado):
                        resultado = asyncio.run(resultado)
                    print(resultado)
            if args.saltos:
                resultado_saltos = modulo.saltos(args.segunda)
                if asyncio.iscoroutine(resultado_saltos):
                    resultado_saltos = asyncio.run(resultado_saltos)
                print(resultado_saltos)
            else:
                resultado = modulo.responder(args.segunda, context_id)
                if asyncio.iscoroutine(resultado):
                    resultado = asyncio.run(resultado)
                print(resultado)
            return 0

        if args.saltos:
            resultado_saltos = modulo.saltos(args.pregunta)
            if asyncio.iscoroutine(resultado_saltos):
                resultado_saltos = asyncio.run(resultado_saltos)
            print(resultado_saltos)
        else:
            resultado = modulo.responder(args.pregunta, context_id)
            if asyncio.iscoroutine(resultado):
                resultado = asyncio.run(resultado)
            print(resultado)
        return 0

    except Exception as error:
        # Regla del proyecto: error en una sola línea, sin stack trace.
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
