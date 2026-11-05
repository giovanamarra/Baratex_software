# Ordem de execução dos tickets

Atualizado em 2026-11-05, depois da mudança de requisito do commit `25b5f99` (ADR-0009, 0010, 0011).

Os tickets 01 a 10 estão resolvidos. A ordem abaixo mantém a ordem numérica dos tickets existentes. Os novos de data e vigência entram logo depois do 11. Os outros entram junto do ticket existente que mais depende deles. Todo ticket só começa com os seus `Blocked by` resolvidos, e a sequência abaixo respeita isso.

Modelo: **Opus** para regras de negócio, backup, planilha, Excel/PDF/LLM e mudanças em código já feito; **Sonnet** só para telas e consultas com regra já decidida.

| # | Ticket | Modelo |
|---|---|---|
| 1 | 11 — Rodar no computador da gestora, com backup | Opus |
| 2 | 31 — Data do Catálogo informada na Revisão e Oferta vigente pelo Catálogo mais recente | Opus |
| 3 | 32 — Código repetido no mesmo Catálogo: agrupado na Revisão, vale o menor Preço unitário | Opus |
| 4 | 33 — Aviso de Catálogo mais antigo e correção da data de um Catálogo confirmado | Opus |
| 5 | 12 — Criar Produto e ligar Ofertas a ele | Opus |
| 6 | 13 — Comparar as Ofertas vigentes de um Produto | Sonnet |
| 7 | 14 — Foto da Oferta lida da grade de cartões | Opus |
| 8 | 34 — Trocar ou tirar a foto de uma Oferta na Revisão | Opus |
| 9 | 15 — Pedido para um Fornecedor, com Caixas por Loja | Opus |
| 10 | 16 — Ajustar e listar os meus Pedidos | Sonnet |
| 11 | 40 — Linha do Pedido cuja Oferta deixou de ser vigente | Opus |
| 12 | 17 — Fracionamento no Perfil do Fornecedor | Opus |
| 13 | 18 — Exportar um Pedido na planilha padrão da gestora | Opus |
| 14 | 19 — Exportar vários Pedidos num arquivo, com um bloco por desconto | Opus |
| 15 | 20 — Reconhecer um segundo Layout de grade de cartões | Opus |
| 16 | 35 — Descrição normalizada como código da Oferta sem código | Opus |
| 17 | 21 — Importar um Catálogo em tabela Excel, com o mapeamento de colunas no Perfil do Fornecedor | Opus |
| 18 | 36 — Completar o Catálogo com uma planilha de preços | Opus |
| 19 | 37 — Várias planilhas de preços num Catálogo e desconto por arquivo | Opus |
| 20 | 38 — Ligar as fotos do arquivo do Catálogo às Ofertas da planilha | Opus |
| 21 | 22 — Catálogo em tabela com várias colunas de preço | Opus |
| 22 | 23 — Catálogo em tabela em PDF e correção do mapeamento | Opus |
| 23 | 39 — Foto da Oferta nos Catálogos em tabela (Excel e PDF) | Opus |
| 24 | 24 — Investigação: tempo e custo por página da LLM com visão | Opus |
| 25 | 25 — Importar um Catálogo de layout livre ou só imagem pela LLM | Opus |
| 26 | 26 — Conferir as páginas lidas pela LLM ao lado da imagem | Opus |
| 27 | 27 — Ler páginas com o Claude Haiku | Opus |
| 28 | 28 — Histórico de preço de uma Oferta e evolução do Produto por Fornecedor | Sonnet |
| 29 | 29 — Painel de volume de Pedidos de compra por Loja | Sonnet |
| 30 | 30 — Painel de evolução de preço dos Produtos e comparação entre Fornecedores | Sonnet |

## Onde a regra de posição não pôde ser seguida à letra

- **40** é de vigência (ADR-0009), mas depende do Pedido (15, 16) e da correção de data (33). Por isso entra logo depois do 16, e não logo depois do 11.
- **39** (fotos fora da grade) não pode ficar junto do 14: a foto em Excel e em PDF em tabela precisa do leitor de tabela (21, 23). Entra logo depois do 23. A foto da LLM está nos tickets 25 e 26. Junto do 14 ficou o **34** (trocar ou tirar a foto).
- **35** entra logo antes do 21, que depende dele (mapeamento sem coluna de código).
- **36, 37 e 38** (planilhas de preços) entram logo depois do 21, porque precisam do leitor de tabela, e antes do 22, que depende do 37 (aviso no desconto de cada arquivo).
- **24** não depende de nada e pode ser adiantado, se for útil ter as medidas antes.
