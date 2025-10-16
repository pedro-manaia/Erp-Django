
@echo on
setlocal EnableExtensions
set HERE=%~dp0

REM 1) Instala dependências automaticamente e mostra logs nesta janela
python -u "%HERE%tray_server.py" --install-deps

REM 2) Inicia o TRAY em background, sem segurar esta janela
start "" /D "%HERE%" /B pythonw "%HERE%tray_server.py"

echo.
echo [INFO] Tray iniciado. Esta janela fechará em 5 segundos...
timeout /t 5 /nobreak >nul
exit /b
