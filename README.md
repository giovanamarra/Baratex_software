# Comparador de Catálogos de Fornecedores

Aplicação web em Django que importa Catálogos de Fornecedores, calcula o Preço unitário de cada Oferta e ajuda a gestora a comparar e montar Pedidos. O vocabulário está em [GLOSSARY.md](GLOSSARY.md), as decisões em [docs/adr/](docs/adr/) e o MVP em [docs/spec.md](docs/spec.md).

## Preparar o ambiente

Requer Python 3.13.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
```

## Abrir a aplicação

1. Crie o usuário do Responsável pela instalação (pede usuário, e-mail opcional e senha):

   ```sh
   .venv/bin/python manage.py createsuperuser
   ```

2. Inicie o servidor:

   ```sh
   .venv/bin/python manage.py runserver
   ```

3. Abra <http://127.0.0.1:8000/admin/>, entre com esse usuário e cadastre:
   - em **Gestores › Adicionar**, cada Gestor com usuário e senha; na página do Gestor, a seção **Lojas** recebe as Lojas dele;
   - ou em **Lojas › Adicionar**, uma Loja escolhendo o Gestor dono.

4. Saia do painel e abra <http://127.0.0.1:8000/>. Entre com o usuário de um Gestor para ver as Lojas dele e os Fornecedores do grupo.

Não há autocadastro nem recuperação de senha: só o Responsável cria Gestores.

## Rodar os testes

```sh
.venv/bin/python manage.py test
```

Os testes entram pelos casos de uso de cada módulo (por exemplo, `catalogos/casos_de_uso.py`) e usam o banco de teste do Django. Nenhum teste chama serviços externos.

## Conferir o leitor com os Catálogos reais

Os Catálogos reais ficam fora do repositório (a pasta `catalogos-exemplo/` está no `.gitignore`) e nunca entram nos testes. Para conferir, na sua máquina, que o leitor do Layout A continua lendo os arquivos reais:

```sh
.venv/bin/python ferramentas/conferir_catalogos_reais.py catalogos-exemplo
```

O script não faz parte da suíte de testes. Para cada arquivo, numerado pela ordem alfabética do nome, ele imprime só números: se o Layout A foi reconhecido, quantos cartões e quantas Ofertas, quantas sem preço e sem Caixa, e o tempo. Nenhum código, descrição, preço ou nome de marca aparece na saída, então ela pode ser compartilhada.
