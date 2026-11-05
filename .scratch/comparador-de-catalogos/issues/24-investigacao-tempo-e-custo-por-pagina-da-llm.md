# 24 — Investigação: tempo e custo por página da LLM com visão

Status: ready-for-agent
Type: research
Blocked by: —
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › LLM com visão; Further Notes › mudança de requisito de 2026-11-05); [C4 Container](../../../docs/architecture/c4-2-container.md) (pergunta em aberto sobre o worker)
ADRs: ADR-0006, ADR-0008 (prevê mover a leitura para segundo plano se ficar lenta), ADR-0010 (PDF só com fotos e descrições), ADR-0011 (área da foto devolvida pela LLM)
User stories: nenhuma diretamente; decide o desenho dos tickets 25 e 27
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## Pergunta

Ler um Catálogo de dezenas de páginas com o Claude Haiku cabe numa requisição web da Importação, ou é preciso um worker em segundo plano? Quanto custa cada página e cada Catálogo, agora que a LLM também devolve a área da foto e a marca de cada página?

## Método

- Gerar Catálogos fictícios de quatro tipos, com dados inventados e conhecidos de antemão:
  1. grade densa de cartões só como imagem (sem texto selecionável);
  2. layout livre, com Ofertas espalhadas, preços em destaque e textos decorativos;
  3. página fotografada ou escaneada (inclinada, com ruído);
  4. **PDF só com fotos e descrições, sem preço e sem código**, com a marca no canto da página e muitas fotos por página, imitando a estrutura do caso real que motivou o ADR-0010 (48 páginas, cerca de 2.100 imagens). Só a estrutura; nada do real.
  Nenhum Catálogo real é enviado.
- Um script descartável, fora da suíte de testes, chama o Claude Haiku (modelo e chave da configuração, ADR-0008) com saída estruturada "página → Ofertas propostas", em pelo menos 10 páginas de cada tipo. Para cada item, a saída inclui: código (opcional), descrição, preço (pode vir ausente), Caixa, **área da foto na página** (quando houver) e, por página, a **marca** indicada (quando houver).
- Medir por página: tempo de resposta (mediana e máximo), tokens de entrada e de saída, custo pelo preço publicado no dia e acertos contra os dados conhecidos (Ofertas encontradas e preços errados, principalmente os errados que parecem plausíveis).
- Medir a área da foto: em quantos itens o recorte contém a foto certa, em quantos pega a do vizinho, e quanto a área aumenta a resposta (tokens e custo) em relação à mesma página sem pedir a área.
- Medir a marca da página: em quantas páginas ela vem certa.
- Testar duas resoluções de imagem, para ver a troca entre custo e acerto (inclusive do recorte).
- Estimar o tempo e o custo de um Catálogo de 50 páginas, lido em sequência e com um paralelismo pequeno, e do PDF só de fotos de 48 páginas.

## Critério de decisão (proposta, a confirmar com a gestora)

- A aplicação roda no computador da gestora, então não há tempo-limite de proxy. O limite é a paciência dela.
- Se um Catálogo de 50 páginas levar **mais de 2 minutos**, mesmo com paralelismo pequeno → worker em segundo plano. Nesse caso: abrir um ticket novo, sugerir um ADR (novo container no C4) e ajustar o ticket 25.
- Caso contrário → leitura dentro da requisição, como o C4 inferiu.
- Se o recorte errar a foto em muitos itens, registrar a taxa: a conferência por página (ticket 26) é a proteção, e a gestora decide se vale a pena.

## Saída esperada

- Anexar a este arquivo, em `## Answer`: a tabela de medidas (com a área da foto e a marca), o custo estimado por Catálogo e do PDF só de fotos, a decisão sobre o worker e o prompt e o esquema de saída que funcionaram melhor (insumo dos tickets 25 e 27).
- Atualizar `Status: resolved`.

## Regras

- Nenhum teste automatizado chama a API real. O script não roda com `manage.py test`.
- A chave fica no arquivo de ambiente, nunca no repositório.
- Antes de escrever o script, consulte a skill `claude-api` para o identificador do modelo e o SDK atuais.
