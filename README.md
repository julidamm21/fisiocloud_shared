# Fisiocloud — shared

Utilidades compartidas entre microservicios Django.

| Módulo | Uso |
|---|---|
| `jwt_auth.py` | JWT (crear/decodificar), `JWTAuthentication`, `api_ok` / `api_error` |
| `django_settings_base.py` | `build_settings()` común a todos los backends |
| `db.py` | Helpers de conexión / entorno de BD |
| `exceptions.py` | Excepciones HTTP compartidas |

## Uso

Cada backend incluye (o copia) este paquete como `shared/` en su `PYTHONPATH`.

El `JWT_SECRET` debe ser el mismo en todos los servicios.
