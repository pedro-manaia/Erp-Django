
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings

from .initial_data import seed_initial_data

@receiver(post_migrate)
def create_defaults_after_migrate(sender, **kwargs):
    """
    Roda após 'migrate --run-syncdb' e cria dados padrão somente
    quando o banco é recém-criado. É seguro rodar várias vezes.
    Pode ser desabilitado com a env DISABLE_AUTO_SEED=1.
    """
    import os
    if os.environ.get("DISABLE_AUTO_SEED") in ("1","true","True","yes","on"):
        return
    # Só atua quando todas as tabelas principais existem
    needed = ["auth.User","products.Product","customers.Customer","finance.ExpenseCategory"]
    for label in needed:
        try:
            app_label, model_name = label.split(".")
            model = apps.get_model(app_label, model_name)
            # testa acesso simples; se tabela não existir, Query falhará no migrate inicial de alguns bancos
            model.objects.first()
        except Exception:
            return  # ainda não é hora
    seed_initial_data()
