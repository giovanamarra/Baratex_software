# 31 — Data do Catálogo informada na Revisão e Oferta vigente pelo Catálogo mais recente

Status: resolved
Type: task
Blocked by: 04, 06, 09 (todos resolvidos)
Spec: [docs/spec.md](../../../docs/spec.md) (Revisão › Data do Catálogo, confirmação recusada; Modelo de dados › Catálogo, Catálogos já existentes, Oferta vigente)
ADRs: ADR-0009 (itens 1, 2, 4 e 5, primeira parte), ADR-0007
User stories: 15, 54, 55 (entre Catálogos), 57 (data do Catálogo), 58, 101, 102, 107 (na busca)
Muda código já feito: tickets 04 (data do Catálogo), 06 (nova recusa de confirmação) e 09 (regra de vigência). Esses tickets continuam resolvidos.

## O que entrega

A gestora diz, na Revisão, de quando é o Catálogo (data completa ou só mês e ano). A Oferta vigente passa a ser a do Catálogo de data mais recente, **mesmo que o preço tenha subido**. Um catálogo do mês anterior importado hoje não derruba o preço atual.

## Critérios de aceite

Data do Catálogo na Revisão (101, 102, 15)

- O campo "Data do Catálogo" começa vazio, com o atalho `É de hoje (dd/mm/aaaa)`, que preenche com o dia em que a Importação começou (não o dia da confirmação).
- Aceita `15/10/2026` (data completa), `10/2026` (só mês e ano) e `15/10/26` (ano com 2 dígitos = 20xx, guardado como 15/10/2026). Espaços nas pontas são ignorados.
- A data fica no rascunho da Revisão (sobrevive a um recarregamento) e pode ser trocada até confirmar. Informar de novo vale a última.
- A confirmação é recusada sem data do Catálogo (101). A recusa entra na mesma mensagem única das outras recusas da confirmação (ticket 06).
- Data depois de hoje é recusada; só mês e ano é recusado quando o mês é depois do mês atual (`11/2026` vale em 05/11/2026; `12/2026` não). Ano antes de 2000 é recusado (102).

Catálogo guardado (04, 58)

- O Catálogo guarda a **data do Catálogo** com a sua precisão (dia, mês e ano, ou só mês e ano) e, separado, o **dia da Importação**, só como registro.
- Na tela, a data do Catálogo aparece como foi informada: `15/10/2026` ou `10/2026`.
- A lista de Catálogos do Fornecedor mostra as duas datas ("Data do Catálogo" e "Importado em") e ordena pela data do Catálogo, da mais recente para a mais antiga; com a mesma data, o confirmado por último primeiro (58).
- Migração dos Catálogos que já existem: a data do Catálogo vira a data completa igual ao dia da Importação guardado hoje. Nenhuma Oferta vigente muda com a migração.

Oferta vigente entre Catálogos (54, 55)

- Para cada Fornecedor + código, vale a Oferta do Catálogo de **data do Catálogo** mais recente que tem esse código.
- **O preço subiu:** código 1001 no Catálogo de 01/10/2026 a 10,00 e no de 15/10/2026 a 11,00 → vigente a de 11,00 (54).
- **Catálogo antigo importado depois:** o Catálogo de 15/10/2026 é confirmado primeiro, e o de 01/09/2026 é importado e confirmado depois → continua vigente a Oferta do de 15/10/2026.
- **A substituição é código a código:** o Catálogo novo não tem o código 1002 → a Oferta 1002 do Catálogo anterior continua vigente.
- **Mesma data → vale o confirmado por último**, qualquer que seja o preço (55): dois Catálogos de 15/10/2026 com o código 1001, o primeiro confirmado a 9,90 e o segundo a 10,50 → vigente a de 10,50. A busca padrão devolve **uma** Oferta para o código.
- **Só mês e ano conta como o dia 1** daquele mês: `10/2026` é mais antigo que `15/10/2026` e tem a mesma data que `01/10/2026` (aí vale o confirmado por último).
- Quem é vigente é calculado na consulta, nunca gravado.

Busca (57, 107)

