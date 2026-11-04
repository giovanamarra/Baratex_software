# 24 — Investigação: tempo e custo por página da LLM com visão

Status: ready-for-agent
Type: research
Blocked by: —
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › LLM com visão); [C4 Container](../../../docs/architecture/c4-2-container.md) (pergunta em aberto sobre o worker)
ADRs: ADR-0006, ADR-0008 (prevê mover a leitura para segundo plano se ficar lenta)
User stories: nenhuma diretamente; decide o desenho dos tickets 25 e 27

## Pergunta

Ler um Catálogo de dezenas de páginas com o Claude Haiku cabe numa requisição web da Importação, ou é preciso um worker em segundo plano? Quanto custa cada página e cada Catálogo?

## Método

- Gerar Catálogos fictícios de três tipos, com dados inventados e conhecidos de antemão:
  1. grade densa de cartões só como imagem (sem texto selecionável);
  2. layout livre, com Ofertas espalhadas, preços em destaque e textos decorativos;
  3. página fotografada ou escaneada (inclinada, com ruído).
  Nenhum Catálogo real é enviado.
- Um script descartável, fora da suíte de testes, chama o Claude Haiku (modelo e chave da configuração, ADR-0008) com saída estruturada "página → Ofertas propostas", em pelo menos 10 páginas de cada tipo.
- Medir por página: tempo de resposta (mediana e máximo), tokens de entrada e de saída, custo pelo preço publicado no dia e acertos contra os dados conhecidos (Ofertas encontradas e preços errados, principalmente os errados que parecem plausíveis).
- Testar duas resoluções de imagem, para ver a troca entre custo e acerto.
- Estimar o tempo e o custo de um Catálogo de 50 páginas, lido em sequência e com um paralelismo pequeno.

## Critério de decisão (proposta, a confirmar com a gestora)

- A aplicação roda no computador da gestora, então não há tempo-limite de proxy. O limite é a paciência dela.
- Se um Catálogo de 50 páginas levar **mais de 2 minutos**, mesmo com paralelismo pequeno → worker em segundo plano. Nesse caso: abrir um ticket novo, sugerir um ADR (novo container no C4) e ajustar o ticket 25.
- Caso contrário → leitura dentro da requisição, como o C4 inferiu.

## Saída esperada

- Anexar a este arquivo, em `## Answer`: a tabela de medidas, o custo estimado por Catálogo, a decisão sobre o worker e o prompt e o esquema de saída que funcionaram melhor (insumo do ticket 27).
- Atualizar `Status: resolved`.

## Regras

- Nenhum teste automatizado chama a API real. O script não roda com `manage.py test`.
- A chave fica no arquivo de ambiente, nunca no repositório.
- Antes de escrever o script, consulte a skill `claude-api` para o identificador do modelo e o SDK atuais.
