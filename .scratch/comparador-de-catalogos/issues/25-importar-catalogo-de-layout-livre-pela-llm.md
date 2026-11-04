# 25 — Importar um Catálogo de layout livre ou só imagem pela LLM

Status: ready-for-agent
Type: task
Blocked by: 06, 24
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Escolha do caminho, LLM com visão; Testing Decisions › único fake)
ADRs: ADR-0006 (caminho 3), ADR-0008 (interface trocável "ler página → Ofertas propostas")
User stories: 14 (imagem), 16, 20, 22, 27

## O que entrega

Catálogos que nenhum leitor determinístico entende passam a entrar no sistema: as páginas são lidas pela LLM com visão e propostas na Revisão. Este ticket usa só o fake da LLM. O adaptador real é o ticket 27.

## Critérios de aceite

- Existe a interface "ler página → Ofertas propostas". Os testes usam um fake com respostas fixas por página.
- Escolha do caminho (16):
  - PDF sem texto selecionável → cada página é transformada em imagem e lida pela LLM;
  - imagem (PNG, JPG) → uma página, lida pela LLM;
  - PDF com texto, sem Layout reconhecido, sem mapeamento de tabela e sem indicação de tabela → LLM. Isso substitui a mensagem provisória do ticket 03.
- Cada Oferta proposta tem caminho "LLM" e a página de origem (27).
- As imagens das páginas ficam guardadas (para sempre), para a conferência do ticket 26.
- A contagem de preços não existe nesse caminho. A Revisão diz `Contagem de preços não disponível para Ofertas lidas pela LLM.`
- O desconto das Condições do Catálogo é pedido como no ticket 05. As marcas do ticket 08 valem para essas Ofertas.
- Se o ticket 24 decidir por um worker em segundo plano, este ticket é ajustado antes da sessão de TDD.

## Erros (mensagens em português)

- O fake devolve uma resposta fora do formato numa página → a Revisão mostra, para aquela página: `Não consegui ler a página 3: a resposta veio fora do formato esperado. Adicione à mão as Ofertas dessa página ou recomece a Importação.` Nenhuma Oferta sai dessa página; as outras páginas seguem normais. Uma resposta inválida nunca vira Oferta silenciosa.
- O fake simula o serviço fora do ar → `Não consegui falar com o serviço de leitura de Catálogos. Nada foi salvo; tente de novo em alguns minutos.` (22)
- Nenhuma página com preço → `Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.`

## O que o teste precisa

- **Fake da LLM**: um dicionário página → resposta, com respostas válidas, uma inválida (campo de preço ausente ou estrutura quebrada) e uma exceção de serviço indisponível.
- PDF fictício sem texto selecionável (páginas só com imagem), gerado no teste; uma imagem PNG fictícia; um PDF com texto que não corresponde a nenhum Layout.
- Nenhum teste chama a API real.

## Fora deste ticket

- A conferência obrigatória por página (26). O adaptador real do Claude Haiku (27).
