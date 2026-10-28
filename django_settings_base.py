"""Factory de settings Django para microservicios Fisiocloud."""
from __future__ import annotations

import os
from pathlib import Path


def _csrf_trusted_origins() -> list[str]:
    defaults = (
        "http://localhost:8089,http://127.0.0.1:8089,"
        "http://localhost:8000,http://127.0.0.1:8000"
    )
    raw = os.environ.get("CSRF_TRUSTED_ORIGINS", defaults)
    origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    front = (os.environ.get("FRONTEND_URL") or "").strip().rstrip("/")
    if front and front not in origins:
        origins.append(front)
    return origins


def build_settings(
    base_dir: Path,
    db_name: str,
    service_apps: list[str] | None = None,
    extra_middleware: list[str] | None = None,
):
    """Retorna un dict con settings; el módulo settings.py hace globals().update(...)."""
    secret = os.environ.get("DJANGO_SECRET_KEY", f"dev-secret-{db_name}")
    debug = os.environ.get("DJANGO_DEBUG", "1") == "1"
    apps = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "rest_framework",
        "corsheaders",
        "core",
    ]
    if service_apps:
        apps.extend(service_apps)

    middleware = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
    if extra_middleware:
        middleware.extend(extra_middleware)

    return {
        "BASE_DIR": base_dir,
        "SECRET_KEY": secret,
        "DEBUG": debug,
        "ALLOWED_HOSTS": ["*"],
        # Necesario cuando se entra por nginx / dominio público
        "CSRF_TRUSTED_ORIGINS": _csrf_trusted_origins(),
        "CSRF_COOKIE_SECURE": False,
        "SESSION_COOKIE_SECURE": False,
        "INSTALLED_APPS": apps,
        "MIDDLEWARE": middleware,
        "ROOT_URLCONF": "config.urls",
        "TEMPLATES": [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [base_dir / "templates"],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            }
        ],
        "WSGI_APPLICATION": "config.wsgi.application",
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": db_name,
                "USER": os.environ.get("DB_USER", "root"),
                "PASSWORD": os.environ.get("DB_PASSWORD", "root"),
                "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
                "PORT": os.environ.get("DB_PORT", "3309"),
                "OPTIONS": {"charset": "utf8mb4"},
            }
        },
        "AUTH_PASSWORD_VALIDATORS": [
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ],
        "LANGUAGE_CODE": "es-co",
        "TIME_ZONE": "America/Bogota",
        "USE_I18N": True,
        "USE_TZ": True,
        "STATIC_URL": "/static/",
        "STATICFILES_DIRS": [base_dir / "static"] if (base_dir / "static").exists() else [],
        "STATIC_ROOT": base_dir / "staticfiles",
        "MEDIA_URL": "/media/",
        # Compartido. Preferir MEDIA_ROOT en env; si no, <raíz deploy>/media
        "MEDIA_ROOT": (
            Path(os.environ["MEDIA_ROOT"])
            if os.environ.get("MEDIA_ROOT")
            else (base_dir.parent / "media")
        ),
        "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
        "CORS_ALLOW_ALL_ORIGINS": True,
        "CORS_ALLOW_CREDENTIALS": True,
        "REST_FRAMEWORK": {
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "shared.jwt_auth.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "EXCEPTION_HANDLER": "shared.exceptions.custom_exception_handler",
            "DEFAULT_RENDERER_CLASSES": [
                "rest_framework.renderers.JSONRenderer",
            ],
        },
        "JWT_SECRET": os.environ.get("JWT_SECRET", "fisiocloud-dev-secret-change-me"),
        # Dominio público (navegador). Ej.: https://app-fisiocloudia.duckdns.org
        "FRONTEND_URL": os.environ.get("FRONTEND_URL", "http://127.0.0.1:8089").rstrip("/"),
        "SEGURIDAD_URL": os.environ.get("SEGURIDAD_URL", "http://127.0.0.1:8101"),
        "SUSCRIPCION_URL": os.environ.get("SUSCRIPCION_URL", "http://127.0.0.1:8102"),
        "INFO_MEDICA_URL": os.environ.get("INFO_MEDICA_URL", "http://127.0.0.1:8103"),
        "AGENDAMIENTO_URL": os.environ.get("AGENDAMIENTO_URL", "http://127.0.0.1:8104"),
        "PARAMETRIZACION_URL": os.environ.get("PARAMETRIZACION_URL", "http://127.0.0.1:8105"),
        "TRATAMIENTO_CASA_URL": os.environ.get("TRATAMIENTO_CASA_URL", "http://127.0.0.1:8106"),
        "SOPORTE_URL": os.environ.get("SOPORTE_URL", "http://127.0.0.1:8107"),
        "PROCESOS_AUTOMATICOS_URL": os.environ.get(
            "PROCESOS_AUTOMATICOS_URL", "http://127.0.0.1:8108"
        ),
        "ASISTENTE_VOZ_URL": os.environ.get(
            "ASISTENTE_VOZ_URL", "http://127.0.0.1:8109"
        ),
    }
