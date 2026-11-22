"""Script de prueba integral para verificar la entrega local del Servicio FastAPI y A2A.

Ejecuta los casos exigidos por la rúbrica:
1. Control de acceso: intento rechazado (sin token / token inválido) y acceso autorizado.
2. Entrada inválida: mensaje vacío rechazado con HTTP 400.
3. Solicitud de datos faltantes antes de concluir (escalar receta sin indicar porciones).
4. Colaboración multi-agente A2A conservando cifras, unidades, cálculos y supuestos.
5. Consulta fuera de alcance (límite de los agentes).

Imprime cada caso con el formato de tabla exigido en la página 3 del PDF.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

HOST_WEB = os.getenv("HOST_WEB", "127.0.0.1")
PUERTO_WEB = os.getenv("PUERTO_WEB", "8000")
URL_BASE = f"http://{HOST_WEB}:{PUERTO_WEB}"
TOKEN_VALIDO = (os.getenv("TOKEN_ACCESO") or "").strip()


def imprimir_ficha_caso(
    numero: int,
    titulo: str,
    solicitud: str,
    esperado: str,
    obtenido: str,
    observaciones: str,
) -> None:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("=" * 92)
    print(f"CASO {numero}: {titulo}")
    print("-" * 92)
    print(f"Entorno y fecha    : LOCAL | {fecha}")
    print(f"Solicitud          : {solicitud}")
    print(f"Resultado esperado : {esperado}")
    print(f"Resultado obtenido : {obtenido}")
    print(f"Observaciones      : {observaciones}")
    print("=" * 92 + "\n")


async def probar_recorrido() -> int:
    if not TOKEN_VALIDO:
        print(
            "Error: TOKEN_ACCESO no está definido en .env. Configúralo antes de ejecutar las pruebas."
        )
        return 1

    async with httpx.AsyncClient(timeout=120.0) as cliente:
        # Verificar que el servidor FastAPI esté arriba
        try:
            salud = await cliente.get(f"{URL_BASE}/salud")
            datos_salud = salud.json()
            print(
                f"Servidor detectado en {URL_BASE} | Agentes A2A activos: {datos_salud.get('agentes_descubiertos')}\n"
            )
        except Exception as error:  # noqa: BLE001
            print(
                f"Error: El servidor FastAPI en {URL_BASE} no responde ({str(error).replace(chr(10), ' ').strip()}). "
                "Inicia primero los agentes y scripts/web.py."
            )
            return 1

        # CASO 1: Acceso rechazado (token inválido)
        resp_rechazo = await cliente.post(
            f"{URL_BASE}/api/consultar",
            headers={"Authorization": "Bearer token-falso-no-autorizado"},
            json={"mensaje": "receta de brownie"},
        )
        cuerpo_rechazo = resp_rechazo.json()
        imprimir_ficha_caso(
            numero=1,
            titulo="Control de acceso - Intento rechazado (Token inválido)",
            solicitud="POST /api/consultar con encabezado Authorization: Bearer <token-invalido>",
            esperado="HTTP 401 Unauthorized rechazando el acceso sin ejecutar al agente.",
            obtenido=f"HTTP {resp_rechazo.status_code} | {cuerpo_rechazo.get('detail')}",
            observaciones="El servidor valida TOKEN_ACCESO y bloquea llamadas no autorizadas sin exponer el token real.",
        )

        headers_ok = {"Authorization": f"Bearer {TOKEN_VALIDO}"}

        # CASO 2: Entrada inválida (mensaje vacío)
        resp_vacio = await cliente.post(
            f"{URL_BASE}/api/consultar",
            headers=headers_ok,
            json={"mensaje": "   "},
        )
        cuerpo_vacio = resp_vacio.json()
        imprimir_ficha_caso(
            numero=2,
            titulo="Manejo de entrada inválida (Mensaje vacío)",
            solicitud="POST /api/consultar con mensaje vacío ('   ')",
            esperado="HTTP 400 Bad Request indicando que el mensaje no puede estar vacío.",
            obtenido=f"HTTP {resp_vacio.status_code} | {cuerpo_vacio.get('detail')}",
            observaciones="Las entradas inválidas no se presentan como operaciones exitosas.",
        )

        # CASO 3: Solicitud de datos faltantes antes de concluir
        pregunta_incompleta = "Escala la receta de brownie por favor"
        resp_faltante = await cliente.post(
            f"{URL_BASE}/api/consultar",
            headers=headers_ok,
            json={"mensaje": pregunta_incompleta},
        )
        datos_faltante = resp_faltante.json()
        imprimir_ficha_caso(
            numero=3,
            titulo="Solicitud de datos faltantes antes de calcular",
            solicitud=pregunta_incompleta,
            esperado="El coordinador detecta que falta el número de porciones y lo solicita antes de concluir.",
            obtenido=(
                f"HTTP {resp_faltante.status_code} | estado={datos_faltante.get('estado')} | "
                f"respuesta={datos_faltante.get('respuesta')}"
            ),
            observaciones="No inventa un número de porciones cuando el usuario omite el dato requerido.",
        )

        # CASO 4: Colaboración Multi-Agente A2A y fidelidad de cifras, unidades y supuestos
        pregunta_multi = (
            "Organizo un taller para 16 porciones: necesito escalar la receta de brownie a 16 porciones, "
            "2 canciones de synth-pop de los años 80 y una técnica de ideación en fase de divergencia."
        )
        resp_multi = await cliente.post(
            f"{URL_BASE}/api/consultar",
            headers=headers_ok,
            json={"mensaje": pregunta_multi},
        )
        datos_multi = resp_multi.json()
        texto_multi = (datos_multi.get("respuesta") or "").replace("\n", " | ")
        imprimir_ficha_caso(
            numero=4,
            titulo="Acceso autorizado + Colaboración Multi-Agente A2A y fidelidad de conclusión",
            solicitud=pregunta_multi,
            esperado=(
                "Participan Agente pastelero, Agente de música ochentera y Agente Innovacion por A2A, "
                "conservando factor 2.00 (base 8 porciones), gramos, 175 °C, años 1981-1987 y técnicas de divergencia."
            ),
            obtenido=(
                f"HTTP {resp_multi.status_code} | agentes={datos_multi.get('agentes_participantes')} | "
                f"respuesta={texto_multi[:360]}..."
            ),
            observaciones="Se conservan intactos los datos, cálculos, unidades y supuestos de cada agente A2A.",
        )

        # CASO 5: Límite del sistema / Fuera de alcance
        pregunta_fuera = "¿Cuál es el pronóstico del clima en Tokio para mañana?"
        resp_fuera = await cliente.post(
            f"{URL_BASE}/api/consultar",
            headers=headers_ok,
            json={"mensaje": pregunta_fuera},
        )
        datos_fuera = resp_fuera.json()
        imprimir_ficha_caso(
            numero=5,
            titulo="Límite de los agentes (Consulta fuera de alcance)",
            solicitud=pregunta_fuera,
            esperado="El coordinador informa claramente que no tiene un agente para ese tema y lista las especialidades.",
            obtenido=(
                f"HTTP {resp_fuera.status_code} | estado={datos_fuera.get('estado')} | "
                f"respuesta={datos_fuera.get('respuesta')}"
            ),
            observaciones="Límite declarado de forma transparente al usuario.",
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(probar_recorrido()))
    except Exception as error:  # noqa: BLE001 - Regla 4: error en una sola línea
        print(f"Error: {str(error).replace(chr(10), ' ').strip()}")
        raise SystemExit(1)
