@echo off
rem Starts the listener for this machine. Leave this window open; Ctrl+C stops it.
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\listener.py %*
) else (
  python tools\listener.py %*
)
pause
