# Comparador de Catálogos de Fornecedores

Aplicação web em Django que importa Catálogos de Fornecedores, calcula o Preço unitário de cada Oferta e ajuda a gestora a comparar e montar Pedidos. O vocabulário está em [GLOSSARY.md](GLOSSARY.md), as decisões em [docs/adr/](docs/adr/) e o MVP em [docs/spec.md](docs/spec.md).

## Usar no computador da gestora

Estes passos são para quem não programa. O sistema roda só neste computador: nenhum outro computador da rede consegue abrir. Onde os passos diferem, há uma linha para **Windows** e outra para **macOS**.

### Instalar (uma vez só)

1. Instale o **Python 3.13** pelo site <https://www.python.org/downloads/>.
   - **Windows:** na primeira tela do instalador, marque **Add python.exe to PATH** antes de clicar em **Install Now**.
   - **macOS:** abra o arquivo baixado e siga o instalador até o fim.
2. Copie a pasta do programa (a pasta onde está este README) para um lugar fixo, por exemplo **Documentos**. Não mude a pasta de lugar depois.
3. Abra um terminal **dentro da pasta do programa**:
   - **Windows:** abra a pasta no Explorador de Arquivos, clique na barra de endereço, digite `cmd` e aperte Enter.
   - **macOS:** abra o aplicativo **Terminal**, digite `cd ` (com um espaço no fim), arraste a pasta do programa para a janela e aperte Enter.
4. Copie e cole no terminal, uma linha por vez, apertando Enter depois de cada uma:
   - **Windows:**

     ```bat
     py -3.13 -m venv .venv
     .venv\Scripts\pip install -r requirements.txt
     copy .env.exemplo .env
     .venv\Scripts\python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

   - **macOS:**

     ```sh
     python3.13 -m venv .venv
     .venv/bin/pip install -r requirements.txt
     cp .env.exemplo .env
     .venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

   A última linha mostra uma chave secreta, uma sequência longa de letras e símbolos. Deixe o terminal aberto.
5. Abra o arquivo **.env** da pasta do programa num editor de texto (Bloco de Notas no Windows, TextEdit no macOS) e preencha:
   - `SECRET_KEY=`: cole a chave do passo anterior, no lugar de `troque-por-uma-chave-gerada`;
   - `PASTA_DE_ARQUIVOS=`: a pasta onde ficarão os arquivos dos Catálogos e as fotos, **fora** da pasta do programa (há exemplos no próprio arquivo). Se deixar vazio, o sistema usa `ComparadorDeCatalogos/arquivos` dentro da pasta do usuário;
   - `ANTHROPIC_API_KEY=`: pode ficar vazia; o sistema funciona sem ela.

   Salve o arquivo. O `.env` guarda segredos: não o envie para ninguém. Ele também não entra no backup.
6. Ainda no terminal, prepare o banco e crie o usuário do Responsável pela instalação (o comando pede um usuário, um e-mail, que pode ficar em branco, e uma senha):
   - **Windows:** `.venv\Scripts\python manage.py migrate` e depois `.venv\Scripts\python manage.py createsuperuser`
   - **macOS:** `.venv/bin/python manage.py migrate` e depois `.venv/bin/python manage.py createsuperuser`

### Iniciar o sistema

1. Na pasta do programa, dê um duplo clique em:
   - **Windows:** `iniciar.bat`;
   - **macOS:** `iniciar.command`. Na primeira vez, o macOS pode recusar o arquivo. Nesse caso, clique nele com o botão direito, escolha **Abrir** e confirme.
2. Abre uma janela preta (o terminal do sistema) e, alguns segundos depois, o navegador no endereço <http://127.0.0.1:8000/>. Se o navegador não abrir sozinho, abra esse endereço.
3. Deixe a janela preta aberta enquanto usa o sistema. Para parar, feche a janela.

Se aparecer a página **Algo deu errado**, o detalhe do erro fica escrito na janela preta. Tire uma foto dessa janela para quem cuida da instalação.

### Cadastrar o primeiro Gestor e as Lojas

1. Com o sistema iniciado, abra <http://127.0.0.1:8000/admin/> e entre com o usuário do Responsável criado na instalação.
2. Em **Gestores › Adicionar**, cadastre cada Gestor com usuário e senha. Na página do Gestor, a seção **Lojas** recebe as Lojas dele.
3. Ou, em **Lojas › Adicionar**, cadastre uma Loja escolhendo o Gestor dono.
4. Clique em **Encerrar sessão**, abra <http://127.0.0.1:8000/> e entre com o usuário de um Gestor.

Não há autocadastro nem recuperação de senha: só o Responsável cria Gestores.

## Fazer backup e restaurar

O backup é um único arquivo `.zip`, com a data e a hora no nome (por exemplo `backup-comparador-2026-11-05_14-30-07.zip`). Ele leva o banco e a pasta de arquivos inteira: os arquivos dos Catálogos, as planilhas de preços, as imagens de página e as fotos. Pode ser feito com o sistema aberto. O `.env` não entra no backup.

