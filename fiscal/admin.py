from django.contrib import admin
from .models import FiscalDocument

@admin.register(FiscalDocument)
class FiscalDocumentAdmin(admin.ModelAdmin):
    list_display = ("id","tipo","serie","numero","situacao","criado_em")
    list_filter = ("tipo","situacao")
    search_fields = ("chave","provider_id")
