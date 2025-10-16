@echo off
REM Apaga qualquer banco antigo e recria 'db.sql' via migrate
setlocal
if exist db.sql del /f /q db.sql
if exist config_export.sql del /f /q config_export.sql
if exist config_export_safe.sql del /f /q config_export_safe.sql
call .venv\Scripts\activate
python manage.py migrate --run-syncdb
python manage.py createsuperuser --username pedro --email . --noinput 2>NUL
echo Done.
