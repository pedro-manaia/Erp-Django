from django.contrib import admin
from django.utils.html import format_html
from django.core.cache import cache
from .models import Announcement

CACHE_KEY = "global_announcement"

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("short_message","level","active","expires_at","created_at")
    list_filter = ("level","active","created_at")
    search_fields = ("message",)
    actions = ["ativar","desativar","publicar_no_cache","limpar_aviso_cache"]

    def short_message(self, obj):
        return (obj.message[:60] + "…") if len(obj.message) > 60 else obj.message
    short_message.short_description = "Mensagem"

    @admin.action(description="Ativar selecionados")
    def ativar(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Desativar selecionados")
    def desativar(self, request, queryset):
        queryset.update(active=False)

    @admin.action(description="Publicar (cache global) o mais recente ativo")
    def publicar_no_cache(self, request, queryset):
        obj = queryset.filter(active=True).order_by("-created_at").first()
        if obj:
            cache.set(CACHE_KEY, {
                "message": obj.message,
                "level": obj.level,
                "expires_at": obj.expires_at.isoformat() if obj.expires_at else None,
            }, timeout=24*3600)
            self.message_user(request, "Aviso publicado no cache.")
        else:
            self.message_user(request, "Nenhum aviso ativo dentre os selecionados.", level="warning")

    @admin.action(description="Limpar aviso global (cache)")
    def limpar_aviso_cache(self, request, queryset):
        cache.delete(CACHE_KEY)
        self.message_user(request, "Aviso global limpo do cache.")
