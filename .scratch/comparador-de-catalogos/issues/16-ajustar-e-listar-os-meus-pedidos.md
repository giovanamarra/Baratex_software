# 16 — Ajustar e listar os meus Pedidos

Status: ready-for-agent
Type: task
Blocked by: 15, 13
Spec: [docs/spec.md](../../../docs/spec.md) (Pedidos; Base comum do grupo; Testing Decisions › testes pelo cliente HTTP)
ADRs: ADR-0007 (Pedido é privado do Gestor no MVP), ADR-0009 (data do Catálogo nas linhas)
User stories: 4, 76, 81, 82, 83, 84, 100, 107 (nas linhas do Pedido)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora ajusta a compra (altera e remove linhas, escreve uma observação), retoma Pedidos em andamento e adiciona Ofertas direto da comparação. Os Pedidos dela ficam invisíveis para os outros Gestores.

## Critérios de aceite

Pelo caso de uso

- Alterar as quantidades de uma linha e remover uma linha (82).
- Definir a observação do Pedido, em texto livre (81).
- Listar os meus Pedidos, com Fornecedor e data de criação, do mais recente para o mais antigo (83).
- Os Pedidos de um Gestor não aparecem na lista de outro (100).
- Uma linha cuja Oferta está acima do Teto de compra aparece destacada no Pedido (84).
- Cada linha do Pedido mostra a data do Catálogo da sua Oferta, como foi informada (107).
- Na comparação do Produto, a tela oferece "adicionar ao Pedido" para os Pedidos do Gestor com o mesmo Fornecedor da Oferta, usando o mesmo caso de uso do ticket 15 (76).

Pelo cliente HTTP do Django (Testing Decisions)

- O Gestor B não consegue abrir nem editar, pela URL, um Pedido do Gestor A (4).
- O Gestor B não consegue incluir, pelo formulário, uma Loja do Gestor A no próprio Pedido.

## Erros (mensagens em português)

- Abrir ou editar o Pedido de outro Gestor → `Este Pedido é de outro Gestor.`
- Adicionar uma Oferta que já está no Pedido → `Esta Oferta já está no Pedido. Altere a quantidade na linha existente.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Gestores com Lojas; Teto definido; um Produto com Ofertas ligadas.
- Nenhum fake da LLM.

## Fora deste ticket

- Consultar Pedidos de outros Gestores (Out of Scope; o modelo não deve impedir).
- Linha cuja Oferta deixou de ser vigente, com "Usar a Oferta vigente" (40).
