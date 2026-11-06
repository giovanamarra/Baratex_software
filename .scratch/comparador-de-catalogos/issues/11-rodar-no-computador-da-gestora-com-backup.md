# 11 — Rodar no computador da gestora, com backup

Status: resolved
Type: task
Blocked by: 04
Spec: [docs/spec.md](../../../docs/spec.md) (Arquitetura e tecnologia; Modelo de dados › Foto); [C4 Container](../../../docs/architecture/c4-2-container.md) (perguntas em aberto)
ADRs: ADR-0008, ADR-0011 (fotos na pasta de arquivos)
User stories: nenhuma diretamente; dá suporte a 1 e 6
Atualizado em 2026-11-05 (ADR-0009, 0010, 0011)

## O que entrega

A gestora usa o sistema no próprio computador, com instruções que outra pessoa consegue seguir, e o banco e os arquivos de Catálogo têm backup.

Decisões da usuária que este ticket aplica (pergunta em aberto do C4):

- **Onde roda:** no computador da gestora. Os outros Gestores só passam a usar quando houver um servidor; nesse momento, um ADR decide a implantação.
- **Arquivos:** os arquivos de origem de cada Catálogo (o arquivo do Catálogo e as planilhas de preços), as imagens de página e as fotos são guardados **para sempre**. A única exceção são os arquivos e as fotos de uma Revisão abandonada (tickets 04 e 14).

## Critérios de aceite

- O README explica, para quem não programa: como instalar, como iniciar o sistema com um único comando ou script, qual endereço abrir no navegador, e como o Responsável pela instalação cria o primeiro Gestor e as Lojas pelo painel administrativo.
- O README avisa que o backup cresce com as fotos: o primeiro Catálogo grande de um Fornecedor pode ocupar dezenas de MB, e os seguintes quase nada (ADR-0011).
- A aplicação escuta só no próprio computador (localhost).
- Os arquivos de Catálogo, as imagens de página e as fotos (subpasta `fotos/`) ficam numa pasta de arquivos fora do repositório. Nenhuma imagem fica dentro do banco.
- Os segredos (chave da API da LLM) vêm de um arquivo de ambiente fora do repositório. O sistema inicia sem a chave: ela só é necessária a partir do ticket 25.
- Fazer backup (comando) gera um único arquivo, com a data no nome, contendo o banco e a pasta de arquivos inteira, com as subpastas (inclusive `fotos/`).
- Restaurar esse backup numa instalação vazia traz de volta os Catálogos, as Ofertas e os arquivos de origem. Teste: importar e confirmar um Catálogo fictício, fazer backup, apagar, restaurar, buscar a Oferta e ver o mesmo Preço unitário e o arquivo de origem presente.
- Um arquivo posto em `fotos/` antes do backup volta, com o mesmo conteúdo, depois de restaurar. (A foto de uma Oferta de verdade só existe a partir do ticket 14, que repete este teste com a foto.)

## Erros (mensagens em português)

- Pasta de destino do backup inexistente → `A pasta de destino não existe: <caminho>.`
- Restaurar um arquivo que não é backup do sistema → `Este arquivo não é um backup do Comparador de Catálogos.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; pastas temporárias para o backup; um arquivo qualquer em `fotos/`.
- Nenhum fake da LLM.

## Fora deste ticket

- Servidor, HTTPS e acesso dos outros Gestores (fica para quando a implantação mudar).
- Backup automático agendado.

## Notas

- Escolher o lugar de execução não é difícil de reverter, então não é preciso ADR agora. Quando for para um servidor, vale um ADR. O C4 Container pode trocar "a decidir" por "sistema de arquivos local" no Armazenamento de arquivos.

## Comments

**2026-11-05 — implementado por TDD** (commits `8675cca` a `4a1a404`, mais o commit de README, scripts e documentação)

- **Decisões da usuária:** a gestora usa Windows ou macOS (scripts `iniciar.bat` e `iniciar.command`); `DEBUG=False` sem biblioteca nova, com o CSS servido por `runserver --insecure --noreload` só em 127.0.0.1; página `templates/500.html`; `LOGGING` de `django.request` para o terminal; seams: casos de uso, comandos, leitor do `.env` e `ALLOWED_HOSTS`.
- **Configuração** (`comparador/ambiente.py`, `ler_configuracao`): `.env` sem biblioteca (`NOME=valor`, comentários com `#`, aspas opcionais). Chaves: `SECRET_KEY`, `PASTA_DE_ARQUIVOS`, `ANTHROPIC_API_KEY` (setting `CHAVE_DA_LLM`, opcional até o ticket 25), `DEBUG`. Sem `.env`: valores de desenvolvimento, `DEBUG=False`, pasta `~/ComparadorDeCatalogos/arquivos`, aviso no terminal. Modelo em `.env.exemplo`.
- **Backup** (app `manutencao`, `manutencao/casos_de_uso.py`): `fazer_backup(pasta_destino, agora=None)` → `backup-comparador-AAAA-MM-DD_HH-MM-SS.zip` com `banco.sqlite3` (cópia pela API de backup do SQLite), `arquivos/...` (a pasta de arquivos inteira) e `manifesto.json` (`formato`, `versao` 1, `data`, `catalogos`). `restaurar_backup(arquivo)` recusa instalação com Catálogos, arquivo que não é zip e zip sem manifesto. Comandos `fazer_backup <pasta>` e `restaurar_backup <arquivo>` transformam `ErroDeNegocio` em `CommandError`.
- **Ticket 14:** repetir `test_arquivo_posto_em_fotos_volta_com_o_mesmo_conteudo` com a foto de uma Oferta de verdade.
- **Os scripts `iniciar` rodam `migrate` antes de subir**, então um backup restaurado de uma versão anterior é migrado ao iniciar.

