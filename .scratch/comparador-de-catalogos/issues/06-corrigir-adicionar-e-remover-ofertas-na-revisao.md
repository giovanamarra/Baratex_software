# 06 — Corrigir, adicionar e remover Ofertas na Revisão

Status: ready-for-agent
Type: task
Blocked by: 05
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › confirmação recusada; Extração › marcas de conferência)
ADRs: ADR-0006 (Oferta sem Caixa não é confirmada)
User stories: 30 (preço ausente ou zero), 31, 34, 35, 36

## O que entrega

A gestora conserta erros de leitura antes de salvar. A confirmação é recusada enquanto houver Oferta sem Caixa ou sem preço válido.

## Critérios de aceite

- Corrigir uma Oferta proposta (código, descrição, preço impresso, Caixa, Embalagem intermediária) faz a Revisão mostrar o valor novo e recalcula o Preço unitário (34).
- Adicionar uma Oferta à mão faz ela aparecer na Revisão com o caminho "manual" (35).
- Remover uma Oferta proposta tira ela da Revisão, e ela não entra no Catálogo (36).
- Uma Oferta sem preço ou com preço zero fica marcada (30).
- A confirmação é recusada enquanto houver Oferta sem Caixa. Depois que a gestora informa a Caixa, a confirmação passa (31).
- A confirmação é recusada enquanto houver Oferta sem preço maior que zero.
- As correções só chegam ao Catálogo com a confirmação. Abandonar a Revisão descarta todas.

## Erros (mensagens em português)

- Confirmar com Oferta sem Caixa → `Informe a Caixa antes de confirmar. Ofertas sem Caixa: 1001, 1007.`
- Confirmar com Oferta sem preço válido → `Informe um preço maior que zero antes de confirmar. Ofertas sem preço: 1003.`
- Corrigir com preço negativo ou zero → `O preço precisa ser maior que zero.`
- Caixa zero, negativa ou fracionária → `A Caixa precisa ser um número inteiro de Unidades de venda, maior que zero.`
- Adicionar Oferta sem código ou sem descrição → `Informe o código e a descrição da Oferta.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com um cartão sem Caixa e um cartão sem preço.
- Nenhum fake da LLM.

## Fora deste ticket

- Preço fora do padrão, Unidade de venda ambígua, sugestão de Conteúdo e contagem de preços (08).
