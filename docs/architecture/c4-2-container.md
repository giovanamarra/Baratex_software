# C4 — Nível 2: Container

Arquitetura do MVP, derivada de [spec](../spec.md), [GLOSSARY](../../GLOSSARY.md) e [ADRs](../adr/). Os três containers já existem no código: a Aplicação web em Django, o banco SQLite e a pasta de arquivos (ticket 11). Parte das responsabilidades listadas ainda é planejada, e a leitura pela LLM ainda não foi implementada.

```mermaid
C4Container
  title Container — Comparador de Catálogos de Fornecedores

  Person(gestora, "Gestora de compras", "Importa Catálogos, compara Produtos e monta Pedidos")
  Person(outro_gestor, "Outro Gestor do grupo", "Usa a mesma base de compras, com as próprias Lojas e Pedidos")
  Person(responsavel, "Responsável pela instalação", "Cadastra Gestores e Lojas")

  System_Boundary(sb, "Comparador de Catálogos") {
    Container(web, "Aplicação web", "Python / Django, HTML renderizado no servidor", "Login e autorização, Importação e Revisão, extração, comparação, Pedidos, exportação da planilha, Painéis e painel administrativo")
    ContainerDb(db, "Banco de dados", "SQLite", "Gestores, Lojas, Fornecedores, Perfis, Catálogos, Ofertas, Produtos, Pedidos, Revisões em andamento e auditoria")
    Container(arquivos, "Armazenamento de arquivos", "Sistema de arquivos local, no computador da gestora", "Arquivos de Catálogo enviados, imagens das páginas para conferência e fotos das Ofertas")
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
| Armazenamento de arquivos | Container (arquivos) | sistema de arquivos local, no computador da gestora (ticket 11) | Arquivo de origem de cada Catálogo, imagens de página para a conferência da LLM e fotos | Spec (Catálogo guarda o arquivo de origem; histórias 28, 57); ADR-0011; ticket 11 |
| Serviço de LLM com visão | Sistema externo | Claude Haiku, via API | Ler páginas e propor Ofertas, sempre seguidas de Revisão | ADR-0006; ADR-0008 |
| Gestora de compras, Outro Gestor do grupo, Responsável pela instalação | Pessoas | — | Como no nível 1 | Ver [nível 1](c4-1-contexto.md) |
| Fornecedor, Representante | Pessoas externas | — | Como no nível 1; não usam o sistema | Ver [nível 1](c4-1-contexto.md) |

A disciplina pede pelo menos 3 responsabilidades distintas. Elas ficam **dentro** da Aplicação web como módulos (Contas, Catálogos, Extração, Importação e Revisão, Produtos, Pedidos, Painéis; ver o spec). São componentes do nível 3 e não aparecem aqui.

## Suposições e pontos inferidos

- Os arquivos de Catálogo, as imagens de página e as fotos ficam no sistema de arquivos local do computador da gestora (o armazenamento de mídia do Django, numa pasta fora do repositório), e não dentro do banco (ADR-0011; ticket 11). O backup leva o banco e essa pasta num único arquivo.
- **Inferido:** a chamada à LLM é feita pela própria Aplicação web, durante a Importação, sem processo em segundo plano. O ADR-0008 aceita esse risco e prevê mover a leitura para segundo plano se ficar lenta.
- Login e autorização usam a autenticação do Django; não há provedor de identidade externo.
- A exportação gera um arquivo Excel baixado pelo navegador; não há serviço de e-mail no MVP.
- Itens fora do MVP (pedidos públicos entre Gestores, frete compartilhado, avisos por e-mail) não aparecem.

## Perguntas em aberto

- Catálogos de dezenas de páginas lidos pela LLM cabem no tempo de uma requisição web, ou será preciso um worker em segundo plano (novo container)? Medir no ticket da LLM.
- Quando houver um servidor para os outros Gestores: como implantar, com HTTPS. Um ADR decide nesse momento.

## Perguntas respondidas

- **Onde a aplicação roda:** no computador da gestora, atendendo só o próprio computador (127.0.0.1). Os outros Gestores só passam a usar quando houver um servidor (ticket 11).
- **Por quanto tempo guardar os arquivos:** para sempre: os arquivos de origem de cada Catálogo, as imagens de página e as fotos. A única exceção são os arquivos e as fotos de uma Revisão abandonada (ticket 11; ADR-0011).
