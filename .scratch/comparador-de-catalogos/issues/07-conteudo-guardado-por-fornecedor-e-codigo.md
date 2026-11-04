# 07 — Conteúdo guardado por Fornecedor e código

Status: ready-for-agent
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
