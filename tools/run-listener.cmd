@echo off
rem Unattended listener loop, started by `python tools\swarm.py start` (no window, survives SSH disconnects).
rem Restarts the listener whenever it exits (code update, crash, hang killed by the supervisor), 10 s apart,
rem and stops only when local\listener.stop exists. Output: local\logs\listener-console.log
rem For a visible window by hand, use tools\start-listener.cmd instead.
cd /d "%~dp0.."
if not exist local\logs mkdir local\logs
set PY=python
if exist local\python.txt set /p PY=<local\python.txt
:run
if exist local\listener.stop goto end
"%PY%" tools\listener.py >> local\logs\listener-console.log 2>&1
if exist local\listener.stop goto end
ping -n 11 127.0.0.1 >nul
goto run
:end
