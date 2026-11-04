# 05 — Preço unitário na Revisão, com o desconto das Condições do Catálogo

Status: resolved
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

## Comments

**2026-11-04 — implementado por TDD** (commits `7419901` a `c105a02`)

- **Cálculo:** `catalogos/preco_unitario.py` (`calcular_preco_unitario`), só Decimal, `ROUND_HALF_UP` em centavos. Derivado: `OfertaProposta.preco_unitario` (desconto da Revisão) e `Oferta.preco_unitario` (desconto do Catálogo); nenhuma coluna no banco. Conteúdo é a constante 1 até o ticket 07.
- **Casos de uso:** `informar_condicoes_do_catalogo(gestor, revisao_id, desconto)` (texto como a gestora digita, vírgula ou ponto; mesmas recusas de Revisão de outro Gestor ou já confirmada); `obter_catalogo(gestor, catalogo_id)` (qualquer Gestor, ADR-0007). `registrar_catalogo` recebe o desconto.
- **Condições do Catálogo:** `desconto` percentual na Revisão e no Catálogo, guardado como digitado (até 4 casas, sem arredondar); vazio = sem desconto.
- **Arredondamento:** 9,99 com 3% → 9,69; 0,50 com 3% → 0,49 (com arredondamento bancário daria 0,48; provado com mutação).
- **História 47:** só a Caixa é testada; o Layout A não tem Embalagem intermediária (decisão do ticket 03).
- **História 25** (decisão da usuária): testada como "o desconto é aplicado uma vez só sobre o preço impresso" (8,00 com 10% informado duas vezes continua 7,20); o Layout A não tem desconto impresso.
- **História 48:** os cartões reais do Layout A trazem "+ N% ipi" ou "sem ipi"; o construtor já tinha o campo e o leitor já o ignorava. A alíquota não é guardada nem exibida.
- **Erro:** campo vazio também é recusado (não é número); para tirar o desconto, a gestora informa 0.
- **Telas:** campo "Desconto do Catálogo (%)" + "Recalcular" na Revisão; coluna Preço unitário ao lado do preço impresso; página do Catálogo (`/catalogos/<id>/`) com o desconto no topo, aberta pela lista de Catálogos; tabela de Ofertas compartilhada pelas duas telas.
