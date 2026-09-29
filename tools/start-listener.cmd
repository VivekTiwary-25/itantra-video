@echo off
rem Starts the listener for this machine. Leave this window open; Ctrl+C stops it.
rem When a git pull brings new tool code, the listener exits with code 75 between tasks and this script starts it again.
cd /d "%~dp0.."
:run
where python >nul 2>nul
if %errorlevel%==0 (
  python tools\listener.py %*
) else (
  py -3 tools\listener.py %*
)
if %errorlevel%==75 (
  echo Listener code was updated. Restarting...
  goto run
)
pause
