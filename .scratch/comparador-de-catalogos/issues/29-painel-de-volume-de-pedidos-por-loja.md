# 29 — Painel de volume de Pedidos de compra por Loja

Status: ready-for-agent
Type: task
Blocked by: 17
Spec: [docs/spec.md](../../../docs/spec.md) (Painéis por Loja; Implementation Decisions › Painéis; Further Notes › categoria)
ADRs: ADR-0007 (Pedidos e Lojas são do Gestor)
User stories: 95, 96

## O que entrega

A gestora vê quanto compra para cada uma das suas Lojas, por Fornecedor e por mês, num painel que deixa claro que são Pedidos de compra, não vendas.

Decisão da usuária: o mês de um Pedido é o da **data de criação**.

## Critérios de aceite

- Volume de Pedidos (Gestor, mês inicial, mês final) devolve, para cada Loja do Gestor, por Fornecedor e por mês de criação do Pedido: o valor e a quantidade de Caixas (95).
- O valor é Unidades de venda × preço impresso, com o desconto das Condições do Catálogo aplicado, como o total da Loja no ticket 15.
- Entram só os Pedidos e as Lojas do Gestor. Os Pedidos de outro Gestor nunca entram.
- Um Pedido criado em outubro e exportado em novembro conta em outubro. Um Pedido nunca exportado também conta.
- O título e os rótulos dizem "Pedidos de compra", e a tela avisa que não são vendas. Nenhum rótulo usa "vendas" para esses dados (96).
- Um mês sem Pedidos não é erro: aparece vazio.

## Erros (mensagens em português)

- Mês inicial depois do mês final → `O mês inicial precisa ser igual ou anterior ao mês final.`

## O que o teste precisa

- Pedidos montados pelos casos de uso, criados em meses diferentes (controle do dia no teste); dois Gestores; um Pedido com Fracionamento.
- Nenhum fake da LLM.

## Notas para o /tdd

- Antes de desenhar o gráfico, use a skill `dataviz`.
- Categoria fica fora: não existe no GLOSSARY (Further Notes do spec).
