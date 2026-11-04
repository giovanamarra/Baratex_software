<<<<<<< HEAD
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
=======
# Baratex_software
>>>>>>> cbea25f903a53a5d2582716336a3e76c7436b008
