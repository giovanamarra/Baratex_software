# 25 — Importar um Catálogo de layout livre ou só imagem pela LLM

Status: ready-for-agent
Type: task
Blocked by: 06, 24, 36, 38
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Escolha do caminho, LLM com visão, Foto, Catálogo sem preço; Catálogo em mais de um arquivo › Ligação da foto; Testing Decisions › único fake)
ADRs: ADR-0006 (caminho 3), ADR-0008 (interface trocável "ler página → Ofertas propostas"), ADR-0010 (itens 2 e 5: sem preço pela leitura; marca da página), ADR-0011 (item 1: área da foto devolvida pela LLM)
User stories: 14 (imagem), 16, 20, 22, 27, 111 (dentro da marca da página), 116 (LLM)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

Catálogos que nenhum leitor determinístico entende passam a entrar no sistema: as páginas são lidas pela LLM com visão e propostas na Revisão, com a foto de cada item recortada da página. Um PDF só com fotos e descrições, lido pela LLM, vira um Catálogo sem preço que pede a planilha de preços. Este ticket usa só o fake da LLM. O adaptador real é o ticket 27.

## Critérios de aceite

- Existe a interface "ler página → Ofertas propostas". Os testes usam um fake com respostas fixas por página.
- A resposta de cada página traz, por item: código (opcional), descrição, preço (**pode vir ausente**), Caixa e a **área da foto** na página (quando houver); e, por página, a **marca** indicada (quando houver).
- Escolha do caminho (16):
  - PDF sem texto selecionável → cada página é transformada em imagem e lida pela LLM;
  - imagem (PNG, JPG) → uma página, lida pela LLM;
  - PDF com texto, sem Layout reconhecido, sem mapeamento de tabela que sirva e sem indicação de tabela → LLM. Isso substitui a mensagem provisória do ticket 03.
- Cada Oferta proposta tem caminho "LLM" e a página de origem (27).
- As imagens das páginas ficam guardadas (para sempre), para a conferência do ticket 26.
- **Foto** (116): a área devolvida é recortada da imagem da página e guardada como no ticket 14 (reduzida, pela impressão digital). Item sem área → Oferta sem foto, sem marca. Uma área fora da página ou vazia não vira foto, e não é erro.
- **Sem preço** (ADR-0010, item 2): a LLM achou produtos e nenhum preço em nenhuma página → Catálogo sem preço, e a Importação exige a planilha de preços (ticket 36). Alguns itens sem preço → Revisão normal, com a Oferta sem preço bloqueando.
- **Ligação dentro da marca da página** (111; decisão da usuária, 2026-11-05): quando há planilha de preços e o arquivo do Catálogo traz a marca da página, a ligação por descrição do ticket 38 compara primeiro "marca da página + descrição do item" (normalizada) com a descrição da planilha, em que a coluna da marca entra primeiro no mapeamento. Se não achar, compara só a descrição. Nos dois casos o texto precisa ser **igual e único** dos dois lados; no arquivo do Catálogo, a unicidade é contada dentro da marca.
  - Exemplo: `Biscoito Leite 200g` na página da marca `FORN` e também na da marca `GAMA`; a planilha tem `FORN Biscoito Leite 200g` e `GAMA Biscoito Leite 200g` → cada foto vai para a sua Oferta.
  - Sem marca na página, vale a regra do ticket 38 como está.
- A contagem de preços não existe nesse caminho. A Revisão diz `Contagem de preços não disponível para Ofertas lidas pela LLM.`
- O desconto das Condições do Catálogo é pedido como nos tickets 05 e 37, e a data como no ticket 31. As marcas do ticket 08 e o código repetido do ticket 32 valem para essas Ofertas.
- Se o ticket 24 decidir por um worker em segundo plano, este ticket é ajustado antes da sessão de TDD.

## Erros (mensagens em português)

- O fake devolve uma resposta fora do formato numa página → a Revisão mostra, para aquela página: `Não consegui ler a página 3: a resposta veio fora do formato esperado. Adicione à mão as Ofertas dessa página ou recomece a Importação.` Nenhuma Oferta sai dessa página; as outras páginas seguem normais. Uma resposta inválida nunca vira Oferta silenciosa. Preço ausente **não** é resposta inválida.
- O fake simula o serviço fora do ar → `Não consegui falar com o serviço de leitura de Catálogos. Nada foi salvo; tente de novo em alguns minutos.` (22)
- Produtos e nenhum preço → `Este arquivo não tem preços. Envie a planilha de preços para continuar.` (ticket 36; substitui `Este documento não tem preços, então não é um Catálogo...`)

## O que o teste precisa

- **Fake da LLM**: um dicionário página → resposta, com respostas válidas (com e sem área da foto, com e sem marca, com e sem preço), uma inválida (estrutura quebrada) e uma exceção de serviço indisponível.
- PDF fictício sem texto selecionável (páginas só com imagem, com quadrados coloridos nas áreas das fotos), gerado no teste; uma imagem PNG fictícia; um PDF com texto que não corresponde a nenhum Layout.
- Uma planilha de preços fictícia com a coluna de marca e a descrição repetida em duas marcas.
- Nenhum teste chama a API real.

## Fora deste ticket

- A conferência obrigatória por página, com as fotos recortadas (26). O adaptador real do Claude Haiku (27).
