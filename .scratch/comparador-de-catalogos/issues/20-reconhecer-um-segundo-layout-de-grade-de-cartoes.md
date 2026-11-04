# 20 — Reconhecer um segundo Layout de grade de cartões

Status: ready-for-agent
Type: task
Blocked by: 08, 14
Spec: [docs/spec.md](../../../docs/spec.md) (Extração › Grade de cartões: um leitor por Layout, acrescentado sem mexer nos outros)
ADRs: ADR-0006 (caminho 1)
User stories: 16

## O que entrega

Um segundo Layout de grade de cartões passa a ser importado. O sistema escolhe sozinho o leitor certo entre os dois.

## Critérios de aceite

- Iniciar a Importação com um Catálogo fictício do Layout B gera a Revisão com as Ofertas lidas pelo leitor B, com o caminho "grade de cartões".
- O Catálogo fictício do Layout A continua sendo lido pelo leitor A. Os testes do Layout A não mudam.
- O leitor B é acrescentado sem alterar o código do leitor A.
- A contagem de preços (08) e a foto (14), se o Layout B tiver fotos, funcionam no Layout B.

## Erros (mensagens em português)

- Um PDF com texto que não é de nenhum dos dois Layouts continua com a mensagem do ticket 03 (até o ticket 23 ou 25 trocá-la).

## O que o teste precisa

- Um construtor do Catálogo fictício do Layout B, imitando a estrutura do segundo Layout real escolhido, com dados inventados.
- Nenhum fake da LLM.

## Notas para o /tdd

- Escolha como Layout B o segundo Layout que mais aparece em `catalogos-exemplo/` ou o do Fornecedor que a gestora mais usa. Cada Layout novo depois deste segue o mesmo molde e não precisa de ticket de desenho.
