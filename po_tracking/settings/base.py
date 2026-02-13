import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

try:
    import environ  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    environ = None

if environ:
    env = environ.Env()
    environ.Env.read_env(BASE_DIR / ".env")
else:  # pragma: no cover
    class _FallbackEnv:
        def __call__(self, key: str, default=None):
            return os.getenv(key, default)

        def bool(self, key: str, default: bool = False) -> bool:
            raw = os.getenv(key)
            if raw is None:
                return default
            return raw.lower() in {"1", "true", "yes", "on"}

    env = _FallbackEnv()

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-key-change-me")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "apps.core",
    "apps.accounts",
    "apps.po",
    "apps.ingestion",
    "apps.batches",
    "apps.audit",
    "apps.admin_portal",
    "apps.exports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "po_tracking.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "po_tracking.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": env("DB_DEFAULT_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DB_DEFAULT_NAME", default=str(BASE_DIR / "db.sqlite3")),
        "HOST": env("DB_DEFAULT_HOST", default=""),
        "PORT": env("DB_DEFAULT_PORT", default=""),
        "USER": env("DB_DEFAULT_USER", default=""),
        "PASSWORD": env("DB_DEFAULT_PASSWORD", default=""),
    },
    "erp": {
        "ENGINE": env("DB_ERP_ENGINE", default="mssql"),
        "NAME": env("DB_ERP_NAME", default=""),
        "HOST": env("DB_ERP_HOST", default=""),
        "PORT": env("DB_ERP_PORT", default=""),
        "USER": env("DB_ERP_USER", default=""),
        "PASSWORD": env("DB_ERP_PASSWORD", default=""),
        "OPTIONS": {
            "driver": env("DB_ERP_ODBC_DRIVER", default="ODBC Driver 18 for SQL Server"),
        },
    },
}

DATABASE_ROUTERS = ["apps.ingestion.router.DatabaseRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
