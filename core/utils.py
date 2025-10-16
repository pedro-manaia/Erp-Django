from django.contrib.auth.models import Group
from typing import Iterable, List

# Módulos oficiais do portal
MODULE_KEYS: List[str] = [
    "vendas",
    "financeiro",
    "fiscal",
    "configuracao",
    "funcionario",
    "estoque",
]

def has_module(user, module: str) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return user.groups.filter(name=f"mod_{module}").exists()

def ensure_module_groups():
    """Garante que todos os grupos mod_* existem e retorna {key: Group}."""
    mapping = {}
    for key in MODULE_KEYS:
        grp, _ = Group.objects.get_or_create(name=f"mod_{key}")
        mapping[key] = grp
    return mapping

def get_user_module_keys(user) -> List[str]:
    """Retorna quais chaves de módulo o usuário possui (via grupos mod_*)."""
    keys = []
    for key in MODULE_KEYS:
        if user.groups.filter(name=f"mod_{key}").exists():
            keys.append(key)
    return keys

def set_user_module_keys(user, keys: Iterable[str]):
    """Define os módulos do usuário (limpa os mod_* conhecidos e adiciona os informados)."""
    keys = set(keys or [])
    groups = ensure_module_groups()
    # Remove somente grupos de módulo conhecidos
    user.groups.remove(*[groups[k] for k in MODULE_KEYS if user.groups.filter(name=f"mod_{k}").exists()])
    # Adiciona os solicitados
    for k in keys:
        if k in groups:
            user.groups.add(groups[k])
    user.save()