> **O backup no mesmo computador não protege contra defeito no computador. Copie o arquivo para um pendrive ou para a nuvem pelo menos uma vez por semana.**
>
> O backup cresce com as fotos. O primeiro Catálogo grande de um Fornecedor pode ocupar dezenas de MB; os seguintes, quase nada, porque a mesma foto não é guardada duas vezes.

### Fazer um backup

1. Abra um terminal dentro da pasta do programa (passo 3 de **Instalar**).
2. Escolha a pasta onde o backup vai ficar, por exemplo o pendrive. Ela precisa existir.
3. Rode o comando, trocando o caminho pelo da pasta escolhida:
   - **Windows:** `.venv\Scripts\python manage.py fazer_backup E:\backups`
   - **macOS:** `.venv/bin/python manage.py fazer_backup /Volumes/PENDRIVE/backups`

   No macOS, em vez de digitar o caminho, você pode arrastar a pasta para a janela do terminal.
4. O terminal responde `Pronto: backup gravado em ...` com o caminho do arquivo. Se a pasta não existir, ele responde `A pasta de destino não existe: ...` e nada é gravado.

### Restaurar um backup

A restauração só funciona numa **instalação vazia**, sem nenhum Catálogo: ela substitui o banco inteiro pelo do backup. Assim, nada feito depois do backup se perde por engano.

1. Num computador novo (ou depois de um defeito), faça os passos 1 a 5 de **Instalar**. No passo 6, rode só o `migrate` e **não** crie o usuário do Responsável: os usuários voltam com o backup.
2. Copie o arquivo do backup para o computador.
3. No terminal, dentro da pasta do programa:
   - **Windows:** `.venv\Scripts\python manage.py restaurar_backup C:\Users\gestora\Downloads\backup-comparador-2026-11-05_14-30-07.zip`
   - **macOS:** `.venv/bin/python manage.py restaurar_backup ~/Downloads/backup-comparador-2026-11-05_14-30-07.zip`
4. O terminal responde `Pronto: backup ... restaurado.`. Inicie o sistema e entre com os mesmos usuários e senhas de antes.

Se o terminal responder `Esta instalação já tem dados...`, a instalação não está vazia e nada foi alterado. Se responder `Este arquivo não é um backup do Comparador de Catálogos.`, o arquivo escolhido não foi gerado pelo `fazer_backup`.

## Para quem programa

### Preparar o ambiente

Requer Python 3.13.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.exemplo .env   # e preencha; para desenvolver, use DEBUG=True
.venv/bin/python manage.py migrate
```

Sem o `.env`, o sistema inicia com valores de desenvolvimento (SECRET_KEY de desenvolvimento, `DEBUG=False`, sem chave da LLM, pasta de arquivos em `~/ComparadorDeCatalogos/arquivos`) e avisa no terminal. Com `DEBUG=False`, o `runserver` só serve o CSS com `--insecure`, como fazem os scripts `iniciar`. Com `DEBUG=True`, `.venv/bin/python manage.py runserver` basta.

### Mover os arquivos de `media/` para a pasta de arquivos

Até o ticket 11, os arquivos enviados ficavam em `media/`, dentro do repositório. Agora ficam na pasta do `PASTA_DE_ARQUIVOS`. O banco guarda o caminho de cada arquivo relativo à pasta (`importacoes/2026/11/...`), então basta mover o conteúdo, mantendo as subpastas:

1. Pare o sistema.
2. Defina `PASTA_DE_ARQUIVOS` no `.env` (ou use o padrão `~/ComparadorDeCatalogos/arquivos`).
3. Mova o conteúdo de `media/` para essa pasta:

   ```sh
   mkdir -p ~/ComparadorDeCatalogos/arquivos
   mv media/* ~/ComparadorDeCatalogos/arquivos/
   ```

4. Confira que a pasta tem `importacoes/` e abra um Catálogo de teste no sistema. Depois, apague a pasta `media/` vazia.

### Rodar os testes

```sh
.venv/bin/python manage.py test
```

Os testes entram pelos casos de uso de cada módulo (por exemplo, `catalogos/casos_de_uso.py`) e usam o banco de teste do Django. Nenhum teste chama serviços externos.

### Skills adaptadas

A skill `tdd` (`.claude/skills/tdd/`) vem do pacote mattpocock/skills e foi adaptada em 2026-11-05 para ler as referências uma vez por sessão e não chamar a skill `codebase-design`, que não está instalada. Motivo: reduzir custo de contexto nas sessões longas de TDD. Uma atualização do pacote desfaz essa adaptação.

### Conferir o leitor com os Catálogos reais

Os Catálogos reais ficam fora do repositório (a pasta `catalogos-exemplo/` está no `.gitignore`) e nunca entram nos testes. Para conferir, na sua máquina, que o leitor do Layout A continua lendo os arquivos reais:

```sh
.venv/bin/python ferramentas/conferir_catalogos_reais.py catalogos-exemplo
```

O script não faz parte da suíte de testes. Para cada arquivo, numerado pela ordem alfabética do nome, ele imprime só números: se o Layout A foi reconhecido, quantos cartões e quantas Ofertas, quantas sem preço e sem Caixa, e o tempo. Nenhum código, descrição, preço ou nome de marca aparece na saída, então ela pode ser compartilhada.
