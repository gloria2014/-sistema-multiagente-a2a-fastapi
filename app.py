"""Punto de entrada ASGI/WSGI en la raíz para compatibilidad automática con Azure App Service (Oryx/Gunicorn)."""

from __future__ import annotations

from scripts.web import app

__all__ = ["app"]
