from .base import *  # noqa

DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS").split(",") if h.strip()]

DATABASES["default"].update(
    {
        "ENGINE": env("DB_DEFAULT_ENGINE", default="mssql"),
        "NAME": env("DB_DEFAULT_NAME", default="po_tracking_app"),
        "HOST": env("DB_DEFAULT_HOST", default=""),
        "PORT": env("DB_DEFAULT_PORT", default="1433"),
        "USER": env("DB_DEFAULT_USER", default=""),
        "PASSWORD": env("DB_DEFAULT_PASSWORD", default=""),
        "OPTIONS": {
            "driver": env("DB_DEFAULT_ODBC_DRIVER", default="ODBC Driver 18 for SQL Server"),
        },
    }
)

DATABASES["erp"].update(
    {
        "ENGINE": env("DB_ERP_ENGINE", default="mssql"),
        "NAME": env("DB_ERP_NAME", default="supplier_erp"),
        "HOST": env("DB_ERP_HOST", default=""),
        "PORT": env("DB_ERP_PORT", default="1433"),
        "USER": env("DB_ERP_USER", default=""),
        "PASSWORD": env("DB_ERP_PASSWORD", default=""),
        "OPTIONS": {
            "driver": env("DB_ERP_ODBC_DRIVER", default="ODBC Driver 18 for SQL Server"),
        },
    }
)
