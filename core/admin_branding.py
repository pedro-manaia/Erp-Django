from django.conf import settings
from django.contrib import admin

site_name = getattr(settings, "SITE_NAME", "Admin")
admin.site.site_header = f"{site_name} — Admin"
admin.site.site_title = f"{site_name}"
admin.site.index_title = "Painel de Controle"
