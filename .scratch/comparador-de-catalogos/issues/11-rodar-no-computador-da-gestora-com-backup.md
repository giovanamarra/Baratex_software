# 11 — Rodar no computador da gestora, com backup

Status: ready-for-agent
Type: task
Blocked by: 04
Spec: [docs/spec.md](../../../docs/spec.md) (Arquitetura e tecnologia); [C4 Container](../../../docs/architecture/c4-2-container.md) (perguntas em aberto)
ADRs: ADR-0008
User stories: nenhuma diretamente; dá suporte a 1 e 6

## O que entrega

A gestora usa o sistema no próprio computador, com instruções que outra pessoa consegue seguir, e o banco e os arquivos de Catálogo têm backup.

Decisões da usuária que este ticket aplica (pergunta em aberto do C4):

- **Onde roda:** no computador da gestora. Os outros Gestores só passam a usar quando houver um servidor; nesse momento, um ADR decide a implantação.
- **Arquivos:** o arquivo original de cada Catálogo, as imagens de página e as fotos são guardados **para sempre**. A única exceção é o arquivo de uma Revisão abandonada (ticket 04).

## Critérios de aceite

- O README explica, para quem não programa: como instalar, como iniciar o sistema com um único comando ou script, qual endereço abrir no navegador, e como o Responsável pela instalação cria o primeiro Gestor e as Lojas pelo painel administrativo.
- A aplicação escuta só no próprio computador (localhost).
- Os arquivos de Catálogo, as imagens de página e as fotos ficam numa pasta de arquivos fora do repositório.
- Os segredos (chave da API da LLM) vêm de um arquivo de ambiente fora do repositório. O sistema inicia sem a chave: ela só é necessária a partir do ticket 25.
- Fazer backup (comando) gera um único arquivo, com a data no nome, contendo o banco e a pasta de arquivos.
- Restaurar esse backup numa instalação vazia traz de volta os Catálogos, as Ofertas e os arquivos de origem. Teste: importar e confirmar um Catálogo fictício, fazer backup, apagar, restaurar, buscar a Oferta e ver o mesmo Preço unitário e o arquivo de origem presente.

## Erros (mensagens em português)

- Pasta de destino do backup inexistente → `A pasta de destino não existe: <caminho>.`
- Restaurar um arquivo que não é backup do sistema → `Este arquivo não é um backup do Comparador de Catálogos.`

## O que o teste precisa

- O construtor do Catálogo fictício do Layout A; pastas temporárias para o backup.
- Nenhum fake da LLM.

## Fora deste ticket

- Servidor, HTTPS e acesso dos outros Gestores (fica para quando a implantação mudar).
- Backup automático agendado.

## Notas

- Escolher o lugar de execução não é difícil de reverter, então não é preciso ADR agora. Quando for para um servidor, vale um ADR. O C4 Container pode trocar "a decidir" por "sistema de arquivos local" no Armazenamento de arquivos.
