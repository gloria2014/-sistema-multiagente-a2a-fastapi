"""Arranque unificado de todos los agentes A2A y del Servicio FastAPI + Canal Web.

Útil tanto para despliegue en la nube (Microsoft Azure App Service / Container Apps)
como para iniciar todo el ecosistema local con un solo comando:
    python scripts/iniciar_nube.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

SERVICIOS_INTERNOS = [
    ("Agente Pastelero", "src.agente_pastelero.server:app", "8002"),
    ("Agente Música Ochentera", "src.agente_musica.server:app", "8003"),
    ("Agente Innovación", "src.agente_innovacion.server:app", "8004"),
    ("Coordinador A2A", "src.coordinador.server:app", "8007"),
]


def main() -> int:
    procesos: list[subprocess.Popen] = []
    ejecutable = sys.executable

    puerto_principal = os.getenv("PORT") or os.getenv("WEBSITES_PORT") or os.getenv("PUERTO_WEB") or "8000"
    host_principal = os.getenv("HOST_WEB", "0.0.0.0")

    # Si estamos corriendo en Azure App Service (WEBSITE_SITE_NAME está definido),
    # arrancamos en un único proceso liviano para evitar agotar RAM/CPU del plan de Azure (503).
    if os.getenv("WEBSITE_SITE_NAME"):
        print(
            f"[AZURE] Iniciando Servicio FastAPI + Agentes A2A en modo nube ({host_principal}:{puerto_principal})..."
        )
        os.chdir(str(RAIZ))
        if str(RAIZ) not in sys.path:
            sys.path.insert(0, str(RAIZ))
        import uvicorn
        from scripts.web import app as app_fastapi

        uvicorn.run(app_fastapi, host=host_principal, port=int(puerto_principal))
        return 0

    try:
        for nombre, modulo, puerto in SERVICIOS_INTERNOS:
            print(f"[ARRANQUE] Iniciando {nombre} en 127.0.0.1:{puerto}...")
            proc = subprocess.Popen(
                [
                    ejecutable,
                    "-m",
                    "uvicorn",
                    modulo,
                    "--host",
                    "127.0.0.1",
                    "--port",
                    puerto,
                ],
                cwd=str(RAIZ),
            )
            procesos.append(proc)
            time.sleep(1.2)

        # Esperar unos segundos para que los agentes publiquen sus Agent Cards
        time.sleep(2.0)

        puerto_principal = os.getenv("PORT") or os.getenv("PUERTO_WEB") or "8000"
        host_principal = os.getenv("HOST_WEB", "0.0.0.0")
        print(
            f"[ARRANQUE] Iniciando Servicio FastAPI Protegido + Canal Web en {host_principal}:{puerto_principal}..."
        )

        proc_web = subprocess.Popen(
            [
                ejecutable,
                "-m",
                "uvicorn",
                "scripts.web:app",
                "--host",
                host_principal,
                "--port",
                str(puerto_principal),
            ],
            cwd=str(RAIZ),
        )
        procesos.append(proc_web)
        return proc_web.wait()

    except KeyboardInterrupt:
        print("\n[DETENCION] Cerrando todos los servidores A2A...")
        return 0
    finally:
        for proc in reversed(procesos):
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:  # noqa: BLE001
                    proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
