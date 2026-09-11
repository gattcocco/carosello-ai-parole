@echo off
setlocal
python "%~dp0open.py"
if errorlevel 1 (
  echo Consulta README.md per Python, Kdenlive e media necessari.
  pause
  exit /b 1
)
