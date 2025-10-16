from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View, CreateView, ListView

from .forms import GerarTituloForm, BaixaForm, NewDocForm, QuickCRForm, QuickCPForm, LedgerEntryForm
from . import services

class FinanceHomeView(LoginRequiredMixin, TemplateView):
    template_name = "finance/home.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        accounts = services.list_accounts()
        balances = [(a, services.account_balance(a["id"])) for a in accounts]
        ctx["accounts"] = accounts
        ctx["balances"] = balances
        ctx["cr_form"] = QuickCRForm()
        ctx["cp_form"] = QuickCPForm()
        ctx["today"] = date.today().isoformat()
        return ctx

class CRListView(LoginRequiredMixin, TemplateView):
    template_name = "finance/cr_list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_list"] = services.listar_lancamentos("CR")
        return ctx

class CPListView(LoginRequiredMixin, TemplateView):
    template_name = "finance/cp_list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rows = services.listar_lancamentos("CP")
        # opcional: computa rótulo de categoria (pai/filho) sem quebrar se rows forem dicts
        try:
            cats = {c.id: c for c in ExpenseCategory.objects.select_related("parent").all()}
        except Exception:
            cats = {}
        def _cid(obj):
            try:
                v = getattr(obj, "expense_category_id", None)
            except Exception:
                v = obj.get("expense_category_id") if isinstance(obj, dict) else None
            if not v:
                try:
                    v = getattr(obj, "expense_category_parent_id", None)
                except Exception:
                    v = obj.get("expense_category_parent_id") if isinstance(obj, dict) else None
            return v

        def _set_label(obj, label):
            try:
                setattr(obj, "categoria_label", label)
            except Exception:
                if isinstance(obj, dict):
                    obj["categoria_label"] = label
        for r in rows:
            cid = _cid(r)
            label = None
            if cid and cid in cats:
                c = cats[cid]
                label = f"{c.parent.name} / {c.name}" if c.parent else c.name
            _set_label(r, label)
        ctx["object_list"] = rows
        return ctx
    # removed conflicting method
    # removed conflicting method

class GerarCPDeEntradaView(LoginRequiredMixin, View):
    template_name = "finance/gerar_titulo.html"
    def get(self, request, pk):
        form = GerarTituloForm()
        return render(request, self.template_name, {"form": form, "titulo": f"Gerar CP da Entrada #{pk}"})
    def post(self, request, pk):
        form = GerarTituloForm(request.POST)
        if form.is_valid():
            services.gerar_cp_de_entrada_estoque(
                mov_id=pk,
                parcelas=form.cleaned_data["parcelas"],
                primeiro_vencimento=form.cleaned_data["primeiro_vencimento"],
                intervalo_dias=form.cleaned_data["intervalo_dias"],
                fornecedor_nome=form.cleaned_data.get("fornecedor_nome") or "",
                categoria_id=(form.cleaned_data.get('categoria').id if form.cleaned_data.get('tipo')=='CP' and form.cleaned_data.get('categoria') else None),
                categoria_parent_id=(form.cleaned_data.get('categoria').parent.id if form.cleaned_data.get('tipo')=='CP' and form.cleaned_data.get('categoria') else None),
            )
            messages.success(request, f"CP gerado para a Entrada #{pk}.")
            return redirect("finance:cp_list")
        return render(request, self.template_name, {"form": form, "titulo": f"Gerar CP da Entrada #{pk}"})

class BaixaParcelaFormView(LoginRequiredMixin, View):
    template_name = "finance/baixa_form.html"
    def get(self, request, pk):
        form = BaixaForm()
        choices = [(a["id"], f'{a["nome"]} ({a["tipo"]})') for a in services.list_accounts()]
        form.fields["conta_id"].choices = choices
        return render(request, self.template_name, {"form": form, "entry_id": pk})
    def post(self, request, pk):
        form = BaixaForm(request.POST)
        choices = [(a["id"], f'{a["nome"]} ({a["tipo"]})') for a in services.list_accounts()]
        form.fields["conta_id"].choices = choices
        if form.is_valid():
            ok = services.baixa_parcela(
                pk,
                data_pagto=form.cleaned_data["data_pagto"],
                meio=form.cleaned_data.get("meio_pagamento") or "",
                conta_id=int(form.cleaned_data["conta_id"]),
            )
            if ok:
                messages.success(request, "Baixa registrada no caixa.")
                return redirect("finance:home")
        messages.error(request, "Não foi possível registrar a baixa.")
        return render(request, self.template_name, {"form": form, "entry_id": pk})

