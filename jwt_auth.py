"""Autenticación JWT compartida entre microservicios."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from rest_framework import authentication, exceptions

JWT_SECRET = os.environ.get("JWT_SECRET", "fisiocloud-dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_HOURS = int(os.environ.get("JWT_ACCESS_HOURS", "12"))
JWT_REFRESH_DAYS = int(os.environ.get("JWT_REFRESH_DAYS", "7"))


def create_access_token(payload: dict[str, Any]) -> str:
    data = payload.copy()
    data["type"] = "access"
    data["exp"] = datetime.now(timezone.utc) + timedelta(hours=JWT_ACCESS_HOURS)
    data["iat"] = datetime.now(timezone.utc)
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(payload: dict[str, Any]) -> str:
    data = {"user_id": payload.get("user_id"), "doc": payload.get("doc"), "type": "refresh"}
    data["exp"] = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_DAYS)
    data["iat"] = datetime.now(timezone.utc)
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed("Token expirado") from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed("Token inválido") from exc


class JWTUser:
    is_authenticated = True

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.id = payload.get("user_id")
        self.doc = payload.get("doc")
        self.rol = payload.get("rol")
        self.nombre = payload.get("nombre", "")
        self.apellido = payload.get("apellido", "")
        self.email = payload.get("email", "")

    @property
    def pk(self):
        return self.id


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).decode("utf-8")
        if not auth:
            token = request.COOKIES.get("access_token") or request.session.get("access_token")
            if not token:
                return None
        else:
            parts = auth.split()
            if len(parts) != 2 or parts[0] != self.keyword:
                return None
            token = parts[1]

        payload = decode_token(token)
        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Se requiere access token")
        return (JWTUser(payload), token)


def api_error(message: str, campos: dict | None = None, status: int = 400):
    body: dict[str, Any] = {"ok": False, "error": message}
    if campos:
        body["campos"] = campos
    return body, status


def api_ok(data: Any = None, message: str = "OK"):
    body: dict[str, Any] = {"ok": True, "message": message}
    if data is not None:
        body["data"] = data
    return body
