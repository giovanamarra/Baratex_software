@echo off
rem Inicia o Comparador de Catalogos no Windows. Duplo clique no Explorador de Arquivos.
rem So este computador acessa (127.0.0.1). Para parar, feche esta janela.
cd /d "%~dp0"

.venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 (
  echo Nao foi possivel preparar o banco. Veja a mensagem acima.
  pause
  exit /b 1
)

echo.
echo Comparador de Catalogos: abra http://127.0.0.1:8000/ no navegador.
echo Para parar o sistema, feche esta janela.
echo.
start "" /min cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:8000/"
rem --insecure serve o CSS e os logos com DEBUG desligado; so vale aqui porque o endereco e 127.0.0.1.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload
pause
