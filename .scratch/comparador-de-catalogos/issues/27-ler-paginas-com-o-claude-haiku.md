# 27 — Ler páginas com o Claude Haiku

Status: ready-for-agent
Type: task
Blocked by: 24, 25
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › LLM com visão: modelo e chave da configuração; resposta estruturada e validada)
ADRs: ADR-0008 (Claude Haiku atrás de interface trocável), ADR-0006 (envio autorizado; testes sem API real), ADR-0010 e ADR-0011 (preço opcional, marca da página e área da foto na resposta)
User stories: 20, 22, 116 (LLM, com a chave real)
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A leitura por LLM passa a funcionar de verdade no computador da gestora, com o Claude Haiku, atrás da mesma interface que os testes usam com o fake.

## Critérios de aceite

- Um adaptador real implementa a interface "ler página → Ofertas propostas" do ticket 25, usando o Claude Haiku.
- O modelo e a chave da API vêm da configuração (arquivo de ambiente do ticket 11), nunca do código.
- A resposta é pedida em formato estruturado e passa pela mesma validação do ticket 25: resposta inválida vira erro da página, nunca Oferta.
- O esquema pedido inclui, como no ticket 25: preço opcional, a área da foto de cada item (opcional) e a marca da página (opcional). O adaptador converte a área para a mesma forma que o fake usa, para o recorte do ticket 25.
- Verificação manual também com o PDF fictício só de fotos do ticket 24 (tipo 4): ele vira Catálogo sem preço e pede a planilha de preços.
- Sem chave configurada, a Importação pela LLM é recusada antes de qualquer chamada (testável com a configuração alterada no teste, sem rede).
- Falha de rede ou da API cai na mesma mensagem de serviço indisponível do ticket 25.
- Verificação manual: importar um Catálogo fictício do ticket 24 pela tela, com a chave real, e anotar o resultado em `## Comments`.

## Erros (mensagens em português)

- Sem chave → `A leitura por LLM não está configurada: falta a chave da API. Peça ao responsável pela instalação para configurá-la.`

## O que o teste precisa

- Só a configuração sem chave. Nenhum teste automatizado chama a API real.

## Notas para o /tdd

- Use o prompt e o esquema de saída que o ticket 24 registrou em `## Answer`.
- Consulte a skill `claude-api` para o SDK e o identificador atual do modelo antes de escrever o adaptador.
