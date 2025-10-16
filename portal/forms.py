from django import forms
from django.contrib.auth import get_user_model
from django.forms import CheckboxSelectMultiple
from core.utils import MODULE_KEYS, get_user_module_keys

User = get_user_model()

MODULE_LABELS = {
    "vendas": "Vendas",
    "financeiro": "Financeiro",
    "fiscal": "Fiscal",
    "configuracao": "Configuração",
    "funcionario": "Funcionário",
    "estoque": "Estoque",
}

class ModulesField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        choices = [(k, MODULE_LABELS.get(k, k.title())) for k in MODULE_KEYS]
        kwargs.setdefault("choices", choices)
        kwargs.setdefault("required", False)
        kwargs.setdefault("widget", CheckboxSelectMultiple)
        super().__init__(*args, **kwargs)

class UserBaseForm(forms.ModelForm):
    modules = ModulesField(label="Módulos liberados", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "modules"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["modules"].initial = get_user_module_keys(self.instance)

class UserCreateForm(UserBaseForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="Confirme a senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta(UserBaseForm.Meta):
        fields = UserBaseForm.Meta.fields + ["password1", "password2"]

    def clean(self):
        data = super().clean()
        p1 = data.get("password1")
        p2 = data.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("As senhas não conferem.")
            if len(p1) < 6:
                raise forms.ValidationError("Use pelo menos 6 caracteres na senha.")
        return data

class UserEditForm(UserBaseForm):
    pass

class UserPasswordForm(forms.Form):
    password1 = forms.CharField(label="Nova senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="Confirme a nova senha", widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        data = super().clean()
        if data.get("password1") != data.get("password2"):
            raise forms.ValidationError("As senhas não conferem.")
        if len(data.get("password1", "")) < 6:
            raise forms.ValidationError("Use pelo menos 6 caracteres na senha.")
        return data


from core.models import SystemConfig

class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = ["session_expire_on_close", "idle_timeout_minutes"]
        labels = {
            "session_expire_on_close": "Pedir login ao fechar navegador",
            "idle_timeout_minutes": "Tempo de inatividade permitido (minutos)",
        }
        widgets = {
            "session_expire_on_close": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "idle_timeout_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 1440}),
        }
