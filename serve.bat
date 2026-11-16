@echo off
rem Sobe a interface do Oráculo na rede local (porta 8000).
rem Acesse pelo computador em http://localhost:8000 e pelo celular em http://IP_DO_PC:8000
cd /d "%~dp0static"
echo Oraculo rodando em http://0.0.0.0:8000  (Ctrl+C para parar)
python -m http.server 8000 --bind 0.0.0.0