- Os resultados mostram a data do Catálogo como foi informada, e a ordem "Catálogo mais recente" da busca segue a data do Catálogo.
- O critério antigo do ticket 09 ("no mesmo dia vale o menor Preço unitário, 9,90 contra 10,50") deixa de valer. O teste correspondente (`test_no_mesmo_dia_vale_a_oferta_de_menor_preco_unitario_e_nao_a_de_menor_preco_impresso`) é reescrito para a regra nova, e não apagado sem substituto.

## Mutações que precisam morrer

As mutações M1, M2 e M3 sobreviveram de propósito na revisão dos tickets 09 e 10, porque a regra ia mudar. Com a regra nova, cada uma é lida assim, e todas precisam derrubar pelo menos um teste. Rode cada uma isolada (desfazendo com `git checkout -- <arquivo>`) e registre o placar em `## Comments`.

| # | Mutação no cálculo da Oferta vigente | Por que precisa morrer |
|---|---|---|
| M1 | Mesma data → vale a de **menor Preço unitário** (a regra antiga). Na revisão, M1 era o contrário ("vale o último confirmado"), que agora é a regra. | O confirmado por último ganha mesmo com preço maior. |
| M2 | Mesma data → **sem desempate** (as duas aparecem como vigentes). | A busca padrão mostraria o mesmo código duas vezes. |
| M3 | Mesma data → vale o Catálogo **confirmado primeiro**. | Inverte a regra 2 do ADR-0009. |
| M14 | "Mais recente" pelo **dia da Importação**, não pela data do Catálogo. | Um catálogo antigo importado hoje viraria vigente. |
| M15 | Só mês e ano conta como o **último dia** do mês. | `10/2026` passaria na frente de `15/10/2026`. |
| M16 | Compara só mês e ano, **ignorando o dia**. | `15/10/2026` e `01/10/2026` empatariam. |
| M17 | Data mais recente ganha **só se o Preço unitário for menor ou igual**. | O preço que subiu não substituiria o anterior. |

Para M1, M2 e M3 morrerem com um só teste, use o caso da "mesma data" acima (o primeiro confirmado é o mais barato). Para M2 e M3 morrerem mesmo com o Preço unitário igual, acrescente um caso com dois Catálogos da mesma data e o mesmo preço, diferenciados pela Caixa.

## Erros (mensagens em português)

- Confirmar sem data → `Informe de quando é este Catálogo antes de confirmar.`
- Formato que não é dia/mês/ano nem mês/ano, ou data que não existe (31/02/2026, 13/2026) → `Informe a data do Catálogo como dia/mês/ano ou mês/ano, por exemplo 15/10/2026 ou 10/2026.`
- Depois de hoje → `A data do Catálogo não pode ser depois de hoje.`
- Ano antes de 2000 → `Confira o ano da data do Catálogo.`
- As recusas de Revisão de outro Gestor ou já confirmada valem também para informar a data.

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A e o auxiliar de importar e confirmar dos testes da busca, agora com a data do Catálogo como parâmetro, separada do dia da Importação (`hoje=`).
- Controle do dia no teste, para "hoje" nas recusas de data futura.
- Uma migração testada: um Catálogo criado no formato antigo ganha a data completa igual ao dia da Importação.
- Nenhum fake da LLM.

## Fora deste ticket

- Aviso de Catálogo mais antigo e correção da data depois de confirmada (33).
- Código repetido dentro do mesmo Catálogo (32).
- Desconto por arquivo de preços (37).
- Data do Catálogo na comparação (13), ao incluir no Pedido (15) e nas linhas do Pedido (16); linha do Pedido que deixou de ser vigente (40).
- Histórico de preço pela data do Catálogo (28).
- Data do Catálogo futura (Out of Scope).

## Comments

**2026-11-05 — implementado por TDD** (commits `7179139` a `4dc08af`, mais o commit deste comentário)

