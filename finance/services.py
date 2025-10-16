
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable, List, Optional, Dict

from django.db import transaction
from django.db.models import Case, When, Value, CharField, BooleanField, IntegerField
from django.utils import timezone

from .models import FinanceDocument, LedgerEntry, ExpenseCategory, Customer


# -----------------------------
# Helpers
# -----------------------------

def _to_date(d: Optional[str | date]) -> Optional[date]:
    if d is None:
        return None
    if isinstance(d, date):
        return d
    # Expecting 'YYYY-MM-DD'
    try:
        parts = [int(p) for p in str(d).split("-")]
        if len(parts) == 3:
            return date(parts[0], parts[1], parts[2])
    except Exception:
        pass
    return None


# -----------------------------
# Listagens (CR/CP)
# -----------------------------

def listar_lancamentos(tipo: str) -> List[LedgerEntry]:
    """
    Retorna os lançamentos (parcelas) de acordo com o tipo ('CR' ou 'CP'),
    com status dinâmico anotado:
      - "paid"     quando pago_em não é nulo
      - "overdue"  quando NÃO pago e vencimento < hoje
      - "open"     quando NÃO pago e vencimento >= hoje
    """
    today = timezone.localdate()
    qs = (
        LedgerEntry.objects
        .select_related("documento", "cliente")
        .filter(documento__tipo=tipo)
        .annotate(
            status_dyn=Case(
                When(pago_em__isnull=False, then=Value("paid")),
                When(pago_em__isnull=True, vencimento=today, then=Value("due_today")),
                When(pago_em__isnull=True, vencimento__lt=today, then=Value("overdue")),
                default=Value("open"),
                output_field=CharField(),
            ),
            status_order=Case(
                When(pago_em__isnull=True, vencimento__lt=today, then=Value(0)),       # overdue
                When(pago_em__isnull=True, vencimento=today, then=Value(1)),           # due_today
                When(pago_em__isnull=True, vencimento__gt=today, then=Value(2)),       # open
                When(pago_em__isnull=False, then=Value(3)),                            # paid
                default=Value(4),
                output_field=IntegerField(),
            ),
        )
        .order_by("status_order", "vencimento", "id")
    )
    return list(qs)

# -----------------------------
# Criação manual de documentos (CR/CP) com parcelas
# -----------------------------

@transaction.atomic
def criar_documento_manual(
    *,
    tipo: str,
    descricao: str,
    valor_total: Decimal,
    parcelas: int,
    primeiro_vencimento: Optional[date] = None,
    intervalo_dias: int,
    cliente_id: Optional[int] = None,
    parceiro_nome: str = "",
    meio_pagamento: str = "",
    categoria_id: Optional[int] = None,
    categoria_parent_id: Optional[int] = None,
) -> FinanceDocument:
    """
    Cria um documento financeiro e gera os lançamentos (parcelas) associados.
    Obs.: Categoria de despesa ainda não está modelada no LedgerEntry. Mantemos os parâmetros
    por compatibilidade, mas eles não são persistidos em relação direta.
    """
    # Documento
    doc = FinanceDocument.objects.create(
        tipo=tipo,
        descricao=descricao,
        valor_total=valor_total,
        cliente_id=cliente_id if tipo == "CR" else None,
        fornecedor_nome=parceiro_nome if tipo == "CP" else "",
    )

    # Geração das parcelas
    if parcelas <= 0:
        parcelas = 1

    # Rateio simples do valor total
    valor_parcela = (Decimal(valor_total) / Decimal(parcelas)).quantize(Decimal("0.01"))
    data = primeiro_vencimento or timezone.localdate()

    entries = []
    for i in range(parcelas):
        e = LedgerEntry.objects.create(
            documento=doc,
            cliente_id=cliente_id if tipo == "CR" else None,
            tipo=tipo,
            descricao=f"{descricao} ({i+1}/{parcelas})",
            valor=valor_parcela,
            vencimento=data,
            pago_em=None,
            meio_pagamento=meio_pagamento or "",
            expense_category_id=categoria_id if (tipo=="CP") else None,
            expense_category_parent_id=categoria_parent_id if (tipo=="CP") else None,
        )
        entries.append(e)
        data = data + timedelta(days=int(intervalo_dias or 30))

    return doc


# ==== Accounts & Payment Methods (no migrations, raw SQL) ====
from django.db import connection

