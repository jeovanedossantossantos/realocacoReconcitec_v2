::  @echo off
::  cd /d %~dp0

::  echo Iniciando o aplicativo Streamlit...
:: call venv\Scripts\activate

::  streamlit run app.py

@echo off
cd /d %~dp0
echo ----------------------------------
echo Iniciando o aplicativo Streamlit...
echo ----------------------------------

:: 1. Checa se a venv existe
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

:: 2. Ativa a venv
call venv\Scripts\activate

:: 3. Instala dependências se necessário
echo Instalando dependências...
pip install --upgrade pip >nul
pip install -r requirements.txt

:: 4. Inicia o app
echo Executando o app...
streamlit run app.py

:: 5. Aguarda usuário pressionar uma tecla após o fechamento
echo.
echo App finalizado. Pressione qualquer tecla para sair.
pause >nul

