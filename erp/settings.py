from pathlib import Path
import os
import environ

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Env
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Segurança / Debug
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key-change-me")
DEBUG = env.bool("DEBUG", default=True)

# ---- Hosts e CSRF ----
_default_hosts = ["localhost", "127.0.0.1", "[::1]", "manaia.ddns.net"]
_env_hosts = [h.strip() for h in env("ALLOWED_HOSTS", default="").split(",") if h.strip()]
ALLOWED_HOSTS = ["*"] # list(dict.fromkeys(_default_hosts + _env_hosts))

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3100",
    "http://127.0.0.1:3100",
    "http://manaia.ddns.net:3100",
    "https://localhost:3100",
    "https://127.0.0.1:3100",
    "https://manaia.ddns.net:3100",
]

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceiros
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    # Apps do projeto
    "core",
    "portal",
    "customers",
    "finance",
    "fiscal",
    "inventory",
    "products",
    "rental",
    "sales",
    "scheduling",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.LoginRequiredMiddleware",
    'core.active_devices.middleware.ActiveDevicesMiddleware',
]

ROOT_URLCONF = "erp.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "portal" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "erp.wsgi.application"

# ---- Banco de dados (ÚNICO arquivo SQLite: db.sql) ----
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sql",
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Locale
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

# Uploads
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django / Projeto
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Redirecionamentos pós login/logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # expira ao fechar o navegador

# DRF + Spectacular
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "ERP API",
    "VERSION": "1.0.0",
}