"""Manejador de excepciones DRF con mensajes claros."""
from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        data = {"ok": False, "error": _extract_message(response.data)}
        if isinstance(response.data, dict) and any(
            isinstance(v, (list, dict)) for v in response.data.values()
        ):
            data["campos"] = response.data
        response.data = data
        return response

    logger.exception("Error no controlado: %s", exc)
    return Response(
        {"ok": False, "error": "Error interno del servidor. Intente de nuevo o contacte soporte."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(data) -> str:
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        parts = []
        for key, val in data.items():
            if isinstance(val, list):
                parts.append(f"{key}: {', '.join(str(v) for v in val)}")
            else:
                parts.append(f"{key}: {val}")
        return "; ".join(parts) if parts else "Solicitud inválida"
    if isinstance(data, list):
        return "; ".join(str(x) for x in data)
    return str(data)
