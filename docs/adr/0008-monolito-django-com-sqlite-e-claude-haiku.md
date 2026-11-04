---
status: accepted
---

# Monólito web em Django com SQLite, e Claude Haiku como LLM com visão

O projeto prefere poucas peças e soluções que a desenvolvedora consiga explicar, com backend em Python e banco relacional. O MVP precisa de login, autorização por Gestor, persistência, telas web e um cadastro simples de Gestores e Lojas. O ADR-0006 deixou para o spec a escolha concreta da LLM com visão, pelo critério de menor custo desde que leia imagem. Decidimos:

- **Uma única aplicação web em Django**, com HTML renderizado no servidor. As regras de negócio ficam em casos de uso chamados pelas telas, e não há API separada.
- **SQLite** como banco. PostgreSQL só entra se for preciso, e o código não deve depender de recursos exclusivos do SQLite.
- **Claude Haiku** como LLM com visão, atrás de uma interface "ler página → Ofertas propostas" que pode ser trocada. O modelo e a chave de API vêm da configuração.

## Opções consideradas

- **Django (escolhida):** já traz login, sessões, ORM, migrações, painel administrativo e cliente de teste. Gestores e Lojas são cadastrados pelo painel administrativo, sem tela própria.
- **Flask + SQLAlchemy:** mais leve e explícito, mas login, migrações e painel administrativo seriam peças à parte.
- **FastAPI + Jinja:** pensado para APIs; login e telas exigem mais montagem.
- **Gemini Flash** para a LLM: também é de baixo custo e lê imagem. Ficou o Claude Haiku para usar uma única conta de API, e a interface permite trocar depois.

## Consequências

- Um único processo concentra telas, regras e extração. Uma leitura longa pela LLM pode deixar a Importação lenta. Se isso atrapalhar, a extração pela LLM pode passar para um processo em segundo plano sem mudar os casos de uso.
- Os testes usam o banco de teste do Django e um fake da interface da LLM. Nenhum teste chama a API real (ADR-0006).
