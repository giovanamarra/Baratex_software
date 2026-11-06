#!/bin/sh
# Inicia o Comparador de Catálogos no macOS. Duplo clique no Finder.
# Só este computador acessa (127.0.0.1). Para parar, feche esta janela.
cd "$(dirname "$0")" || exit 1

.venv/bin/python manage.py migrate --noinput || { echo "Não foi possível preparar o banco. Veja a mensagem acima."; read -r _; exit 1; }

echo ""
echo "Comparador de Catálogos: abra http://127.0.0.1:8000/ no navegador."
echo "Para parar o sistema, feche esta janela."
echo ""
(sleep 3; open "http://127.0.0.1:8000/") &
# --insecure serve o CSS e os logos com DEBUG desligado; só vale aqui porque o endereço é 127.0.0.1.
exec .venv/bin/python manage.py runserver 127.0.0.1:8000 --insecure --noreload
