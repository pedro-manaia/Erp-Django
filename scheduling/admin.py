from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id","titulo","inicio","fim","cliente","local")
    list_filter = ("inicio","fim")
    search_fields = ("titulo","descricao","local")
