"""Pruebas unitarias y de integración local para control de acceso, entradas y datos faltantes."""

from __future__ import annotations

import os
import asyncio

from fastapi.testclient import TestClient

os.environ.setdefault("TOKEN_ACCESO", "token-prueba-pytest-123")

from scripts.web import app
from src.coordinador.graph import _detectar_datos_faltantes


cliente_http = TestClient(app)


def test_salud_publico() -> None:
    """El endpoint /salud debe responder 200 sin requerir token."""
    respuesta = cliente_http.get("/salud")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["ok"] is True
    assert datos["acceso_protegido"] is True


def test_acceso_rechazado_sin_token() -> None:
    """Una solicitud sin token debe ser rechazada con HTTP 401."""
    respuesta = cliente_http.post("/api/consultar", json={"mensaje": "receta de brownie"})
    assert respuesta.status_code == 401
    assert "Acceso rechazado" in respuesta.json()["detail"]


def test_acceso_rechazado_token_invalido() -> None:
    """Una solicitud con token incorrecto debe ser rechazada con HTTP 401."""
    respuesta = cliente_http.post(
        "/api/consultar",
        headers={"Authorization": "Bearer clave-incorrecta"},
        json={"mensaje": "receta de brownie"},
    )
    assert respuesta.status_code == 401
    assert "no es válido" in respuesta.json()["detail"]


def test_entrada_invalida_mensaje_vacio() -> None:
    """Con token válido pero mensaje vacío debe devolver HTTP 400."""
    token = os.environ["TOKEN_ACCESO"]
    respuesta = cliente_http.post(
        "/api/consultar",
        headers={"Authorization": f"Bearer {token}"},
        json={"mensaje": "   "},
    )
    assert respuesta.status_code == 400
    assert "Entrada inválida" in respuesta.json()["detail"]


def test_detector_datos_faltantes_escalado() -> None:
    """Si se pide escalar una receta sin indicar porciones, solicita el dato faltante."""
    aviso = _detectar_datos_faltantes("Por favor escala la receta de brownie")
    assert aviso is not None
    assert "porciones" in aviso.lower()

    sin_aviso = _detectar_datos_faltantes("Escala la receta de brownie para 16 porciones")
    assert sin_aviso is None
