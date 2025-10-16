from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

@admin.action(description="Ativar usuários selecionados")
def make_active(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    messages.success(request, f"{updated} usuário(s) ativado(s).")

@admin.action(description="Inativar usuários selecionados")
def make_inactive(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    messages.success(request, f"{updated} usuário(s) inativado(s).")

class UserAdmin(DjangoUserAdmin):
    # Mostra a coluna 'Ativo?' e filtros práticos
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser", "last_login")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    ordering = ("username",)
    actions = [make_active, make_inactive]

    # Bloqueia exclusão
    def has_delete_permission(self, request, obj=None):
        return False

    # Remove "Delete selected users"
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


from django.contrib import admin
from .models import SystemConfig

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('id','session_expire_on_close','idle_timeout_minutes','updated_at')
