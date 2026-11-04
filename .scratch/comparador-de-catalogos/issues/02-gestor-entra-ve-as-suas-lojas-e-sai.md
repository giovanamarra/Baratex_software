# 02 — Gestor entra, vê as suas Lojas e sai

Status: resolved
Type: task
Blocked by: 01
Spec: [docs/spec.md](../../../docs/spec.md) (Acesso e Lojas; Testing Decisions › poucos testes pelo cliente HTTP)
ADRs: ADR-0007 (Lojas são do Gestor), ADR-0008 (painel administrativo, sem autocadastro)
User stories: 1, 2, 3, 6, 7 (e a tela da história 8)

## O que entrega

A gestora entra com usuário e senha, vê as próprias Lojas, pode renomeá-las e sai. Gestores e Lojas são cadastrados pelo painel administrativo do Django. A tela de Fornecedores do ticket 01 passa a existir, atrás do login.

## Critérios de aceite

Pelo caso de uso

- O Responsável pela instalação cadastra um Gestor e as Lojas dele pelo painel administrativo. Cada Loja pertence a exatamente um Gestor.
- Listar as minhas Lojas (Gestor) devolve só as Lojas desse Gestor.
- Renomear Loja (Gestor, Loja, nome): o dono da Loja consegue.

Pelo cliente HTTP do Django (os únicos testes de tela deste ticket)

- Sem login, qualquer página leva à tela de login.
- Depois do login, a página inicial mostra as Lojas do Gestor e não mostra as de outro.
- Um Gestor que tenta, pela URL, editar a Loja de outro é recusado e a Loja não muda.
- Depois de sair, a próxima página pede login de novo.
- A tela de Fornecedores (lista e cadastro) só abre com login e chama o caso de uso do ticket 01.

## Erros (mensagens em português)

- Renomear a Loja de outro Gestor → `Esta Loja é de outro Gestor. Só ele pode editá-la.`
- Nome de Loja vazio → `Informe o nome da Loja.`
- Login com senha errada → `Usuário ou senha incorretos.`

## O que o teste precisa

- Dois Gestores fictícios, cada um com duas Lojas de nomes inventados ("Loja Centro", "Loja Norte"...).
- Nenhum Catálogo fictício. Nenhum fake da LLM.

## Fora deste ticket

- Autocadastro e recuperação de senha por e-mail (Out of Scope).
- Autorização de Pedidos (tickets 15 e 16).

## Comments

**2026-11-04 — implementado por TDD** (commits `57d79d0` a `71b1c9b`)

- Casos de uso em `contas/casos_de_uso.py`: `listar_minhas_lojas`, `renomear_loja`, `exigir_dono_da_loja`.
- `AcessoNegado` (filha de `ErroDeNegocio`, em `comparador/erros.py`): as telas respondem 403. Reutilizar nos Pedidos (tickets 15 e 16).
- Login obrigatório pelo `LoginRequiredMiddleware`. O teste `test_sem_login_qualquer_pagina_leva_ao_login` percorre todas as rotas nomeadas de `comparador/urls.py`: toda página nova precisa de nome e já nasce coberta.
- Rotas: `/entrar/`, `/sair/` (só POST), `/`, `/lojas/<pk>/editar/`, `/fornecedores/`, `/admin/`.
- Identidade visual: `static/css/tokens.css` (testado contra o bloco do BRAND.md), `static/css/base.css`, logos em `static/img/`, `templates/base.html`. Teste impede hex fora de `tokens.css`.
- 18 testes, todos verdes. Os 10 comportamentos e o teste de tokens começaram vermelhos. Só o teste de hex nasceu verde (o CSS já usava variáveis) e foi provado com mutação.
- O painel administrativo foi conferido com um teste descartável (não ficou no repositório).
