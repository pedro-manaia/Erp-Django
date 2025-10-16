import os, sys, pathlib
from decimal import Decimal

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp.settings")

import django
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from customers.models import Customer
from products.models import Product
from finance.models import ExpenseCategory

def log(msg):
    print(f"[seed] {msg}")

def ensure_user():
    User = get_user_model()
    username = os.environ.get("ERP_DEFAULT_USER", "pedro")
    password = os.environ.get("ERP_DEFAULT_PASS", "pedro")
    email = "pedro@example.com"
    u, created = User.objects.get_or_create(username=username, defaults={"email": email})
    u.is_staff = True
    u.is_superuser = True
    u.set_password(password)
    u.save()
    log(("Usuario criado: " if created else "Usuario atualizado: ") + f"{username}/{password}")

def ensure_customers():
    demos = [
        dict(tipo="J", nome="Cliente Teste LTDA", razao_social="Cliente Teste LTDA", cpf_cnpj="12.345.678/0001-90",
             email="financeiro@clienteteste.com.br", telefone="(61) 3333-0001", whatsapp="(61) 9 8888-0001",
             endereco="Av. Central, 100", cidade="Brasília", uf="DF", cep="70000-000"),
        dict(tipo="F", nome="Maria da Silva", razao_social="", cpf_cnpj="123.456.789-09",
             email="maria.silva@example.com", telefone="(61) 4002-8922", whatsapp="(61) 9 9999-1111",
             endereco="Rua das Flores, 50", cidade="Brasília", uf="DF", cep="70000-001"),
        dict(tipo="J", nome="Fornecedor Exemplo ME", razao_social="Fornecedor Exemplo ME", cpf_cnpj="98.765.432/0001-10",
             email="contato@fornecedor.me", telefone="(61) 3333-0002", whatsapp="(61) 9 8888-0002",
             endereco="SIA Trecho 1, Lote 2", cidade="Brasília", uf="DF", cep="70000-002"),
    ]
    for d in demos:
        obj, created = Customer.objects.get_or_create(cpf_cnpj=d["cpf_cnpj"], defaults=d)
        if not created:
            for k, v in d.items():
                setattr(obj, k, v)
            obj.save()
        log(("Cliente criado: " if created else "Cliente atualizado: ") + obj.nome)

def ensure_products():
    demos = [
        dict(sku="TST-001", nome="Copo Personalizado 300ml", descricao="Copo plástico para festas", preco_venda=Decimal("2.50"), custo=Decimal("1.00"), unidade="UN", estoque_atual=500),
        dict(sku="TST-002", nome='Balão Metalizado 18"', descricao="Balão decorativo", preco_venda=Decimal("6.90"), custo=Decimal("3.50"), unidade="UN", estoque_atual=200),
        dict(sku="TST-003", nome="Toalha de Mesa TNT", descricao="Toalha descartável 1,4x2,2m", preco_venda=Decimal("8.00"), custo=Decimal("4.00"), unidade="UN", estoque_atual=150),
        dict(sku="LOC-001", nome="Cadeira Branca (locação)", descricao="Cadeira para eventos", preco_venda=Decimal("15.00"), custo=Decimal("0.00"), unidade="UN", estoque_atual=50, disponivel_para_locacao=True, valor_diaria=Decimal("5.00"), caucao=Decimal("50.00")),
        dict(sku="LOC-002", nome="Mesa Plástica (locação)", descricao="Mesa redonda", preco_venda=Decimal("25.00"), custo=Decimal("0.00"), unidade="UN", estoque_atual=20, disponivel_para_locacao=True, valor_diaria=Decimal("8.00"), caucao=Decimal("80.00")),
    ]
    for d in demos:
        obj, created = Product.objects.get_or_create(sku=d["sku"], defaults=d)
        if not created:
            for k, v in d.items():
                setattr(obj, k, v)
            obj.save()
        log(("Produto criado: " if created else "Produto atualizado: ") + f"{obj.sku} - {obj.nome}")

def ensure_categories():
    root_ops, _ = ExpenseCategory.objects.get_or_create(name="Operacional", parent=None)
    root_fin, _ = ExpenseCategory.objects.get_or_create(name="Financeiro", parent=None)
    root_imp, _ = ExpenseCategory.objects.get_or_create(name="Impostos", parent=None)

    for name in ["Aluguel", "Energia", "Água", "Internet", "Limpeza"]:
        ExpenseCategory.objects.get_or_create(name=name, parent=root_ops)

    for name in ["Tarifas Bancárias", "Juros/Multa", "Descontos Concedidos"]:
        ExpenseCategory.objects.get_or_create(name=name, parent=root_fin)

    for name in ["ISS", "ICMS ST", "PIS/COFINS"]:
        ExpenseCategory.objects.get_or_create(name=name, parent=root_imp)

    log("Categorias e subcategorias OK")

