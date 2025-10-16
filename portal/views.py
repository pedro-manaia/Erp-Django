from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, FormView
from core.models import SystemConfig
from core.utils import has_module, set_user_module_keys, ensure_module_groups

User = get_user_model()

class ModuleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    module = None
    raise_exception = True
    def test_func(self):
        return has_module(self.request.user, self.module)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "portal/home.html"

# ---- Configuração: Usuários ----
from .forms import SystemConfigForm, UserCreateForm, UserEditForm, UserPasswordForm

class ConfigView(ModuleRequiredMixin, TemplateView):
    module = "configuracao"
    template_name = "portal/module_config.html"

class ConfigUsersListView(ModuleRequiredMixin, ListView):
    module = "configuracao"
    model = User
    template_name = "portal/config_users_list.html"
    paginate_by = 25

    def get_queryset(self):
        ensure_module_groups()  # garante grupos criados
        qs = User.objects.all().order_by("username")
        q = self.request.GET.get("q")
        active = self.request.GET.get("ativo")
        if q:
            qs = qs.filter(username__icontains=q) | qs.filter(email__icontains=q) | qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q)
        if active == "1":
            qs = qs.filter(is_active=True)
        elif active == "0":
            qs = qs.filter(is_active=False)
        return qs

class ConfigUserCreateView(ModuleRequiredMixin, CreateView):
    module = "configuracao"
    model = User
    form_class = UserCreateForm
    template_name = "portal/config_user_form.html"
    success_url = reverse_lazy("config_users")

    def get_form(self, form_class=None):
        ensure_module_groups()
        return super().get_form(form_class)

    def form_valid(self, form):
        resp = super().form_valid(form)
        pwd = form.cleaned_data.get("password1")
        if pwd:
            self.object.set_password(pwd)
            self.object.save()
        set_user_module_keys(self.object, form.cleaned_data.get("modules", []))
        messages.success(self.request, "Usuário criado com sucesso.")
        return resp

class ConfigUserEditView(ModuleRequiredMixin, UpdateView):
    module = "configuracao"
    model = User
    form_class = UserEditForm
    template_name = "portal/config_user_form.html"
    success_url = reverse_lazy("config_users")

    def get_form(self, form_class=None):
        ensure_module_groups()
        return super().get_form(form_class)

    def form_valid(self, form):
        resp = super().form_valid(form)
        set_user_module_keys(self.object, form.cleaned_data.get("modules", []))
        messages.success(self.request, "Usuário atualizado com sucesso.")
        return resp

class ConfigUserPasswordView(ModuleRequiredMixin, FormView):
    module = "configuracao"
    form_class = UserPasswordForm
    template_name = "portal/config_user_password.html"

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.user_obj.set_password(form.cleaned_data["password1"])
        self.user_obj.save()
        messages.success(self.request, f"Senha de '{self.user_obj.username}' atualizada.")
        return redirect("config_users")


class ConfigSystemView(LoginRequiredMixin, TemplateView):
    template_name = "portal/config_system.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cfg = SystemConfig.get_solo()
        ctx["form"] = SystemConfigForm(initial={
            "session_expire_on_close": cfg.session_expire_on_close,
            "idle_timeout_minutes": cfg.idle_timeout_minutes,
        })
        return ctx

    def post(self, request, *args, **kwargs):
        form = SystemConfigForm(request.POST)
        if form.is_valid():
            cfg = SystemConfig.get_solo()
            cfg.session_expire_on_close = form.cleaned_data["session_expire_on_close"]
            cfg.idle_timeout_minutes = form.cleaned_data["idle_timeout_minutes"]
            cfg.save()
            messages.success(request, "Configurações salvas com sucesso.")
            return redirect("config_system")
        messages.error(request, "Verifique os campos do formulário.")
        return self.get(request, *args, **kwargs)


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_then_login(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login")


# grava export de configuração em db.sql na raiz do projeto
import os
from django.conf import settings

def _write_config_sql(idle_minutes: int, session_expire_on_close: bool):
    """
    Gera um arquivo .sql de export em BASE_DIR, sem sobrescrever o arquivo do banco SQLite.
    Usa o nome seguro 'config_export.sql'. Se o DB estiver apontando para esse arquivo,
    cai para 'config_export_safe.sql'.
    """
    from django.conf import settings
    import os
    from pathlib import Path

    sql = f"""-- Export automático das configurações do sistema
-- Gerado pela aplicação (não editar manualmente)
CREATE TABLE IF NOT EXISTS system_kv (
  k VARCHAR(100) PRIMARY KEY,
  v VARCHAR(255)
);
INSERT INTO system_kv (k, v) VALUES
  ('idle_timeout_minutes', '{idle_minutes}'),
  ('session_expire_on_close', '{1 if session_expire_on_close else 0}')
ON CONFLICT(k) DO UPDATE SET v=excluded.v;
"""
    export_path = Path(settings.BASE_DIR) / "config_export.sql"

    try:
        db = getattr(settings, "DATABASES", {}).get("default", {})
        engine = (db.get("ENGINE") or "")
        name = db.get("NAME")
        if "sqlite" in engine and name:
            db_path = Path(name).resolve()
            if db_path == export_path.resolve():
                export_path = Path(settings.BASE_DIR) / "config_export_safe.sql"
    except Exception:
        # fallback simples
        pass

    with open(export_path, "w", encoding="utf-8") as f:
        f.write(sql)
