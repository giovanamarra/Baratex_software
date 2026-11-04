# 05 — Preço unitário na Revisão, com o desconto das Condições do Catálogo

Status: ready-for-agent
Type: task
Blocked by: 04
Spec: [docs/spec.md](../../../docs/spec.md) (Modelo de dados › Preço unitário; Conteúdo e Preço unitário)
ADRs: ADR-0005 (fórmula, sem impostos). ADR-0002 está substituído: **não** somar IPI.
User stories: 23, 25, 37, 42, 47, 48

## O que entrega

A gestora informa o desconto daquele Catálogo e vê o Preço unitário de cada Oferta já na Revisão e, depois de confirmar, nas Ofertas do Catálogo.

## Critérios de aceite

- Toda Oferta proposta começa com Conteúdo 1 (42). Sem desconto, o Preço unitário é igual ao preço impresso.
- Informar as Condições do Catálogo (desconto em %) durante a Revisão recalcula todas as Ofertas:
  **Preço unitário = preço impresso × (1 − desconto) ÷ Conteúdo**, arredondado para centavos (meio centavo para cima).
  - Exemplo: preço impresso 10,00 com desconto de 10% → 9,00.
- Caixa e Embalagem intermediária nunca dividem o preço: uma Oferta de 12,00 com Caixa 48 e Embalagem intermediária 12 tem Preço unitário 12,00 (47).
- Um desconto já impresso no Catálogo não é aplicado de novo. Vale o preço impresso no cartão, e só o desconto informado pela gestora é aplicado: um cartão impresso a 8,00, sem desconto informado, dá 8,00 (25).
- Se o desconto for informado de novo, vale o último. Ao confirmar, ele fica guardado nas Condições do Catálogo.
- Impostos são ignorados: um cartão com alíquota impressa (ex.: "IPI 10%") tem o mesmo Preço unitário que teria sem ela, e a alíquota não é guardada nem exibida (48).
- Depois de confirmar, consultar as Ofertas de um Catálogo (a partir da lista de Catálogos do ticket 04) mostra o mesmo Preço unitário da Revisão.
- O Preço unitário é sempre derivado, nunca digitado nem gravado como valor independente.

## Erros (mensagens em português)

- Desconto negativo, de 100% ou mais, ou que não é número → `O desconto precisa ser de 0% até menos de 100%.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A, com um cartão que traz uma alíquota impressa inventada e um cartão com Caixa e Embalagem intermediária.
- Nenhum fake da LLM.

## Fora deste ticket

- Definir o Conteúdo (07). Catálogos com várias colunas de preço, que não pedem desconto (22).