def ensure_revenue_categories():
    root_rec, _ = ExpenseCategory.objects.get_or_create(name="Receitas", parent=None)
    for name in ["Vendas", "Serviços", "Receitas Financeiras", "Outras Receitas"]:
        ExpenseCategory.objects.get_or_create(name=name, parent=root_rec)

@transaction.atomic
def main():
    ensure_user()
    ensure_customers()
    ensure_products()
    ensure_categories()
    ensure_revenue_categories()
    ensure_accounts()
    ensure_payment_methods()
    ensure_sample_documents()
    log("Seed de dados fictícios concluído.")


# === Adições: contas, formas de pagamento e CR/CP de exemplo ===
from finance import services as fin_svc
from finance.models import FinanceDocument
from django.utils import timezone
from datetime import timedelta

def ensure_accounts():
    try:
        items = fin_svc.list_accounts()
    except Exception:
        items = []
    if items:
        log("Contas já existem; mantendo.")
        return
    fin_svc.create_account("Caixa", "CAIXA")
    fin_svc.create_account("Banco do Brasil", "BANCO")
    fin_svc.create_account("Carteira PIX", "CARTEIRA")
    log("Contas padrão criadas.")

def ensure_payment_methods():
    try:
        items = fin_svc.list_payment_methods()
    except Exception:
        items = []
    if items:
        log("Formas de pagamento já existem; mantendo.")
        return
    fin_svc.create_payment_method("Dinheiro", "DINHEIRO")
    fin_svc.create_payment_method("Pix", "PIX")
    fin_svc.create_payment_method("Cartão de Crédito", "CREDITO")
    fin_svc.create_payment_method("Boleto", "BOLETO")
    log("Formas de pagamento padrão criadas.")

def _pick_category(name_like: str):
    # Busca categoria por nome (case-insensitive), retorna primeira que casar.
    try:
        return ExpenseCategory.objects.filter(name__iexact=name_like).first() or ExpenseCategory.objects.filter(name__icontains=name_like).first()
    except Exception:
        return None

def ensure_sample_documents():
    # CR: usa categoria em 'Vendas' (Receitas)
    cat_cr = _pick_category("Vendas") or _pick_category("Receitas")
    # CP: usa categoria 'Despesas Gerais' (Despesas/Operacional)
    cat_cp = _pick_category("Despesas Gerais") or _pick_category("Operacional") or _pick_category("Despesas")
    today = timezone.now().date()
    # Evita duplicar: se já houver algum documento, não cria
    if FinanceDocument.objects.exists():
        log("Documentos financeiros já existem; mantendo.")
        return
    # CR de exemplo (2 parcelas)
    cat_id = None
    cat_parent_id = None
    if cat_cr:
        if getattr(cat_cr, "parent_id", None):
            cat_parent_id = cat_cr.parent_id
            cat_id = cat_cr.id
        else:
            cat_parent_id = cat_cr.id
            cat_id = None
    fin_svc.criar_documento_manual(
        tipo="CR",
        descricao="CR Demo - Venda inicial",
        valor_total=Decimal("150.00"),
        parcelas=2,
        primeiro_vencimento=today,
        intervalo_dias=30,
        parceiro_nome="Cliente Demo",
        categoria_id=cat_id,
        categoria_parent_id=cat_parent_id,
    )
    # CP de exemplo (1 parcela)
    cat_id = None
    cat_parent_id = None
    if cat_cp:
        if getattr(cat_cp, "parent_id", None):
            cat_parent_id = cat_cp.parent_id
            cat_id = cat_cp.id
        else:
            cat_parent_id = cat_cp.id
            cat_id = None
    fin_svc.criar_documento_manual(
        tipo="CP",
        descricao="CP Demo - Despesa inicial",
        valor_total=Decimal("80.00"),
        parcelas=1,
        primeiro_vencimento=today + timedelta(days=7),
        intervalo_dias=30,
        parceiro_nome="Fornecedor Demo",
        categoria_id=cat_id,
        categoria_parent_id=cat_parent_id,
    )
    log("CR/CP de exemplo criados.")


if __name__ == "__main__":
    main()
