# 18 — Exportar um Pedido na planilha padrão da gestora

Status: ready-for-agent
Type: task
Blocked by: 16
Spec: [docs/spec.md](../../../docs/spec.md) (Exportação de Pedidos; Implementation Decisions › Exportação; Testing Decisions › Exportação)
ADRs: ADR-0004 (formato único da gestora), ADR-0005 (preço sem impostos)
User stories: 85 (um Pedido), 86, 88, 89, 90, 91, 92, 93, 94
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora exporta um Pedido num arquivo Excel com a estrutura e as fórmulas da planilha que ela já envia aos Fornecedores e Representantes, pronto para ajustar e enviar.

## Estrutura do bloco (tirada da planilha padrão da gestora, sem os dados)

1. Uma linha com o nome do Fornecedor.
2. Uma linha de grupo: "PRODUTO" sobre as colunas da Oferta e o nome de cada Loja sobre as 3 colunas dela.
3. Uma linha de cabeçalho: `CÓD.`, `DESCRIÇÃO`, `VALOR`, `EMBAL.` e, para cada Loja, `CAIXA`, `QUANT`, `VALOR`.
4. Uma linha por Oferta do Pedido: código e descrição do Fornecedor, preço impresso por Unidade de venda **sem impostos e sem desconto** (VALOR), Caixa em Unidades de venda (EMBAL.) e, por Loja, as Caixas (valor digitado), `QUANT` = fórmula CAIXA × EMBAL. e `VALOR` = fórmula QUANT × VALOR da Oferta.
5. Uma linha de total, com fórmulas de soma de `QUANT` e `VALOR` de cada Loja.
6. Quando o desconto das Condições do Catálogo é maior que zero, uma linha de desconto: o percentual na coluna `DESCRIÇÃO` e, por Loja, `QUANT` repetindo o total e `VALOR` = fórmula total × (1 − desconto). O preço das linhas não muda (91).
7. A observação do Pedido, abaixo do bloco (93).

## Critérios de aceite

- Exportar Pedidos (Gestor, [Pedido]) devolve um arquivo .xlsx. O teste reabre o arquivo e confere a estrutura acima (86, 88, 89).
- Quantidades, valores e somas são fórmulas que apontam para as células certas, e não valores fixos (90). Avaliadas, dão os valores esperados.
- Só aparecem as Lojas com alguma quantidade no Pedido (92). Linhas sem nenhuma quantidade não entram.
- Quantidades em Caixas fracionadas (Fracionamento) saem como número decimal na coluna `CAIXA`.
- A exportação registra a data no Pedido, e o Pedido continua editável (94).

## Erros (mensagens em português)

- Nenhum Pedido escolhido → `Escolha pelo menos um Pedido para exportar.`
- Pedido de outro Gestor → `Este Pedido é de outro Gestor.`
- Pedido sem nenhuma quantidade → `O Pedido do Fornecedor Alfa não tem nenhuma quantidade para exportar.`

## O que o teste precisa

- O Pedido é montado pelos casos de uso: o construtor do Catálogo fictício do Layout A, com desconto de 5% inventado; um Gestor com três Lojas, uma delas sem quantidade; uma observação.
- Uma forma de avaliar as fórmulas no teste (biblioteca de avaliação de fórmulas ou um avaliador mínimo só do teste), além de checar o texto das fórmulas.
- Nenhum fake da LLM.

## Fora deste ticket

- Vários Pedidos e blocos por desconto distinto (19).
- Oferta sem código, com a coluna `CÓD.` vazia (88): a Oferta sem código só existe a partir do ticket 35, que acrescenta esse critério à exportação.
- Desconto do arquivo de preços da linha, em vez do desconto do Catálogo (37).
- A exportação não é bloqueada por linha que deixou de ser vigente (40).
- Aparência idêntica, título da planilha, linha de preço médio e totais entre Lojas que existem na planilha da gestora mas não estão no spec nem no ADR-0004.
- Formato de cada Fornecedor; reimportar planilhas editadas (Out of Scope).