class NewDocView(LoginRequiredMixin, View):
    template_name = "finance/new_doc.html"
    def get(self, request):
        tipo_get = request.GET.get("tipo") or ""
        form = NewDocForm(initial={"tipo": tipo_get})
        return render(request, self.template_name, {"form": form})
    def post(self, request):
        form = NewDocForm(request.POST)
        if form.is_valid():
            
            selected_cat = form.cleaned_data.get("categoria")
            cat_id = None
            cat_parent_id = None
            if selected_cat:
                if getattr(selected_cat, "parent", None):
                    cat_parent_id = selected_cat.parent_id
                    cat_id = selected_cat.id
                else:
                    cat_parent_id = selected_cat.id
                    cat_id = None
            services.criar_documento_manual(
                tipo=form.cleaned_data["tipo"],
                descricao=form.cleaned_data["descricao"],
                valor_total=form.cleaned_data["valor_total"],
                parcelas=form.cleaned_data["parcelas"],
                primeiro_vencimento=form.cleaned_data["primeiro_vencimento"],
                intervalo_dias=form.cleaned_data["intervalo_dias"],
                parceiro_nome=form.cleaned_data.get("parceiro_nome") or "",
                categoria_id=cat_id,
                categoria_parent_id=cat_parent_id,
            )
            messages.success(request, "Documento criado.")
            return redirect("finance:home")
        return render(request, self.template_name, {"form": form})

class AccountsListCreateView(LoginRequiredMixin, View):
    template_name = "finance/accounts.html"
    def get(self, request):
        accounts = services.list_accounts()
        rows = []
        for a in accounts:
            b = services.account_balance(a['id'])
            rows.append({'a': a, 'saldo': b.get('balance', 0.0), 'saldo_fmt': services.format_brl(b.get('balance', 0.0))})
        return render(request, self.template_name, {'accounts': accounts, 'rows': rows})
def post(self, request):
        nome = request.POST.get("nome", "").strip()
        tipo = request.POST.get("tipo", "cash")
        if nome:
            services.create_account(nome, tipo)
            messages.success(request, "Conta criada.")
        return redirect("finance:accounts")

class CashbookView(LoginRequiredMixin, View):
    template_name = "finance/cashbook.html"
    def get(self, request):
        account_id = request.GET.get("account_id")
        start = request.GET.get("start")
        end = request.GET.get("end")
        acc = int(account_id) if account_id else None
        s = date.fromisoformat(start) if start else None
        e = date.fromisoformat(end) if end else None
        rows = services.list_cashbook(acc, s, e)
        accounts = services.list_accounts()
        balances = services.account_balance(acc) if acc else None
        return render(request, self.template_name, {
            "accounts": accounts,
            "rows": rows,
            "selected": acc,
            "balances": balances,
            "start": start,
            "end": end,
        })
class QuickCRView(LoginRequiredMixin, View):
    def post(self, request):
        form = QuickCRForm(request.POST)
        if form.is_valid():
            services.gerar_cr_de_pedido(
                order_id=form.cleaned_data["pedido_id"],
                parcelas=form.cleaned_data["parcelas"],
                primeiro_vencimento=form.cleaned_data["primeiro_vencimento"],
                intervalo_dias=form.cleaned_data["intervalo_dias"],
            )
            messages.success(request, "CR gerado a partir do Pedido.")
        else:
            messages.error(request, "Dados inválidos.")
        return redirect("finance:home")

class QuickCPView(LoginRequiredMixin, View):
    def post(self, request):
        form = QuickCPForm(request.POST)
        if form.is_valid():
            services.gerar_cp_de_entrada_estoque(
                mov_id=form.cleaned_data["entrada_id"],
                parcelas=form.cleaned_data["parcelas"],
                primeiro_vencimento=form.cleaned_data["primeiro_vencimento"],
                intervalo_dias=form.cleaned_data["intervalo_dias"],
            )
            messages.success(request, "CP gerado a partir da Entrada.")
        else:
            messages.error(request, "Dados inválidos.")
        return redirect("finance:home")

