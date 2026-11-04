---
status: accepted
---

# Preço unitário usa só o preço impresso, sem impostos, e divide pelo Conteúdo

Substitui o ADR-0002, que somava o IPI destacado ao Preço unitário. O papel da gestora no sistema é **selecionar mercadoria**; a triagem fiscal acontece depois, feita pela contabilidade da empresa, que calcula IPI, ICMS e DIFAL. Decidimos que o sistema ignora qualquer imposto:

**Preço unitário = preço impresso × (1 − desconto%) ÷ Conteúdo**, arredondado para centavos (meio centavo para cima).

## Regras que continuam valendo do ADR-0002

- Caixa e Embalagem intermediária nunca dividem o preço; elas só definem a compra mínima. Dividir por elas, como sugeria o briefing, gera preços dezenas de vezes menores que os reais.
- Conteúdo é quantos itens a loja vende separadamente a partir de uma Unidade de venda. O padrão é 1, para que o pior erro possível seja um kit parecer caro, nunca parecer barato. A decisão fica guardada por Fornecedor + código.
- Desconto já impresso no Catálogo não é aplicado de novo.

## Opções consideradas

- **Somar o IPI destacado (ADR-0002):** fica mais perto do valor pago ao Fornecedor, mas mistura no sistema uma responsabilidade que é da contabilidade.
- **Ignorar impostos (escolhida):** é mais simples e corresponde ao trabalho real da gestora.

## Consequências

Fornecedores que destacam IPI parecem mais baratos do que os que já o embutem no preço; na amostra, a diferença chega a 15%. Uma Oferta abaixo do Teto de compra pode acabar acima dele depois da triagem fiscal. Essa diferença é aceita. A alíquota impressa no Catálogo não é exibida nem usada no MVP.

Atualizado em 2026-11-04: o desconto das Condições do Catálogo é percentual, como na planilha de Pedido da gestora (ticket 05).
