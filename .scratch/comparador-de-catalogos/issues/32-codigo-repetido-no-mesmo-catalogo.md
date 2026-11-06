# 32 — Código repetido no mesmo Catálogo: agrupado na Revisão, vale o menor Preço unitário

Status: claimed
Type: task
Blocked by: 31
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › Código repetido; Extração › marcas de conferência; Modelo de dados › Oferta: posição no arquivo, Oferta vigente)
ADRs: ADR-0009 (item 3)
User stories: 55 (dentro do Catálogo), 106
Muda código já feito: tickets 08 (marca nova, que não bloqueia) e 09 (desempate da vigência dentro do Catálogo). Esses tickets continuam resolvidos.

## O que entrega

Quando o mesmo código aparece mais de uma vez no Catálogo (o mesmo item em duas seções, ou um erro de leitura), a Revisão mostra as Ofertas lado a lado para a gestora remover as erradas. Se ela não remover, vale a de menor Preço unitário.

## Critérios de aceite

Na Revisão (106)

- As Ofertas propostas com o mesmo código ficam agrupadas, sob `Código repetido (N Ofertas)`, lado a lado, com descrição, preço impresso, Preço unitário, Caixa e página de origem (e a foto, quando o ticket 14 existir).
- Cada Oferta do grupo tem a marca "código repetido". A marca **não bloqueia** a confirmação.
- Remover uma das duas tira o agrupamento e a marca da que ficou. A marca é recalculada depois de cada correção: corrigir o código de uma delas também desfaz o grupo.
- O código é comparado como guardado (sem espaços nas pontas). Códigos diferentes só em maiúsculas não são o mesmo código.

Depois de confirmar (55)

- Todas as Ofertas repetidas entram no Catálogo (nada é descartado sem a gestora remover).
- A Oferta vigente do código, dentro desse Catálogo, é a de **menor Preço unitário**. Com Preço unitário igual, vale a que aparece **primeiro no arquivo**.
- A Oferta guarda a sua posição no arquivo (ordem de leitura). Uma Oferta adicionada à mão fica depois das extraídas, na ordem em que foi adicionada.
- A regra entre Catálogos do ticket 31 vem antes: o código repetido num Catálogo de 15/10/2026 não concorre com o mesmo código de um Catálogo de 01/10/2026; o de 01/10 nunca é vigente.
- A busca padrão devolve uma única Oferta vigente por Fornecedor + código; com "Mostrar também Ofertas antigas", mostra as repetidas.

## Mutações que precisam morrer

| # | Mutação | Por que precisa morrer |
|---|---|---|
| M18 | Código repetido no mesmo Catálogo → sem desempate (as duas aparecem como vigentes). | Mesmo código duas vezes na busca. |
| M19 | Preço unitário igual → vale a **última** do arquivo. | Contraria o ADR-0009, item 3. |
| M20 | Vale a de **maior** Preço unitário. | Contraria o ADR-0009, item 3. |
| M21 | Desempate por menor Preço unitário aplicado também **entre Catálogos da mesma data**. | Volta a regra antiga (é a M1 do ticket 31, vista daqui). |

Neste ticket, dentro de um Catálogo, o desconto e o Conteúdo são os mesmos para todas as Ofertas de um código, então "desempate pelo preço impresso" ainda não pode morrer. Ele morre no ticket 37, em que cada planilha tem o seu desconto.

## Erros (mensagens em português)

- Nenhum erro novo: o código repetido é uma marca de conferência, não uma recusa.

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A com o mesmo código em dois cartões (preços diferentes, e outro caso com preço igual e Caixa diferente), em páginas diferentes.
- Nenhum fake da LLM.

## Fora deste ticket

- Código repetido entre planilhas de preços do mesmo Catálogo, com desconto por arquivo (37).
- Descrição repetida quando a Oferta não tem código (35: a mesma regra passa a valer pela descrição normalizada).
