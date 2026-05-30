@echo off
REM Script de création de la tâche planifiée pour purge automatique des logs de sécurité
REM À exécuter en tant qu'administrateur

set PYTHON_EXE=C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe
set PROJECT_DIR=C:\Users\User\Desktop\Compta_mat
set MANAGE_PY=%PROJECT_DIR%\manage.py
set TASK_NAME=PurgeDocumentSecurityLogs
set START_TIME=02:00
set START_DATE=2026/04/01

schtasks /Create /SC DAILY /TN "%TASK_NAME%" /TR "\"%PYTHON_EXE%\" \"%MANAGE_PY%\" purge_document_security_logs" /ST %START_TIME% /CD %START_DATE% /RL HIGHEST /F

echo Tâche planifiée "%TASK_NAME%" créée pour exécuter la purge automatique chaque nuit à %START_TIME%.