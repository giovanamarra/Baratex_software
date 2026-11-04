# 01 — Esqueleto do projeto e cadastro de Fornecedor

Status: resolved
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

## Comments

**2026-11-04 — implementado por TDD** (commits `38f2008` a `3c4fe4f`)

- Django 6.1.3, SQLite, `pt-br`, `America/Sao_Paulo`, `AUTH_USER_MODEL = 'contas.Gestor'` na primeira migração. Dependências em `requirements.txt`; ambiente em `.venv/`.
- Casos de uso: `catalogos/casos_de_uso.py` (`cadastrar_fornecedor(gestor, nome)`, `listar_fornecedores(gestor)`).
- Exceção base: `comparador/erros.py` (`ErroDeNegocio`, com `.mensagem`).
- Auxiliar de teste: `contas/auxiliares_de_teste.py` (`criar_gestor(usuario)`).
- Testes: `catalogos/tests/test_cadastro_de_fornecedor.py`, 5 testes, todos verdes.
- O teste "outro Gestor vê o Fornecedor" nasceu verde (a lista não filtra por Gestor). Fica como regressão do ADR-0007; uma mutação temporária que torna a lista privada ao primeiro Gestor fez só ele falhar.
- Nome repetido é comparado com `casefold()` em Python, porque o `iexact` do SQLite não iguala maiúsculas acentuadas.
