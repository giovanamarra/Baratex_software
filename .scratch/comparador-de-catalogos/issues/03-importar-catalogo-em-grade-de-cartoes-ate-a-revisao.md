# 03 — Importar um Catálogo em grade de cartões até a Revisão

Status: ready-for-agent
Type: task
Blocked by: 01, 02
Spec: [docs/spec.md](../../../docs/spec.md) (Extração; Revisão; Casos de uso › Importação)
ADRs: ADR-0006 (três caminhos, caminho 1), ADR-0008. O ADR-0001 está substituído: a recusa de Layout desconhecido abaixo é **provisória**.
User stories: 9, 14 (PDF), 16, 21, 22, 26, 27

## O que entrega

A gestora escolhe o Fornecedor, envia um PDF em grade de cartões de **um** Layout conhecido (o Layout A) e vê as Ofertas extraídas numa Revisão em andamento. Nada vira Catálogo ainda: confirmar e abandonar ficam para o ticket 04.

## Critérios de aceite

- Iniciar Importação (Gestor, Fornecedor, arquivo) com um Catálogo fictício do Layout A de N cartões cria uma Revisão em andamento com N Ofertas propostas. Cada uma tem código, descrição, preço impresso, Caixa, Embalagem intermediária (quando o cartão traz uma) e caminho de extração "grade de cartões".
- O Layout é reconhecido pelo conteúdo do PDF, sem a gestora escolher o leitor (16).
- O Fornecedor da Revisão é o escolhido pela gestora, mesmo quando o PDF traz o nome de outra marca (9).
- ~~Nada é salvo como Catálogo~~: movido para o ticket 04, que cria o Catálogo e a lista de Catálogos do Fornecedor (decisão da usuária, 2026-11-04).
- A Revisão em andamento é persistida. Buscá-la de novo pelo identificador, como num recarregamento da página, traz as mesmas Ofertas propostas.
- A gestora vê as próprias Revisões em andamento e consegue retomá-las. A Revisão em andamento é de quem iniciou a Importação: outro Gestor que a abre pela URL recebe 403 com `Esta Revisão é de outro Gestor.` (decisão da usuária, 2026-11-04).
- O arquivo enviado fica guardado no armazenamento de arquivos, ligado à Revisão.
- Telas finas: formulário de Importação (Fornecedor + arquivo) e tela de Revisão com as Ofertas e o caminho de extração de cada uma (27).

## Erros (mensagens em português)

- Sem Fornecedor → `Escolha o Fornecedor do Catálogo.`
- Documento sem nenhum preço → `Este documento não tem preços, então não é um Catálogo. Envie o arquivo com os preços.` Nenhuma Revisão é criada (21).
- Arquivo que não abre (bytes inválidos) → `Não consegui abrir este arquivo. Ele pode estar corrompido: peça ao Fornecedor que envie de novo.` (22)
- **Provisório**, até os tickets 21, 23 e 25:
  - PDF com texto que não é de nenhum Layout conhecido → `Não reconheci o Layout deste PDF. Por enquanto, só Catálogos em grade de cartões de Layouts conhecidos podem ser importados.`
  - Excel, imagem ou outro formato → `Por enquanto, só Catálogos em PDF de grade de cartões podem ser importados.`

## O que o teste precisa

- **Catálogo fictício do Layout A**: um construtor de teste que gera o PDF, com texto selecionável, a partir de uma lista de Ofertas inventadas. Ele imita a estrutura do Layout real escolhido: quantos cartões há por página, onde fica cada campo e os rótulos do Layout (prefixo do código, "R$", rótulo da Caixa, rótulo da Embalagem intermediária) e o traço que permite reconhecê-lo. Códigos, descrições, preços e nomes de marca são inventados. O construtor é reutilizado em quase todos os tickets seguintes.
- Os casos mínimos: duas páginas; um cartão com nome de marca diferente do Fornecedor; o mesmo Layout sem nenhum preço; e bytes inválidos.
- Sem cartão com Embalagem intermediária: o Layout A real não tem esse campo (só "Cx: N"), então o leitor nunca a propõe (decisão da usuária, 2026-11-04).
- Nenhum fake da LLM.

## Fora deste ticket

- Confirmar e abandonar (04); Preço unitário (05); correções e regras de confirmação (06); marcas de conferência e contagem de preços (08); foto (14); segundo Layout (20).

## Notas para o /tdd

- **Qual Layout é o A**: escolha na sessão o Layout que cobre mais arquivos em `catalogos-exemplo/`. Sugestão: a família de 8 arquivos gerados pelo mesmo sistema da importadora. Confirme antes que é uma grade de cartões com texto selecionável. Use os arquivos reais só para estudar a estrutura; nenhum entra no repositório.
- O reconhecimento usa um traço estrutural do Layout, não o nome real do Fornecedor.
