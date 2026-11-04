# 01 — Esqueleto do projeto e cadastro de Fornecedor

Status: ready-for-agent
Type: task
Blocked by: —
Spec: [docs/spec.md](../../../docs/spec.md) (Testing Decisions; Implementation Decisions › Arquitetura e tecnologia)
ADRs: ADR-0008 (Django + SQLite), ADR-0007 (base do grupo)
User stories: 8

## O que entrega

O projeto Django roda, o executor de testes roda e existe o primeiro caso de uso real, **cadastrar Fornecedor**, com o teste que serve de modelo para todos os tickets seguintes. O teste entra pelo caso de uso, usa o banco de teste do Django, não usa mocks internos e verifica comportamento, não estrutura.

## Critérios de aceite

Esqueleto

- Projeto Django com SQLite, `LANGUAGE_CODE = "pt-br"` e fuso `America/Sao_Paulo`. As dependências ficam fixadas num arquivo de requisitos.
- Modelo de usuário próprio para o **Gestor** desde a primeira migração. O Django recomenda isso no início, porque trocar depois é caro.
- Um único comando roda todos os testes (`python manage.py test`), documentado no README.
- Existe uma exceção base de regra de negócio (nome indicativo: `ErroDeNegocio`) que carrega a mensagem em português mostrada à gestora. As exceções dos próximos tickets herdam dela.
- Cada módulo do spec vira um app Django só quando um ticket precisar dele. Este ticket cria apenas `contas` (Gestor) e `catalogos` (Fornecedor).
- Os casos de uso de cada módulo ficam num arquivo próprio (ex.: `catalogos/casos_de_uso.py`), separado das views. As views apenas chamam casos de uso.

Comportamento (pelo caso de uso)

- Dado um Gestor, quando ele cadastra o Fornecedor "Fornecedor Alfa", então "Fornecedor Alfa" aparece na lista de Fornecedores.
- Outro Gestor vê o mesmo Fornecedor na lista, porque a base é do grupo (ADR-0007).
- O nome é guardado sem espaços nas pontas.

## Erros (mensagens em português)

- Nome vazio ou só com espaços → `Informe o nome do Fornecedor.` Nenhum Fornecedor é criado.
- Nome igual a um já cadastrado, ignorando maiúsculas e espaços nas pontas → `Já existe um Fornecedor chamado Fornecedor Alfa.`

## O que o teste precisa

- Um auxiliar de teste para criar Gestores, que os próximos tickets vão reutilizar (o ticket 02 acrescenta Lojas).
- Nenhum Catálogo fictício. Nenhum fake da LLM.

## Fora deste ticket

- Telas e login (ticket 02).
- Perfil do Fornecedor (tickets 17 e 21).

## Notas para o /tdd

- Este ticket define o padrão: um teste por comportamento, nomeado pelo comportamento ("cadastrar Fornecedor com nome repetido é recusado"), sem verificar tabelas nem chamadas internas.
