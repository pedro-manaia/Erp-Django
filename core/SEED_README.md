
# Auto Seed (core.initial_data)

- Sinal `post_migrate` conectado em `core/signals.py` executa *seed* logo após `migrate --run-syncdb`.
- Cria: **usuário admin**, **Produto Padrão (P001)**, **Cliente Padrão**, **Categoria de Despesa "Despesas Gerais"**.
- Controle via variáveis de ambiente:
  - `ADMIN_USERNAME` (padrão: `admin`)
  - `ADMIN_EMAIL` (padrão: `admin@local`)
  - `ADMIN_PASSWORD` (padrão: `admin`)
  - `DISABLE_AUTO_SEED=1` para desabilitar.

Executa de forma idempotente: se já existir, não duplica.
