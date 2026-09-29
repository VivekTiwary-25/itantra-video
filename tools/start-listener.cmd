@echo off
rem Starts the listener for this machine. Leave this window open; Ctrl+C stops it.
cd /d "%~dp0.."
where python >nul 2>nul
if %errorlevel%==0 (
  python tools\listener.py %*
) else (
  py -3 tools\listener.py %*
)
pause
