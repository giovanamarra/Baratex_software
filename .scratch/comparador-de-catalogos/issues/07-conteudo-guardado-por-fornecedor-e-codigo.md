# 07 — Conteúdo guardado por Fornecedor e código

Status: resolved
Type: task
Blocked by: 05
Spec: [docs/spec.md](../../../docs/spec.md) (Modelo de dados › Conteúdo, Auditoria; Revisão › a confirmação aplica o Conteúdo guardado)
ADRs: ADR-0005 (Conteúdo divide o preço; padrão 1), ADR-0007 (auditoria)
User stories: 41, 44, 45, 46

## O que entrega

A gestora diz que um kit de 3 tesouras vendidas avulsas tem Conteúdo 3 e vê o Preço unitário cair para um terço. A decisão vale para os próximos Catálogos desse Fornecedor.

## Critérios de aceite

- Na Revisão, definir o Conteúdo de uma Oferta proposta recalcula o Preço unitário na hora: 9,00 com Conteúdo 3 → 3,00 (44).
- Ao confirmar a Revisão, o Conteúdo fica guardado por Fornecedor + código, com o Gestor e a data (45, 46).
- No Catálogo seguinte do mesmo Fornecedor, a Oferta com o mesmo código já chega na Revisão com Conteúdo 3 (41).
- O mesmo código de outro Fornecedor continua com Conteúdo 1.
- Se a Revisão for abandonada, o Conteúdo definido nela não é guardado.
- Fora da Revisão, definir o Conteúdo de um Fornecedor + código já existente muda o Preço unitário de todas as Ofertas desse Fornecedor + código, inclusive as de Catálogos anteriores, porque o Conteúdo é guardado por Fornecedor + código e não por Oferta.
- O histórico de alterações do Conteúdo de um Fornecedor + código lista Gestor, data, valor anterior e valor novo (46).

## Erros (mensagens em português)

- Conteúdo zero, negativo ou fracionário → `O Conteúdo precisa ser um número inteiro maior ou igual a 1.`
- Definir o Conteúdo, fora da Revisão, de um código sem Oferta → `O Fornecedor Alfa não tem Oferta com o código 9999.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; dois Catálogos do mesmo Fornecedor em dias diferentes; um segundo Fornecedor com o mesmo código.
- Controle do dia no teste.
- Nenhum fake da LLM.

## Fora deste ticket

- A sugestão de Conteúdo quando a descrição cita peças (08).
- O botão "definir Conteúdo" nos resultados da busca (09, que usa o caso de uso deste ticket).

## Comments

**2026-11-04 — implementado por TDD** (commits `e503175` a `9015fa8`; antes, duas correções pedidas pela usuária: `ff35c77` telas que abrem e `8be8c68` preço ambíguo)

- **Guardado** (`catalogos.models.AlteracaoDeConteudo`): um registro por mudança (Fornecedor, código, Gestor, data, valor anterior, valor novo). O Conteúdo atual é o valor novo do registro mais recente; sem registro, vale 1. O histórico é a própria fonte, sem tabela à parte que possa divergir.
- **Na Revisão** (`OfertaProposta.conteudo_definido`): só o Conteúdo definido nela; vazio = usa o guardado. Definido em Corrigir (`corrigir_oferta_proposta(..., conteudo)`). Abandonar descarta.
- **Confirmação** (`confirmar_revisao(gestor, revisao_id, hoje=None)`): grava no histórico só o Conteúdo que difere do guardado, com o dia da confirmação. Confirmar sem mudar o herdado não cria registro (regra da usuária).
- **Fora da Revisão** (`definir_conteudo(gestor, fornecedor, codigo, conteudo, hoje=None)`): recusa código sem Oferta confirmada do Fornecedor (Oferta proposta não conta). Muda o Preço unitário das Ofertas de todos os Catálogos do Fornecedor + código: é a regra, testada explicitamente. Mesmo valor do atual não cria registro.
- **Histórico** (`historico_do_conteudo`): do mais recente para o mais antigo. Qualquer Gestor define e vê (ADR-0007).
- **Conteúdo digitado** (`conteudo_digitado`): inteiro ≥ 1; "3" vale (com espaços em volta também); "3,0", "2.5", "0", "-1", texto e vazio são recusados.
- **Exceção (decisão da usuária, 2026-11-05, implementada no ticket 08):** "Manter 1", na sugestão de Conteúdo, é uma decisão explícita e entra no histórico mesmo sem mudar o valor (1 → 1, com Gestor e data). Com ela guardada, a sugestão não reaparece. Fora disso, continua valendo: sem mudança de valor, sem registro.
- **Telas:** coluna Conteúdo ao lado do Preço unitário (Revisão e Catálogo); campo Conteúdo no Corrigir (não no Adicionar: a Oferta nova usa o guardado e pode ser corrigida depois); por linha do Catálogo, "Definir Conteúdo" (aviso "Atenção: Isto muda o Preço unitário desta Oferta em todos os Catálogos do Fornecedor." antes de salvar) e "Histórico" (dd/mm/aaaa).
