from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id","nome","cpf_cnpj","email","telefone","ativo","criado_em")
    search_fields = ("nome","razao_social","cpf_cnpj","email")
    list_filter = ("ativo","uf","cidade")
