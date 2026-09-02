@echo off
cd /d "%~dp0"
echo Starting Clinical Lab AI Analyzer backend...
venv\Scripts\python.exe run_server.py
