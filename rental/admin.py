from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id","produto","cliente","inicio","fim","quantidade","status","criado_em")
    list_filter = ("status","inicio","fim")
    search_fields = ("produto__nome","cliente__nome")
