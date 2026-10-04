@echo off
setlocal
pushd "%~dp0"
node build.js --render
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
