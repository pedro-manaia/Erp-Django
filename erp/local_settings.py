# Overrides de desenvolvimento para acesso pela rede local
DEBUG = True
ALLOWED_HOSTS = ["*"]  # DEV APENAS
# Se for acessar por nome de host/DOMÍNIO com http, e o Django reclamar de CSRF,
# adicione aqui, ex.: CSRF_TRUSTED_ORIGINS = ["http://192.168.0.10:8000"]


# --- Força criação de tabelas SEM migrações para apps core ---
try:
    MIGRATION_MODULES
except NameError:
    MIGRATION_MODULES = {}

MIGRATION_MODULES.update({
    'admin': None,
    'auth': None,
    'contenttypes': None,
    'sessions': None,
    'messages': None,
})
