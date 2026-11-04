# 17 — Fracionamento no Perfil do Fornecedor

Status: ready-for-agent
Type: task
Blocked by: 15
Spec: [docs/spec.md](../../../docs/spec.md) (Fornecedores e Perfil do Fornecedor; Modelo de dados › Pedido, Perfil do Fornecedor, Auditoria)
ADRs: ADR-0007 (Perfil é do grupo; alterações com autor e data)
User stories: 10, 13, 78

## O que entrega

A gestora registra que um Fornecedor aceita vender menos que uma Caixa, com uma quantidade mínima. Os Pedidos passam a aceitar meia Caixa desse Fornecedor, respeitando o mínimo.

Decisão da usuária: o mínimo vale para a **soma das Lojas numa linha** do Pedido, não para cada Loja.

## Critérios de aceite

- Definir o Perfil do Fornecedor: Fracionamento (sim ou não) e menor quantidade aceita, em Unidades de venda (10).
- O histórico de alterações do Perfil lista Gestor, data e o que mudou (13).
- Com Fracionamento, mínimo 12 e Caixa de 48 (78):
  - Loja Centro 0,25 Caixa (12 Unidades de venda) → aceito; guarda 12.
  - Loja Centro 0,125 Caixa (6) + Loja Norte 0,125 Caixa (6) = 12 na linha → aceito.
  - Só Loja Centro com 0,125 Caixa (6) → recusado.
  - Uma linha sem nenhuma quantidade (0) continua aceita.
- Quantidades em Caixas inteiras continuam aceitas, como no ticket 15.
- Sem Fracionamento, a regra do ticket 15 continua valendo (79).

## Erros (mensagens em português)

- Linha abaixo do mínimo → `O Fornecedor Alfa aceita no mínimo 12 Unidades de venda por Oferta. Esta linha soma 6.`
- Fração que não dá um número inteiro de Unidades de venda (0,3 Caixa de 48 = 14,4) → `A quantidade precisa dar um número inteiro de Unidades de venda: 0,3 Caixa de 48 dá 14,4.`
- Perfil com Fracionamento sem mínimo, ou com mínimo zero ou negativo → `Informe a menor quantidade aceita, em Unidades de venda, maior que zero.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com uma Oferta de Caixa 48; um Gestor com duas Lojas.
- Nenhum fake da LLM.

## Fora deste ticket

- Mapeamento de colunas no Perfil (21, 23).
- Restringir quem altera o Perfil (Out of Scope).
