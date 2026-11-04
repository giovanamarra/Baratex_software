# C4 — Nível 2: Container

Arquitetura **planejada** do MVP, derivada de [spec](../../.scratch/comparador-de-catalogos/spec.md), [GLOSSARY](../../GLOSSARY.md) e [ADRs](../adr/). Ainda não existe código.

```mermaid
C4Container
  title Container — Comparador de Catálogos de Fornecedores

  Person(gestora, "Gestora de compras", "Importa Catálogos, compara Produtos e monta Pedidos")
  Person(outro_gestor, "Outro Gestor do grupo", "Usa a mesma base de compras, com as próprias Lojas e Pedidos")
  Person(responsavel, "Responsável pela instalação", "Cadastra Gestores e Lojas")

  System_Boundary(sb, "Comparador de Catálogos") {
    Container(web, "Aplicação web", "Python / Django, HTML renderizado no servidor", "Login e autorização, Importação e Revisão, extração, comparação, Pedidos, exportação da planilha, Painéis e painel administrativo")
    ContainerDb(db, "Banco de dados", "SQLite", "Gestores, Lojas, Fornecedores, Perfis, Catálogos, Ofertas, Produtos, Pedidos, Revisões em andamento e auditoria")
    Container(arquivos, "Armazenamento de arquivos", "a decidir", "Arquivos de Catálogo enviados, imagens das páginas para conferência e fotos das Ofertas")
  }

  System_Ext(llm, "Serviço de LLM com visão", "Claude Haiku: lê páginas de Catálogos de layout livre ou só imagem")
  Person_Ext(fornecedor, "Fornecedor", "Envia Catálogos e recebe Pedidos, fora do sistema")
  Person_Ext(representante, "Representante", "Recebe Pedidos de vários Fornecedores, fora do sistema")

  Rel(gestora, web, "Importa Catálogos, compara Produtos e exporta Pedidos em", "HTTP(S)")
  Rel(outro_gestor, web, "Consulta a base e monta os próprios Pedidos em", "HTTP(S)")
  Rel(responsavel, web, "Cadastra Gestores e Lojas pelo painel administrativo de", "HTTP(S)")
  Rel(web, db, "Lê e grava dados de compra em", "SQL")
  Rel(web, arquivos, "Guarda e lê arquivos de Catálogo e imagens em", "E/S de arquivos")
  Rel(web, llm, "Envia páginas e recebe Ofertas propostas de", "JSON/HTTPS")
  Rel(fornecedor, gestora, "Envia Catálogos para")
  Rel(gestora, fornecedor, "Envia a planilha de Pedidos para")
  Rel(gestora, representante, "Envia a planilha de Pedidos para")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Elementos

| Nome | Tipo | Tecnologia | Responsabilidade | Origem |
|---|---|---|---|---|
| Aplicação web | Container | Python / Django | Telas, login e autorização por Gestor, casos de uso de Importação, Revisão, Produtos, Pedidos e Painéis; extração por três caminhos; geração da planilha de Pedidos; painel administrativo | ADR-0008; ADR-0006; ADR-0004; ADR-0007; spec, histórias 1–100 |
| Banco de dados | Container (banco) | SQLite | Persistência da base de compras do grupo, das Lojas e Pedidos de cada Gestor, das Revisões em andamento e da auditoria de Perfil, Conteúdo e vínculos | ADR-0008; ADR-0007; spec, Modelo de dados |
| Armazenamento de arquivos | Container (arquivos) | **a decidir** (sugestão: sistema de arquivos do servidor) | Arquivo de origem de cada Catálogo, imagens de página para a conferência da LLM e fotos | Spec (Catálogo guarda o arquivo de origem; histórias 28, 57); **container inferido** |
| Serviço de LLM com visão | Sistema externo | Claude Haiku, via API | Ler páginas e propor Ofertas, sempre seguidas de Revisão | ADR-0006; ADR-0008 |
| Gestora de compras, Outro Gestor do grupo, Responsável pela instalação | Pessoas | — | Como no nível 1 | Ver [nível 1](c4-1-contexto.md) |
| Fornecedor, Representante | Pessoas externas | — | Como no nível 1; não usam o sistema | Ver [nível 1](c4-1-contexto.md) |

A disciplina pede pelo menos 3 responsabilidades distintas. Elas ficam **dentro** da Aplicação web como módulos (Contas, Catálogos, Extração, Importação e Revisão, Produtos, Pedidos, Painéis; ver o spec). São componentes do nível 3 e não aparecem aqui.

## Suposições e pontos inferidos

- **Inferido:** os arquivos enviados e as imagens de página ficam no sistema de arquivos do servidor (o armazenamento de mídia do Django), e não dentro do banco. Nenhum documento define isso; um ADR curto resolve.
- **Inferido:** a chamada à LLM é feita pela própria Aplicação web, durante a Importação, sem processo em segundo plano. O ADR-0008 aceita esse risco e prevê mover a leitura para segundo plano se ficar lenta.
- Login e autorização usam a autenticação do Django; não há provedor de identidade externo.
- A exportação gera um arquivo Excel baixado pelo navegador; não há serviço de e-mail no MVP.
- Itens fora do MVP (pedidos públicos entre Gestores, frete compartilhado, avisos por e-mail) não aparecem.

## Perguntas em aberto

- Catálogos de dezenas de páginas lidos pela LLM cabem no tempo de uma requisição web, ou será preciso um worker em segundo plano (novo container)? Medir no ticket da LLM.
- Onde a aplicação vai rodar: só no computador da gestora ou num servidor acessível aos outros Gestores? Isso define HTTPS, backup do SQLite e do armazenamento de arquivos. Tecnologia de implantação: **a decidir**.
- Por quanto tempo guardar os arquivos de Catálogo originais e as imagens de página depois da Revisão?
