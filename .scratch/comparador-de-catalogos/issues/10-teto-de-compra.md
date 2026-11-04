# 10 — Teto de compra destacado na Revisão e na busca

Status: ready-for-agent
Type: task
Blocked by: 09
Spec: [docs/spec.md](../../../docs/spec.md) (Teto de compra; Modelo de dados › Teto de compra é um único valor do grupo)
ADRs: ADR-0003 (Teto não é do Produto), ADR-0007 (Teto é do grupo)
User stories: 49, 50, 51

## O que entrega

A gestora define o maior Preço unitário que ainda dá lucro, e toda Oferta acima dele aparece destacada.

## Critérios de aceite

- Definir o Teto de compra (Gestor, valor) guarda um único valor para o grupo. Definir de novo substitui o anterior (49, 51).
- Sem Teto definido, nenhuma Oferta é destacada.
- Com Teto 5,00: uma Oferta com Preço unitário 5,01 fica destacada; uma com 5,00 não fica. Só "acima do Teto" é destacado.
- O destaque usa o Preço unitário, não o preço impresso. Uma Oferta de 5,50 com desconto de 10% (4,95) não é destacada. Um kit de 9,00 com Conteúdo 3 (3,00) também não.
- O destaque aparece na Revisão e nos resultados da busca (50). Os tickets de comparação (13) e de Pedido (16) acrescentam o destaque nas suas listas.
- Mudar o Teto muda o destaque na próxima consulta, sem nenhum outro passo.

## Erros (mensagens em português)

- Teto vazio, zero ou negativo → `O Teto de compra precisa ser maior que zero.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com preços inventados em torno do Teto.
- Nenhum fake da LLM.

## Fora deste ticket

- Teto por Produto, categoria ou Loja (Out of Scope).
