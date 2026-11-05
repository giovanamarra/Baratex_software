# 21 — Importar um Catálogo em tabela Excel, com o mapeamento de colunas no Perfil do Fornecedor

Status: ready-for-agent
Type: task
Blocked by: 06, 17, 35
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Escolha do caminho, Tabela; Modelo de dados › Perfil do Fornecedor, Código; Casos de uso › informar mapeamento de colunas)
ADRs: ADR-0006 (caminho 2), ADR-0010 (itens 7 e 8: código opcional, descrição em várias colunas, vários mapeamentos), ADR-0007 (alteração do Perfil com autor e data)
User stories: 11, 13 (mapeamento), 14 (Excel), 17 (Excel), 18, 33 (tabela), 114 (mapeamento sem coluna de código)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora importa a planilha Excel de um Fornecedor. Na primeira vez de cada formato de planilha, ela indica quais colunas são código (se houver), descrição, preço e Caixa. Nas Importações seguintes, o sistema reconhece a planilha pelos cabeçalhos e já sabe lê-la, mesmo quando o Fornecedor alterna entre planilhas diferentes. O mesmo leitor é usado depois para as planilhas de preços (ticket 36).

## Critérios de aceite

Mapeamento (18, 114)

- Iniciar a Importação com um .xlsx de um Fornecedor sem mapeamento que sirva faz a Importação pedir o mapeamento, mostrando os cabeçalhos encontrados (18).
- O mapeamento indica, pelo texto do cabeçalho: **código (opcional)**, **descrição (uma ou mais colunas, em ordem)**, preço e Caixa.
- A descrição de várias colunas é o texto das colunas juntado na ordem indicada, separado por espaço, sem as células vazias. Exemplo: marca `FORN`, descrição `Biscoito Leite`, sabor (vazio), gramatura `200g` → `FORN Biscoito Leite 200g`.
- Sem coluna de código, a Oferta fica sem código e a descrição normalizada faz o papel de código (ticket 35) (114).
- Só as colunas marcadas como preço contam: uma coluna de preço sugerido de venda, não marcada, é ignorada.

Leitura (17, 33)

- Informar o mapeamento gera a Revisão com uma Oferta por linha que tem preço, com o caminho "tabela" (17).
- Linhas de título, linhas em branco e subtítulos de seção (sem preço) são ignorados.
- Uma linha com a Caixa vazia gera uma Oferta sem Caixa, que bloqueia a confirmação (ticket 06).
- Contagem (33): a Revisão mostra "Preços no arquivo: N · Ofertas extraídas: M", em que N é o número de linhas com valor na coluna de preço.
- O desconto das Condições do Catálogo é pedido como no ticket 05, e a data do Catálogo como no ticket 31.
- A mensagem provisória do ticket 03 para Excel deixa de valer.

Vários mapeamentos no Perfil (11, 13)

- Ao confirmar, o mapeamento novo é **acrescentado** ao Perfil do Fornecedor, junto dos que já existem, com Gestor e data no histórico do Perfil (11, 13).
- Numa Importação, vale o mapeamento guardado cujas colunas existem **todas** nos cabeçalhos da planilha. Se nenhum servir, a gestora indica um novo.
- Exemplo: o Fornecedor Alfa tem a planilha principal (`CÓDIGO`, `DESCRIÇÃO`, `PREÇO`, `CX`) e a de promoção (`PRODUTO`, `SABOR`, `VALOR PROMO`, `EMB`). Depois de mapear cada uma uma vez, as duas vão direto para a Revisão nas próximas Importações (11).
- Se mais de um mapeamento servir, vale o que tem mais colunas, e no empate o guardado por último (regra proposta, para o resultado ser sempre o mesmo).

## Erros (mensagens em português)

- Mapeamento sem coluna de preço → `Indique a coluna de preço.`
- Mapeamento sem coluna de descrição → `Indique a coluna de descrição (uma ou mais).` (substitui `Indique as colunas de código e de descrição.`, porque o código passou a ser opcional)
- A mesma coluna em dois papéis (por exemplo, preço e Caixa) → `A coluna "PREÇO" foi indicada em mais de um papel.` (texto proposto)
- Planilha sem nenhum preço numérico → a recusa atual do ticket 03 (`Este documento não tem preços...`), até o ticket 36 trocá-la pelo pedido de planilha de preços.
- Arquivo .xls antigo → `Formato .xls não aceito. Abra no Excel e salve como .xlsx.`

## O que o teste precisa

- **Catálogo fictício em tabela Excel**, gerado no teste: uma linha de título, uma linha de cabeçalho, de 6 a 10 linhas de Ofertas inventadas, uma linha de subtítulo de seção e uma linha sem Caixa.
- Uma segunda planilha fictícia do mesmo Fornecedor, com outros cabeçalhos, sem coluna de código e com a descrição em três colunas, uma delas às vezes vazia.
- Nenhum fake da LLM.

## Fora deste ticket

- Várias colunas de preço (22). PDF em tabela e correção do mapeamento (23).
- A planilha como planilha de preços de um Catálogo (36, 37).
- Foto ancorada na linha do Excel (39).
