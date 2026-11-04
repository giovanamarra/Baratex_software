# 03 — Importar um Catálogo em grade de cartões até a Revisão

Status: resolved
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

## Comments

**2026-11-04 — implementado por TDD** (commits `f0c9e05` a `82ecfea`)

- **Layout A** (confirmado pela usuária): família de 8 PDFs gerados pelo mesmo sistema da importadora, 1.931 cartões, A4, grade 4 colunas x 5 linhas de cartões de 140 pt, texto selecionável. Reconhecido quando cada cartão traz uma vez `Código:`, `Disponibilidade:` e `Tag:`. O `Ean13:` ficou de fora do traço porque o pdfplumber parte essa palavra em ~3/4 dos cartões reais.
- **Bibliotecas** (escolha da usuária): pdfplumber (MIT) para ler com posição; fpdf2 (LGPL-3.0) para o Catálogo fictício nos testes.
- **Construtor do Catálogo fictício**: `extracao/catalogos_ficticios.py` (`CartaoFicticio`, `catalogo_ficticio_layout_a(cartoes, rodape=...)`, `pdf_ficticio_com_texto(linhas)`). Imita a geometria medida no real, com dados inventados.
- **Casos de uso** (`importacao/casos_de_uso.py`): `iniciar_importacao`, `obter_revisao`, `listar_revisoes_em_andamento`. Extração em `extracao/extrair.py` (`extrair_ofertas`) e `extracao/grade_de_cartoes.py`.
- **Conferência local com os PDFs reais** (nada entrou no repositório): o leitor lê 1.931 de 1.931 cartões, sem código ou descrição vazios, com preço e Caixa nos cartões certos; o reconhecimento aceita os 8 PDFs do Layout A e recusa os outros 20; 918 Ofertas em 2,5 s.
- **Achado do real**: 1 cartão com preço mascarado (`R$***,**`) e 2 com Caixa mascarada (`Cx:***`) viram Oferta sem preço ou sem Caixa. O ticket 06 bloqueia a confirmação delas.
- **Fora do ticket, acrescentado**: Importação sem arquivo é recusada com `Escolha o arquivo do Catálogo.`
- Mensagens provisórias marcadas em `extracao/extrair.py`, citando os tickets 21, 23 e 25.
- Arquivos enviados em `MEDIA_ROOT/importacoes/` (`media/` no `.gitignore`); os testes usam uma pasta temporária.