class HealthView(LoginRequiredMixin, TemplateView):
    template_name = "finance/health.html"
    def get_context_data(self, **kwargs):
        from django.conf import settings
        from pathlib import Path
        ctx = super().get_context_data(**kwargs)
        base_dir = getattr(settings, "BASE_DIR", ".")
        runtime_dir = Path(base_dir) / "runtime" / "finance"
        try:
            runtime_dir.mkdir(parents=True, exist_ok=True)
            test_file = runtime_dir / "_write_test.tmp"
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("ok")
            test_file.unlink(missing_ok=True)
            writable = True
        except Exception:
            writable = False
        ctx.update({"base_dir": str(base_dir), "runtime_dir": str(runtime_dir), "writable": writable})
        return ctx


from .models import ExpenseCategory
from .forms import ExpenseCategoryForm

class ExpenseCategoryListView(LoginRequiredMixin, TemplateView):
    template_name = "finance/expense_category_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            cats = list(ExpenseCategory.objects.select_related("parent").all())
            need_migration = False
        except (OperationalError, ProgrammingError):
            cats = []
            need_migration = True
        top = [c for c in cats if c.parent_id is None]
        by_parent = {}
        for c in cats:
            by_parent.setdefault(c.parent_id, []).append(c)
        ctx["top_categories"] = sorted(top, key=lambda c: c.name.lower())
        ctx["children_map"] = {pid: sorted(lst, key=lambda c: c.name.lower()) for pid, lst in by_parent.items()}
        ctx["need_migration"] = need_migration
        return ctx




class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    template_name = "finance/expense_category_form.html"
    form_class = ExpenseCategoryForm
    def get_initial(self):
        initial = super().get_initial()
        parent = self.request.GET.get("parent")
        if parent:
            initial["parent"] = parent
        return initial
    def get_success_url(self):
        from django.urls import reverse
        return reverse("finance:expense_category_list")

        ctx = super().get_context_data(**kwargs)
        # Robust check: only show warning if the table truly doesn't exist
        table_name = ExpenseCategory._meta.db_table
        try:
            existing = connection.introspection.table_names()
            need_migration = table_name not in existing
        except Exception:
            # On any introspection issue, fail closed but don't crash
            need_migration = True

        cats = []
        if not need_migration:
            cats = list(ExpenseCategory.objects.select_related("parent").all())

        top = [c for c in cats if c.parent_id is None]
        by_parent = {}
        for c in cats:
            by_parent.setdefault(c.parent_id, []).append(c)
        ctx["top_categories"] = sorted(top, key=lambda c: c.name.lower())
        ctx["children_map"] = {pid: sorted(lst, key=lambda c: c.name.lower()) for pid, lst in by_parent.items()}
        ctx["need_migration"] = need_migration
        return ctx

    def dispatch(self, request, *args, **kwargs):
        # If the table doesn't exist yet, show a friendly message and send back to list
        try:
            exists = ExpenseCategory._meta.db_table in connection.introspection.table_names()
        except Exception:
            exists = False
        if not exists:
            messages.warning(request, "O banco ainda não possui a tabela de Categoria de Despesa. Conclua a inicialização do banco e tente novamente.")
            from django.shortcuts import redirect
            return redirect("finance:expense_categories")
        return super().dispatch(request, *args, **kwargs)



class PaymentMethodsView(LoginRequiredMixin, View):
    template_name = "finance/payment_methods.html"
    def get(self, request):
        items = services.list_payment_methods()
        return render(request, self.template_name, {"items": items})
    def post(self, request):
        nome = request.POST.get("nome") or ""
        if nome.strip():
            services.create_payment_method(nome.strip())
            messages.success(request, "Forma de pagamento criada.")
        else:
            messages.error(request, "Informe o nome da forma de pagamento.")
        return redirect("finance:payment_methods")

class RevenueCategoryListView(ExpenseCategoryListView):
    """Lista apenas categorias sob o nó raiz 'Receitas' (sem migração)."""
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Recalcula top/children para mostrar somente a árvore de 'Receitas'
        try:
            cats = list(ExpenseCategory.objects.select_related("parent").all())
        except Exception:
            return ctx
        by_parent = {}
        for c in cats:
            by_parent.setdefault(c.parent_id, []).append(c)
        roots = [c for c in cats if c.parent_id is None]
        root_receitas = next((r for r in roots if r.name.lower() == "receitas"), None)
        if not root_receitas:
            ctx["top_categories"] = []
            ctx["children_map"] = {}
            ctx["title"] = "Categorias de Receita"
            return ctx
        # Top do relatório: filhos diretos de Receitas
        top_receita = sorted(by_parent.get(root_receitas.id, []), key=lambda c: c.name.lower())
        # Monta mapa apenas da subárvore Receitas
        allowed = set([c.id for c in top_receita])
        stack = [c.id for c in top_receita]
        while stack:
            pid = stack.pop()
            for child in by_parent.get(pid, []):
                if child.id not in allowed:
                    allowed.add(child.id)
                    stack.append(child.id)
        children_map = {}
        for pid, lst in by_parent.items():
            if pid in allowed:
                children_map[pid] = sorted([c for c in lst if c.id in allowed], key=lambda c: c.name.lower())
        ctx["top_categories"] = top_receita
        ctx["children_map"] = children_map
        ctx["title"] = "Categorias de Receita"
        return ctx

