@echo off
setlocal EnableExtensions

REM ================================================================
REM  clear_project.bat
REM  Limpa SOMENTE caches/artefatos gerados do projeto.
REM  Nao remove a venv externa (.vent) e nem o banco (db.sql).
REM  Pode ser executado de qualquer lugar; usa a raiz do projeto.
REM ================================================================

set "ROOT=%~dp0"
pushd "%ROOT%" >nul

echo [clear] Limpando caches do projeto (sem tocar na venv ou banco)...

REM 1) Bytecode Python
for /r %%F in (*.pyc *.pyo) do del /f /q "%%F" >nul 2>nul

REM 2) Pastas de cache comuns
for /d /r %%D in (__pycache__) do if exist "%%D" rd /s /q "%%D" >nul 2>nul
for /d /r %%D in (.pytest_cache .mypy_cache .ruff_cache .tox build dist htmlcov) do (
  if exist "%%D" rd /s /q "%%D" >nul 2>nul
)

REM 3) Arquivos de cobertura/logs/temp
del /f /q ".coverage" >nul 2>nul
for /r %%F in (.coverage.* *.log *.tmp) do del /f /q "%%F" >nul 2>nul

REM 4) egg-info
for /d %%D in (*.egg-info) do if exist "%%D" rd /s /q "%%D" >nul 2>nul

REM 5) staticfiles (recriado pelo collectstatic)
if exist "staticfiles" rd /s /q "staticfiles" >nul 2>nul

REM IMPORTANTE - NAO APAGAR:
REM - VENV externa: %USERPROFILE%\Documents\<nome_do_projeto>\.vent
REM - Banco SQLite: db.sql
REM - Uploads: .\media\

echo [clear] Pronto! Caches limpos com sucesso.
popd >nul

endlocal