- **Data do Catálogo na Revisão:** `informar_data_do_catalogo(gestor, revisao_id, texto, hoje=None)` em `importacao/casos_de_uso.py`. O texto é lido por `data_do_catalogo_digitada(texto, hoje)` em `catalogos/casos_de_uso.py`, para o ticket 33 reaproveitar na correção da data. A Revisão guarda `data_do_catalogo` e `data_do_catalogo_so_mes_e_ano`. Só mês e ano fica como o dia 1. A tela mostra o campo junto do desconto e o atalho `É de hoje (dd/mm/aaaa)`, que envia `iniciada_em` pela mesma rota (`informar_data_do_catalogo`).
- **Catálogo:** `data` (a data do Catálogo, que é a que vale), `data_so_mes_e_ano` e `importado_em` (dia em que a Importação começou, só registro). `data_exibida` mostra 15/10/2026 ou 10/2026, na lista, na busca, na página do Catálogo, na mensagem de confirmação e na Revisão confirmada.
- **Migrações:** `importacao.0009_data_do_catalogo_na_revisao`, `catalogos.0012_data_do_catalogo_e_dia_da_importacao` e `catalogos.0013_dia_da_importacao_dos_catalogos_existentes` (copia `data` para `importado_em`; a data do Catálogo continua a mesma data completa). Testada com o MigrationExecutor e conferida numa cópia do db.sqlite3 da desenvolvedora: o mesmo conjunto de Ofertas vigentes antes e depois (382 de 382). Nessa cópia, nenhum código se repete entre os 2 Catálogos.
- **Vigência** (`_que_vale_mais_que_esta`): data do Catálogo mais recente; na mesma data, o maior pk de Catálogo, que é o confirmado por último, porque o Catálogo é criado na confirmação.
- **Pendente para o ticket 32 (decisão da usuária):** o desempate antigo pelo menor Preço unitário saiu. Até o 32, um código repetido **no mesmo Catálogo** aparece duas vezes como vigente na busca padrão.
- **Testes antigos que mudaram:** os que confirmam passaram a informar a data com o auxiliar `informar_data_de_hoje` (como o atalho); `test_data_do_catalogo_e_o_dia_em_que_a_importacao_comecou` (04) virou `test_o_catalogo_guarda_a_data_informada_com_a_precisao_dela_e_separado_o_dia_da_importacao`; `test_no_mesmo_dia_vale_a_oferta_de_menor_preco_unitario_e_nao_a_de_menor_preco_impresso` (09) virou `test_na_mesma_data_vale_o_catalogo_confirmado_por_ultimo_mesmo_mais_caro`; `test_a_busca_padrao_mostra_so_a_oferta_do_catalogo_mais_recente_do_fornecedor` só trocou de nome (`test_vale_a_oferta_do_catalogo_de_data_mais_recente_mesmo_com_o_preco_maior`); os testes de tela da Revisão, da lista de Catálogos e da busca cobrem a data nova.

### Placar das mutações (todas mortas)

Cada uma aplicada sozinha em `catalogos/casos_de_uso.py`, com a suíte inteira rodando, e desfeita com `git checkout -- catalogos/casos_de_uso.py`.

| # | Mutação | Resultado | Testes que derrubou |
|---|---|---|---|
| M1 | mesma data → menor Preço unitário | morta | `test_na_mesma_data_vale_o_catalogo_confirmado_por_ultimo_mesmo_mais_caro`, `test_na_mesma_data_e_com_o_mesmo_preco_vale_o_catalogo_confirmado_por_ultimo` |
| M2 | mesma data → sem desempate | morta | os dois acima e `test_so_mes_e_ano_tem_a_mesma_data_que_o_dia_1_e_vale_o_confirmado_por_ultimo` |
| M3 | mesma data → confirmado primeiro | morta | os mesmos três da M2 |
| M14 | mais recente pelo dia da Importação | morta | `test_catalogo_antigo_importado_depois_nao_derruba_a_oferta_do_catalogo_mais_recente`, `test_so_mes_e_ano_e_mais_antigo_que_um_dia_do_mesmo_mes_depois_do_dia_1` |
| M15 | só mês e ano = último dia do mês | morta | os dois testes de "só mês e ano" da busca (FAIL) e dois da Revisão |
| M16 | compara só mês e ano, sem o dia | morta | `test_so_mes_e_ano_e_mais_antigo_que_um_dia_do_mesmo_mes_depois_do_dia_1` (FAIL). A primeira versão da mutação quebrava a consulta (`TruncMonth` sobre `OuterRef`); foi reescrita anotando `mes` na consulta de fora. |
| M17 | data mais recente só ganha com Preço unitário ≤ | morta | 6 testes, entre eles `test_vale_a_oferta_do_catalogo_de_data_mais_recente_mesmo_com_o_preco_maior` |