_ACCOUNT_SQL = """
CREATE TABLE IF NOT EXISTS finance_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

_PAYMENT_SQL = """
CREATE TABLE IF NOT EXISTS finance_paymentmethod (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def _sqlq(v: str) -> str:
    if v is None:
        return ""
    return str(v).replace("'", "''")


def _ensure_tables():
    with connection.cursor() as cur:
        cur.execute(_ACCOUNT_SQL)
        cur.execute(_PAYMENT_SQL)

def create_account(nome: str, tipo: str) -> int:
    _ensure_tables()
    sql = f"INSERT INTO finance_account (nome, tipo, ativo) VALUES ('{_sqlq(nome)}', '{_sqlq(tipo)}', 1)"
    with connection.cursor() as cur:
        cur.execute(sql)
        return cur.lastrowid

def list_accounts() -> list[dict]:
    _ensure_tables()
    with connection.cursor() as cur:
        cur.execute("SELECT id, nome, tipo, ativo, created_at FROM finance_account WHERE ativo=1 ORDER BY id ASC")
        rows = cur.fetchall()
    res = []
    for r in rows:
        res.append({"id": r[0], "nome": r[1], "tipo": r[2], "ativo": r[3], "created_at": r[4]})
    return res

def account_balance(account_id: int) -> dict:
    """Compute totals using LedgerEntry.meio_pagamento matching the account name (compat)."""
    _ensure_tables()
    with connection.cursor() as cur:
        cur.execute(f"SELECT nome FROM finance_account WHERE id={int(account_id)}")
        row = cur.fetchone()
        if not row:
            return {"in": 0, "out": 0, "balance": 0}
        acc_name = row[0]
    # Use ORM for sums
    qs = LedgerEntry.objects.filter(meio_pagamento=acc_name).values_list("tipo", "valor", "pago_em")
    total_in = sum([float(v) for t, v, pe in qs if t == "CR" and pe is not None])
    total_out = sum([float(v) for t, v, pe in qs if t == "CP" and pe is not None])
    return {"in": total_in, "out": total_out, "balance": total_in - total_out}

# Payment Methods
def create_payment_method(nome: str, tipo: str) -> int:
    _ensure_tables()
    with connection.cursor() as cur:
        sql = f"INSERT INTO finance_paymentmethod (nome, tipo, ativo) VALUES ('{_sqlq(nome)}', '{_sqlq(tipo)}', 1)"
        cur.execute(sql)
        return cur.lastrowid

def list_payment_methods() -> list[dict]:
    _ensure_tables()
    with connection.cursor() as cur:
        cur.execute("SELECT id, nome, tipo, ativo, created_at FROM finance_paymentmethod WHERE ativo=1 ORDER BY nome ASC")
        rows = cur.fetchall()
    res = []
    for r in rows:
        res.append({"id": r[0], "nome": r[1], "tipo": r[2], "ativo": r[3], "created_at": r[4]})
    return res



def format_brl(value) -> str:
    try:
        v = float(value or 0.0)
    except Exception:
        v = 0.0
    neg = v < 0
    v = abs(v)
    intp = int(v)
    cents = int(round((v - intp) * 100))
    # adjust rounding edge-case
    if cents == 100:
        intp += 1
        cents = 0
    intp_str = f"{intp:,}".replace(",", ".")
    return ("-R$ " if neg else "R$ ") + f"{intp_str},{cents:02d}"


# ===== Geração de títulos a partir de objetos de outros apps (sem migração) =====
from django.contrib.contenttypes.models import ContentType

def has_document_for_origin(app_label: str, model: str, obj_id: int, tipo: str) -> bool:
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model.lower())
    except ContentType.DoesNotExist:
        return False
    return FinanceDocument.objects.filter(origem_ct=ct, origem_id=obj_id, tipo=tipo).exists()

@transaction.atomic
def gerar_cr_de_pedido(*, order_id: int, parcelas: int, primeiro_vencimento=None, intervalo_dias: int = 30, meio_pagamento: str = "", categoria_id=None, categoria_parent_id=None) -> FinanceDocument:
    # Import tardio para evitar import cycles
    from sales.models import SalesOrder
    order = SalesOrder.objects.select_related("cliente").get(id=order_id)
    descricao = f"Pedido #{order.id} - {order.cliente}"
    valor = order.total_liquido or 0
    # Documento com vínculo à origem
    ct = ContentType.objects.get(app_label="sales", model="salesorder")
    doc = FinanceDocument.objects.create(
        tipo="CR",
        descricao=descricao,
        valor_total=valor,
        cliente_id=order.cliente_id,
        fornecedor_nome="",
        origem_ct=ct,
        origem_id=order.id,
        status="open",
    )
    # Parcelamento
    if parcelas <= 0:
        parcelas = 1
    valor_parcela = (Decimal(str(valor)) / Decimal(parcelas)).quantize(Decimal("0.01"))
    data = primeiro_vencimento or timezone.localdate()
    for i in range(parcelas):
        LedgerEntry.objects.create(
            documento=doc,
            cliente_id=order.cliente_id,
            tipo="CR",
            descricao=f"{descricao} ({i+1}/{parcelas})",
            valor=valor_parcela,
            vencimento=data,
            pago_em=None,
            meio_pagamento=meio_pagamento or "",
            expense_category_id=None,
            expense_category_parent_id=None,
        )
        data = data + timedelta(days=int(intervalo_dias or 30))
    return doc