class RevenueCategoryCreateView(ExpenseCategoryCreateView):
    """Cria categoria já ancorada em 'Receitas' por padrão (se existir)."""
    def get_initial(self):
        initial = super().get_initial()
        # Se não for passado ?parent=, predefine o pai como 'Receitas' (caso exista)
        if not initial.get("parent"):
            try:
                root = ExpenseCategory.objects.filter(parent__isnull=True, name__iexact="Receitas").first()
                if root:
                    initial["parent"] = root.id
            except Exception:
                pass
        return initial
    def get_success_url(self):
        from django.urls import reverse
        return reverse("finance:revenue_category_list")


# --- Aliases for backward-compatibility with older URL names ---
try:
    FinanceiroHomeView
except NameError:
    class FinanceiroHomeView(FinanceHomeView):
        pass
try:
    FinanceiroCadastroView
except NameError:
    class FinanceiroCadastroView(FinanceHomeView):
        pass
try:
    AccountListCreateView
except NameError:
    AccountListCreateView = AccountsListCreateView
# --- end aliases ---


class CrFromOrderView(LoginRequiredMixin, View):
    """Gera CR a partir de um Pedido (GET simples via link)."""
    def get(self, request, pk):
        from datetime import date
        try:
            services.gerar_cr_de_pedido(order_id=pk, parcelas=1, primeiro_vencimento=date.today(), intervalo_dias=30, meio_pagamento="")
            messages.success(request, f"Contas a Receber gerado a partir do Pedido #{pk}.")
        except Exception as e:
            messages.error(request, f"Falha ao gerar CR: {e}")
        return redirect("sales:orders") if request.META.get("HTTP_REFERER","").find("/vendas")!=-1 else redirect("finance:cr_list")


class LedgerEntryEditView(LoginRequiredMixin, View):
    template_name = "finance/ledger_entry_form.html"

    def get(self, request, pk):
        from .models import LedgerEntry
        try:
            obj = LedgerEntry.objects.get(pk=pk)
        except LedgerEntry.DoesNotExist:
            messages.error(request, "Lançamento não encontrado.")
            return redirect("finance:home")
        initial = {
            "descricao": getattr(obj, "descricao", ""),
            "valor": getattr(obj, "valor", 0),
            "vencimento": getattr(obj, "vencimento", None),
        }
        form = LedgerEntryForm(initial=initial)
        return render(request, self.template_name, {"form": form, "obj": obj})

    def post(self, request, pk):
        from django.db import connection
        from .models import LedgerEntry
        try:
            obj = LedgerEntry.objects.get(pk=pk)
        except LedgerEntry.DoesNotExist:
            messages.error(request, "Lançamento não encontrado.")
            return redirect("finance:home")
        form = LedgerEntryForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "obj": obj})

        # Update basic fields
        obj.descricao = form.cleaned_data["descricao"]
        obj.valor = form.cleaned_data["valor"]
        obj.vencimento = form.cleaned_data["vencimento"]
        try:
            obj.save()
        except Exception:
            # best-effort
            pass

        # Atualiza categoria via ORM
        selected_cat = form.cleaned_data.get("categoria")
        cat_id = None
        cat_parent_id = None
        if selected_cat:
            if getattr(selected_cat, "parent_id", None):
                cat_parent_id = int(selected_cat.parent_id)
                cat_id = int(selected_cat.id)
            else:
                cat_parent_id = int(selected_cat.id)
                cat_id = None

        try:
            obj.expense_category_id = cat_id
            obj.expense_category_parent_id = cat_parent_id
            obj.save(update_fields=["expense_category", "expense_category_parent"])
        except Exception:
            pass

        messages.success(request, "Lançamento atualizado.")
        try:
            tipo = obj.documento.tipo if getattr(obj, "documento_id", None) else obj.tipo
        except Exception:
            tipo = getattr(obj, "tipo", "CR")
        return redirect("finance:cr_list" if tipo == "CR" else "finance:cp_list")