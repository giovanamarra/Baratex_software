# 32 — Código repetido no mesmo Catálogo: agrupado na Revisão, vale o menor Preço unitário

Status: resolved
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

## Comments

**2026-11-05 — implementado por TDD** (commits `f5a4e41` a `c7ba172`, mais o commit deste comentário)

- **Posição no arquivo (decisão da usuária):** é o campo `ordem` que já existia na Oferta proposta e na Oferta. A Extração grava na ordem de leitura; a Oferta adicionada à mão recebe a última + 1. A confirmação agora leva a `ordem` da Oferta proposta até a Oferta do Catálogo (antes renumerava 0..n na ordem em que as Ofertas chegavam, e o agrupamento da Revisão teria trocado essa ordem). Sem campo nem migração novos para a posição.
- **Página de origem (decisão da usuária):** o leitor do Layout A grava `pagina` na `OfertaExtraida`, e ela vai para `OfertaProposta.pagina` (migração `importacao.0010_pagina_de_origem_da_oferta_proposta`, campo opcional). A Oferta do Catálogo não guarda a página neste ticket. Revisões em andamento de antes do ticket ficam sem página.
- **Revisão:** `Revisao.ofertas_propostas()` junta as Ofertas do mesmo código onde o código aparece primeiro, na ordem do arquivo, e conta `ofertas_com_o_mesmo_codigo`. A marca "código repetido" é derivada (sem coluna), também na Oferta sem preço, e não bloqueia. O código é comparado como guardado: sem espaços nas pontas (como já era) e diferenciando maiúsculas.
- **Tela:** na Revisão em andamento, uma linha de cabeçalho `Código repetido (N Ofertas)` no estilo de alerta (`tr.linha--grupo`, borda de alerta à esquerda) abre o grupo; cada linha do grupo mostra a marca em texto e, na coluna Caminho, `p. N` ou `adicionada à mão`.
- **Vigência** (`_que_vale_mais_que_esta`): dentro do mesmo Catálogo, ganha o menor Preço unitário e, empatado, a menor `ordem`. O Preço unitário é calculado na consulta, em centavos e só com inteiros (`_preco_unitario_em_centavos`), com o desconto do Catálogo e o Conteúdo guardado, meio centavo para cima (decisão da usuária: exato, não pelo preço impresso). Conferido fora da suíte contra `calcular_preco_unitario` em 200.000 casos aleatórios: nenhuma divergência.
- **Banco da desenvolvedora:** numa cópia do `db.sqlite3`, o conjunto de Ofertas vigentes é o mesmo com o código do fim do ticket 31 (`f6d60b7`) e com o deste ticket: 382 de 382. Os 2 Catálogos não têm código repetido, então a conferência não exercita o desempate novo.
- **Catálogos reais** (`ferramentas/conferir_catalogos_reais.py`, nova tabela "Código repetido no mesmo Catálogo"): 0 códigos repetidos em cada um dos 8 PDFs do Layout A (1.931 Ofertas).
- **Testes antigos que mudaram:** só `test_revisao_abre_e_mostra_as_ofertas_com_cada_marca_e_a_contagem`, que ganhou um código repetido (e a contagem passou a 10 preços × 9 Ofertas). Nenhum teste antigo contradizia a regra nova.

### Placar das mutações (todas mortas por FAIL)

Cada uma aplicada sozinha em `catalogos/casos_de_uso.py`, com a suíte inteira, e desfeita com `git checkout -- catalogos/casos_de_uso.py`. Nas que comparam Preço unitário entre Catálogos, cada lado usa o desconto do próprio Catálogo.

| # | Mutação | Testes que derrubou |
|---|---|---|
| M18 | sem desempate dentro do Catálogo | 5: os 4 de código repetido da busca e `test_o_codigo_repetido_nao_concorre_com_o_mesmo_codigo_de_um_catalogo_de_data_mais_antiga`. A primeira versão da mutação deixava um erro de sintaxe (não contou) e foi reescrita. |
| M19 | Preço unitário igual → a última do arquivo | 3: `…com_o_mesmo_preco_unitario_vale_a_que_aparece_primeiro_no_arquivo`, `…empata_no_preco_unitario_arredondado…`, `…empata_no_preco_unitario_com_o_desconto…` |
| M20 | vale a de maior Preço unitário | 2: `test_codigo_repetido_no_mesmo_catalogo_vale_a_oferta_de_menor_preco_unitario` e o de Catálogo mais antigo |
| M21 | menor Preço unitário também entre Catálogos da mesma data | 1: `test_na_mesma_data_vale_o_catalogo_confirmado_por_ultimo_mesmo_mais_caro` |
| M1 | mesma data → menor Preço unitário | 2: os dois de "mesma data" |
| M2 | mesma data → sem desempate | 3: os dois de "mesma data" e o de "só mês e ano = dia 1" |
| M3 | mesma data → confirmado primeiro | os mesmos 3 da M2 |
| M14 | mais recente pelo dia da Importação | 3, entre eles `test_catalogo_antigo_importado_depois_nao_derruba_a_oferta_do_catalogo_mais_recente` |
| M15 | só mês e ano = último dia do mês | 3 FAIL (busca e Revisão) e 1 ERROR, que não conta |
| M16 | compara só mês e ano, sem o dia | 2, entre eles `test_so_mes_e_ano_e_mais_antigo_que_um_dia_do_mesmo_mes_depois_do_dia_1` |
| M17 | data mais recente só ganha com Preço unitário ≤ | 7, entre eles `test_vale_a_oferta_do_catalogo_de_data_mais_recente_mesmo_com_o_preco_maior` |
