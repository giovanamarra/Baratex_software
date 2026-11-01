# Referência: Mermaid C4 (níveis 1 e 2)

Leia antes de escrever os diagramas. Os exemplos usam um domínio genérico (uma biblioteca). **Não copie os elementos deles**: copie só a forma.

## Nível 1: Contexto

```mermaid
C4Context
  title Contexto — Sistema de Biblioteca

  Person(leitor, "Leitor", "Pesquisa e reserva livros")
  Person(bibliotecaria, "Bibliotecária", "Cadastra o acervo e gerencia empréstimos")

  System(biblioteca, "Sistema de Biblioteca", "Controla acervo, reservas e empréstimos")

  System_Ext(email, "Serviço de e-mail", "Envia avisos de devolução")

  Rel(leitor, biblioteca, "Pesquisa e reserva livros em")
  Rel(bibliotecaria, biblioteca, "Gerencia o acervo em")
  Rel(biblioteca, email, "Envia avisos por meio de")
```

Elementos permitidos: `Person`, `Person_Ext`, `System`, `System_Ext`, `SystemDb_Ext`, `Rel`, `BiRel`.

## Nível 2: Container

```mermaid
C4Container
  title Container — Sistema de Biblioteca

  Person(leitor, "Leitor", "Pesquisa e reserva livros")

  System_Boundary(sb, "Sistema de Biblioteca") {
    Container(web, "Aplicação web", "a decidir", "Telas de busca, reserva e administração")
    Container(api, "API", "Python / FastAPI", "Regras de reserva e empréstimo")
    ContainerDb(db, "Banco de dados", "PostgreSQL", "Acervo, usuários e empréstimos")
  }

  System_Ext(email, "Serviço de e-mail", "Envia avisos de devolução")

  Rel(leitor, web, "Usa", "HTTPS")
  Rel(web, api, "Chama", "JSON/HTTPS")
  Rel(api, db, "Lê e grava", "SQL")
  Rel(api, email, "Envia avisos", "SMTP")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

Elementos permitidos: os do nível 1, mais `System_Boundary`, `Container`, `ContainerDb`, `ContainerQueue`, `Container_Ext`, `ContainerDb_Ext`.

Assinaturas:
- `Person(alias, rótulo, descrição)`
- `System(alias, rótulo, descrição)`
- `Container(alias, rótulo, tecnologia, descrição)`
- `Rel(origem, destino, rótulo, tecnologia opcional)`

## Erros comuns

- **Classe ou módulo como container.** "ParserDeCatálogo" dentro da API é um componente (nível 3), não um container.
- **Biblioteca como container.** Uma biblioteca de leitura de PDF é copiada para dentro da aplicação; ela não roda sozinha.
- **Relação sem verbo.** Escreva "Lê preços de", não só "Usa" sem contexto.
- **Tecnologia no nível 1.** No Contexto não aparece "PostgreSQL" nem "React".
- **Alias com acento ou espaço.** Use `gestora`, `api_catalogos`. Os acentos ficam só nos rótulos entre aspas.
- **Layout poluído.** Mais de 8 a 10 elementos em um diagrama é sinal de que o nível está errado.
