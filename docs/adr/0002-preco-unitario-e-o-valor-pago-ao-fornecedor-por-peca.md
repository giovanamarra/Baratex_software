---
status: superseded by ADR-0005
---

# Preço unitário é o valor pago ao Fornecedor por peça, dividido pelo Conteúdo e não pela Caixa

O briefing definia Preço unitário como "preço do item ÷ quantidade por embalagem". Nos catálogos reais, porém, a quantidade por embalagem impressa é quase sempre a Caixa ou uma Embalagem intermediária (dúzia, set, sub-caixa), e o preço impresso já se refere a uma única Unidade de venda. Dividir por ela daria preços dezenas de vezes menores que os reais, e quase toda Oferta pareceria abaixo do Teto de compra. Decidimos:

**Preço unitário = (preço impresso − desconto das Condições do Catálogo) + IPI destacado, dividido pelo Conteúdo.**

Isso é o que a gestora paga ao Fornecedor por peça: o valor total da nota fiscal, levado a uma peça.

## Regras

- Caixa e Embalagem intermediária nunca dividem o preço. Elas só definem a compra mínima.
- IPI destacado no Catálogo soma ao preço. Sem destaque, o preço impresso já inclui o IPI.
- O desconto é aplicado antes do IPI. É uma suposição a confirmar com uma nota fiscal real.
- Desconto já impresso no Catálogo não é aplicado de novo.
- Conteúdo é quantos itens a loja vende separadamente a partir de uma Unidade de venda, e não quantas peças há na embalagem. O padrão é 1: assim, o pior erro possível é um kit parecer caro, nunca parecer barato. Quando a descrição cita peças, o sistema sugere mudar o Conteúdo e a gestora decide. A decisão fica guardada por Fornecedor + código.
- Preço impresso, alíquota de IPI e desconto ficam guardados separadamente; o Preço unitário é derivado deles.

## Opções consideradas

- **Dividir pela quantidade por embalagem (briefing):** descartada, porque gera preços absurdos nos catálogos reais.
- **Preço unitário sem IPI, com um "Custo unitário" à parte:** bate com o número impresso, mas põe dois números na tela e convida a comparar o errado.
- **Incluir DIFAL e frete:** descartada. Não são pagos ao Fornecedor, não aparecem no Catálogo, e a alíquota de DIFAL pode variar por produto. Como todos os fornecedores atuais são de fora do estado, o DIFAL pesa de forma parecida em todos e não deve inverter comparações.

## Consequências

O Preço unitário não é o custo final da mercadoria na loja. Se algum dia entrar um Fornecedor do mesmo estado das lojas, a ausência de DIFAL passa a distorcer a comparação e esta decisão deve ser revista.
