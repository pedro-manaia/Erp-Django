
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.module_loading import import_string

from products.models import Product
from customers.models import Customer
from finance.models import ExpenseCategory

def _env(name, default):
    try:
        return getattr(settings, name)
    except Exception:
        pass
    return os.environ.get(name, default)

import os

def seed_initial_data(stdout=None):
    """
    Cria dados iniciais quando o banco é criado do zero.
    É idempotente (usa get_or_create).
    - Usuário admin (ou conforme variáveis ADMIN_*)
    - Produto padrão
    - Cliente padrão
    - Categoria de despesa padrão
    """
    User = get_user_model()

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_email    = os.environ.get("ADMIN_EMAIL", "admin@local")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")

    created_objects = []

    with transaction.atomic():
        # 1) Usuário admin
        u, created = User.objects.get_or_create(
            username=admin_username,
            defaults={"email": admin_email, "is_staff": True, "is_superuser": True},
        )
        if created:
            u.set_password(admin_password)
            u.save(update_fields=["password"])
            created_objects.append(f"Usuario admin '{admin_username}'")
        else:
            # garante staff/superuser e senha conhecida (útil em DB novo parcial)
            changed = False
            if not u.is_staff:
                u.is_staff = True; changed=True
            if not u.is_superuser:
                u.is_superuser = True; changed=True
            if changed:
                u.save(update_fields=["is_staff","is_superuser"])

        # 2) Produto padrão
        prod, c2 = Product.objects.get_or_create(
            sku="P001",
            defaults={
                "nome": "Produto Padrão",
                "descricao": "Criado automaticamente",
                "preco_venda": 0,
                "custo": 0,
                "unidade": "UN",
                "estoque_atual": 0,
                "disponivel_para_locacao": False,
                "valor_diaria": 0,
                "caucao": 0,
                "ativo": True,
            },
        )
        if c2: created_objects.append("Produto Padrão (P001)")

        # 3) Cliente padrão
        cust, c3 = Customer.objects.get_or_create(
            cpf_cnpj="00000000000",
            defaults={
                "tipo": "F",
                "nome": "Cliente Padrão",
                "email": "cliente@local",
                "telefone": "",
                "whatsapp": "",
                "endereco": "",
                "cidade": "",
                "uf": "",
                "cep": "",
                "ativo": True,
            },
        )
        if c3: created_objects.append("Cliente Padrão (CPF 00000000000)")

        # 4) Categoria de despesa padrão
        cat, c4 = ExpenseCategory.objects.get_or_create(name="Despesas Gerais", parent=None)
        if c4: created_objects.append("Categoria de Despesa 'Despesas Gerais'")

    if stdout is not None:
        if created_objects:
            stdout.write("[seed] Criados: " + ", ".join(created_objects))
        else:
            stdout.write("[seed] Nada a criar (já existiam).")
