# 13 — Comparar as Ofertas vigentes de um Produto

Status: ready-for-agent
Type: task
Blocked by: 10, 12, 31
Spec: [docs/spec.md](../../../docs/spec.md) (Produtos e comparação; Casos de uso › comparar Produto)
ADRs: ADR-0003 (sem vencedor), ADR-0005, ADR-0009 (data do Catálogo ao lado da Oferta)
User stories: 50 (na comparação), 65, 66, 67, 107 (na comparação)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora abre um Produto e vê lado a lado as Ofertas vigentes de todos os Fornecedores, da mais barata para a mais cara pelo Preço unitário. É assim que ela descobre se o kit sai mais barato por peça que a tesoura vendida avulsa.

## Critérios de aceite

- Comparar Produto devolve as Ofertas vigentes ligadas a ele, em ordem crescente de Preço unitário. Cada uma vem com descrição, Fornecedor, Caixa, Preço unitário, **data do Catálogo** (como foi informada: `15/10/2026` ou `10/2026`) e o destaque de acima do Teto de compra (65, 50, 107).
- Só entram Ofertas vigentes, pela regra do ticket 31: o preço de um Catálogo de data anterior do mesmo Fornecedor + código não aparece, mesmo que seja mais barato.
- **Kit contra peça avulsa** (67): Fornecedor Alfa, kit de 3 tesouras a 9,00 com Conteúdo 3 (3,00); Fornecedor Alfa, tesoura avulsa a 3,20; Fornecedor Beta, tesoura avulsa a 3,50. A ordem é 3,00; 3,20; 3,50.
- Empate no Preço unitário → ordem alfabética do Fornecedor, para o resultado ser sempre o mesmo.
- Sem vencedora (66): o resultado não tem campo de "melhor compra", e a tela não destaca a primeira Oferta. O único destaque é o do Teto.
- Um Produto sem Ofertas ligadas devolve lista vazia, e a tela diz `Nenhuma Oferta ligada a este Produto ainda.`

## Erros (mensagens em português)

- Comparar um Produto que não existe → `Produto não encontrado.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Fornecedores com as Ofertas inventadas do exemplo do kit; um Catálogo de data anterior com preço **menor**, para provar que a vigência vem da data; Teto definido.
- Nenhum fake da LLM.

## Fora deste ticket

- Foto na comparação (14). Adicionar ao Pedido a partir da comparação (16).
