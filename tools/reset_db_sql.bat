@echo off
REM === Reset do banco único SQLite: db.sql ===
setlocal
cd /d %~dp0\..
if exist db.sql del /f /q db.sql
call .venv\Scripts\activate
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput
echo.
echo [OK] Banco recriado em db.sql e estáticos coletados.
echo Para iniciar: run_windows.bat
