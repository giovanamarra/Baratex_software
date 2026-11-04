# Comparador de Catálogos de Fornecedores

Aplicação web em Django que importa Catálogos de Fornecedores, calcula o Preço unitário de cada Oferta e ajuda a gestora a comparar e montar Pedidos. O vocabulário está em [GLOSSARY.md](GLOSSARY.md), as decisões em [docs/adr/](docs/adr/) e o MVP em [docs/spec.md](docs/spec.md).

## Preparar o ambiente

Requer Python 3.13.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
```

## Rodar os testes

```sh
.venv/bin/python manage.py test
```

Os testes entram pelos casos de uso de cada módulo (por exemplo, `catalogos/casos_de_uso.py`) e usam o banco de teste do Django. Nenhum teste chama serviços externos.
