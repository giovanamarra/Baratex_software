# 30 — Painel de evolução de preço dos Produtos e comparação entre Fornecedores

Status: ready-for-agent
Type: task
Blocked by: 28, 13
Spec: [docs/spec.md](../../../docs/spec.md) (Painéis › evolução do Preço unitário por Produto e Fornecedor)
ADRs: ADR-0003, ADR-0005, ADR-0009 (eixo do tempo pela data do Catálogo)
User stories: 97
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

Um painel em que a gestora acompanha, Produto a Produto, a evolução do Preço unitário de cada Fornecedor e a comparação atual, para planejar as próximas compras.

## Critérios de aceite

- O painel lista os Produtos. Para cada um, mostra a evolução do Preço unitário por Fornecedor (consulta do ticket 28) e as Ofertas vigentes ordenadas (consulta do ticket 13).
- O painel não tem regra nova de cálculo: com os mesmos dados fictícios, os números são idênticos aos dos tickets 13 e 28.
- O eixo do tempo é a **data do Catálogo** (ticket 28), não o dia da Importação; um Catálogo só com mês e ano aparece no dia 1 do mês, com o rótulo como foi informado (`10/2026`).
- As Ofertas vigentes mostram a data do Catálogo, como na comparação (ticket 13).
- Os rótulos dizem "Preço unitário (sem impostos)" e indicam que os preços vêm dos Catálogos.
- A comparação continua sem indicar "melhor compra" (ADR-0003). O destaque de acima do Teto de compra aparece.
- Um Produto sem Ofertas aparece com `Nenhuma Oferta ligada a este Produto ainda.`

## Erros (mensagens em português)

- Abrir o painel de um Produto que não existe → `Produto não encontrado.`

## O que o teste precisa

- Os mesmos dados fictícios do ticket 28 e um Teto definido.
- Nenhum fake da LLM.

## Notas para o /tdd

- Antes de desenhar o gráfico, use a skill `dataviz`.
