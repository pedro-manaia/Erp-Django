# Finance (sem migrações)

Este módulo implementa **Contas a Receber (CR)** e **Contas a Pagar (CP)** sem criar tabelas no banco do Django.
Os lançamentos e documentos são gravados em **arquivos JSON** em `runtime/finance/` dentro do projeto.

## Como usar
1. Copie a pasta `finance/` desta entrega por cima da sua `finance/` atual.
2. Garanta que `erp/urls.py` inclui:
   ```python
   path("finance/", include(("finance.urls","finance"), namespace="finance")),
   ```
3. Inicie o servidor e acesse `/finance/`.

## Onde os dados ficam
- `runtime/finance/ledger_docs.jsonl`: documentos (títulos) CR/CP.
- `runtime/finance/ledger_entries.jsonl`: parcelas (lançamentos).
- `runtime/finance/seq.json`: sequência de IDs.

## Integração
- **CR a partir de Pedido**: usa `sales.SalesOrder` (lido via ORM) para calcular o total e vincula a origem.
- **CP a partir de Entrada**: usa `inventory.StockMovement` (IN/ADJ) e calcula `custo_unitario * quantidade`.

## Limitações
- Como não há tabelas, não há Admin para estes dados.
- Se quiser voltar a um modelo com banco (ORM), bastará migrar no futuro.
