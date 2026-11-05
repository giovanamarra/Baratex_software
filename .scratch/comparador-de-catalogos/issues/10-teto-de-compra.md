# 10 — Teto de compra destacado na Revisão e na busca

Status: resolved
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

## Comments

**Resolução (2026-11-05)**

- **Casos de uso:** `definir_teto(gestor, valor)` e `obter_teto(gestor)`. O Teto é uma linha única do grupo (`TetoDeCompra`, migração 0011); definir de novo substitui. Não guarda autor nem data, porque o ADR-0007 não pede auditoria do Teto.
- **Leitura do valor:** `preco_digitado(texto, nome)` subiu da Importação para Catálogos e é a mesma leitura de preço da Revisão ("1.500" é recusado como ambíguo). Vazio, zero, negativo e texto inválido dão `O Teto de compra precisa ser maior que zero.`
- **Destaque:** derivado na consulta (`Oferta.acima_do_teto`, `OfertaProposta.acima_do_teto`), nunca gravado. Só o Preço unitário acima do Teto; igual não. Sem Teto, nada é destacado. A busca e a Revisão carregam o Teto uma vez por consulta.
- **Telas:** "Teto de compra" na barra (`/teto/`); "acima do Teto" em texto, com a linha em alerta, na busca e na Revisão. O Catálogo confirmado não destaca (o ticket pede só a Revisão e a busca); comparação (13) e Pedido (16) acrescentam o seu.
- **Correção feita antes do ticket:** "Definir Conteúdo" aberto da busca volta para a busca com os mesmos filtros (`?voltar=`, só endereços do próprio sistema); aberto do Catálogo, volta ao Catálogo.
