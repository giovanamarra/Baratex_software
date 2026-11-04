# 19 — Exportar vários Pedidos num arquivo, com um bloco por desconto

Status: ready-for-agent
Type: task
Blocked by: 18
Spec: [docs/spec.md](../../../docs/spec.md) (Exportação de Pedidos)
ADRs: ADR-0004 (um arquivo com vários Pedidos; um bloco por desconto distinto)
User stories: 85, 87

## O que entrega

A gestora escolhe vários Pedidos, na ordem que quiser, e manda tudo de uma vez a um Representante. Um Pedido com Ofertas de Catálogos com descontos diferentes sai em blocos separados, cada um com o desconto certo.

## Critérios de aceite

- Exportar [Pedido Beta, Pedido Alfa] gera um arquivo com o bloco do Beta antes do bloco do Alfa (85).
- Um Pedido com linhas de dois Catálogos do mesmo Fornecedor, ambos com 5%, sai num único bloco.
- Um Pedido com linhas de um Catálogo com 5% e de outro sem desconto sai em dois blocos: um com a linha de desconto de 5% e outro sem linha de desconto (87).
- Dentro de um Pedido, os blocos seguem a ordem em que cada desconto aparece pela primeira vez entre as linhas.
- Cada Pedido exportado tem a data da exportação registrada.
- As regras do ticket 18 (Lojas presentes, fórmulas, observação) valem em cada bloco. A observação sai abaixo do último bloco do Pedido.

## Erros (mensagens em português)

- O mesmo Pedido escolhido duas vezes → `O Pedido do Fornecedor Alfa foi escolhido duas vezes.`

## O que o teste precisa

- Dois Fornecedores; dois Catálogos fictícios do Layout A do mesmo Fornecedor, com descontos diferentes; Pedidos montados pelos casos de uso.
- Nenhum fake da LLM.
