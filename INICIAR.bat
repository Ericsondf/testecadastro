@echo off
title Atlas Toldos - Sistema de Gestao
color 0B
echo.
echo  ==========================================
echo    ATLAS TOLDOS - Sistema de Gestao
echo  ==========================================
echo.
echo  Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERRO: Python nao encontrado!
    echo  Baixe em: https://python.org/downloads
    echo  Marque "Add Python to PATH" ao instalar!
    pause
    exit /b
)
echo  Python OK!
echo.
echo  Instalando dependencias...
pip install flask flask-cors gunicorn --quiet --break-system-packages 2>nul
pip install flask flask-cors --quiet 2>nul
echo  Dependencias OK!
echo.
echo  Iniciando servidor...
echo.
echo  Acesse no navegador: http://localhost:5000
echo  Login ADM: admin@atlastoldos.com / atlas2024
echo.
start "" http://localhost:5000
python server.py
pause