@transaction.atomic
def gerar_cp_de_entrada_estoque(*, mov_id: int, parcelas: int, primeiro_vencimento=None, intervalo_dias: int = 30, fornecedor_nome: str = "", categoria_id=None, categoria_parent_id=None) -> FinanceDocument:
    from inventory.models import StockMovement
    mov = StockMovement.objects.select_related("produto").get(id=mov_id)
    total = (mov.quantidade or 0) * (mov.custo_unitario or 0)
    descricao = f"Entrada #{mov.id} - {mov.produto}"
    # Documento com vínculo à origem
    ct = ContentType.objects.get(app_label="inventory", model="stockmovement")
    doc = FinanceDocument.objects.create(
        tipo="CP",
        descricao=descricao,
        valor_total=total,
        cliente_id=None,
        fornecedor_nome=fornecedor_nome or "",
        origem_ct=ct,
        origem_id=mov.id,
        status="open",
    )
    # Parcelamento
    if parcelas <= 0:
        parcelas = 1
    valor_parcela = (Decimal(str(total)) / Decimal(parcelas)).quantize(Decimal("0.01"))
    data = primeiro_vencimento or timezone.localdate()
    for i in range(parcelas):
        l = LedgerEntry.objects.create(
            documento=doc,
            cliente_id=None,
            tipo="CP",
            descricao=f"{descricao} ({i+1}/{parcelas})",
            valor=valor_parcela,
            vencimento=data,
            pago_em=None,
            meio_pagamento="",
            expense_category_id=categoria_id,
            expense_category_parent_id=categoria_parent_id,
        )
        data = data + timedelta(days=int(intervalo_dias or 30))
        # Opcional: marcar categoria, se informado e for CP
        try:
            if categoria_parent_id:
                setattr(l, "expense_category_parent_id", categoria_parent_id)
            if categoria_id:
                setattr(l, "expense_category_id", categoria_id)
        except Exception:
            pass
    return doc



def list_cashbook(account_id: int | None, start: date | None, end: date | None) -> list[dict]:
    """Retorna movimentos de caixa (apenas lançamentos pagos) para o extrato.

    Cada item: {"date": date, "account_id": int|None, "type": "in"|"out", "description": str, "amount": Decimal}
    Filtro por conta é feito casando LedgerEntry.meio_pagamento com o nome da conta (compatibilidade).
    """
    # Mapear contas por nome<->id
    try:
        accounts = list_accounts()
    except Exception:
        accounts = []
    name_to_id = {a["nome"]: a["id"] for a in accounts}

    qs = LedgerEntry.objects.all()
    # Somente movimentos efetivados (pago)
    qs = qs.exclude(pago_em__isnull=True)

    # Filtro por conta (meio_pagamento == nome da conta)
    if account_id:
        acc = next((a for a in accounts if a["id"] == int(account_id)), None)
        if acc:
            qs = qs.filter(meio_pagamento=acc["nome"])

    # Período pelo campo pago_em
    if start:
        qs = qs.filter(pago_em__gte=start)
    if end:
        qs = qs.filter(pago_em__lte=end)

    qs = qs.order_by("pago_em", "id").values("id", "tipo", "descricao", "valor", "pago_em", "meio_pagamento")

    rows: list[dict] = []
    for r in qs:
        acc_id = name_to_id.get(r["meio_pagamento"])
        rows.append({
            "date": r["pago_em"],
            "account_id": acc_id,
            "type": "in" if r["tipo"] == "CR" else "out",
            "description": r["descricao"],
            "amount": r["valor"],
        })
    return rows

@transaction.atomic
def baixa_parcela(entry_id: int, *, data_pagto, meio: str = "", conta_id: int | None = None) -> bool:
    """
    Registra a baixa de um lançamento (CR/CP).

    - Seta `pago_em` com a data informada.
    - Preenche `meio_pagamento` com o NOME da conta escolhida (compatível com o extrato).
    - Atualiza o status do documento (open/partial/paid).

    Retorna True em caso de sucesso.
    """
    try:
        le = LedgerEntry.objects.select_related("documento").get(id=entry_id)
    except LedgerEntry.DoesNotExist:
        return False

    # Obter nome da conta pelo ID (o extrato casa pelo nome)
    conta_nome = ""
    try:
        if conta_id is not None:
            for a in list_accounts():
                if int(a["id"]) == int(conta_id):
                    conta_nome = a["nome"]
                    break
    except Exception:
        pass

    # Compat: priorize o nome da conta; se não houver, use o "meio" informado
    meio_final = conta_nome or (meio or "")

    # Idempotência: se já estiver pago, apenas garanta o meio_pagamento
    le.pago_em = data_pagto
    le.meio_pagamento = meio_final
    le.save(update_fields=["pago_em", "meio_pagamento"])

    # Se houver documento, atualize o status conforme as parcelas
    if getattr(le, "documento_id", None):
        doc = le.documento
        qs = doc.lancamentos.all()
        if qs.filter(pago_em__isnull=True).exists():
            novo_status = "partial" if qs.filter(pago_em__isnull=False).exists() else "open"
        else:
            novo_status = "paid"
        if doc.status != novo_status:
            doc.status = novo_status
            doc.save(update_fields=["status"])

    return True