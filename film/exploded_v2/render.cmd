@echo off
rem Exploded view v2: stage layers + parts, write ticks, render (render machines only; the lead runs this).
setlocal
pushd "%~dp0"
python build.py || goto :fail
python ticks.py || goto :fail
for /f "usebackq delims=" %%R in (`python -c "import json;print(json.load(open(r'..\..\machine.local.json'))['renders_dir'])"`) do set "RENDERS=%%R"
call hyperframes.cmd render "%~dp0." -q high -f 30 -o "%RENDERS%\exploded_v2\exploded_v2.mp4" || goto :fail
popd
exit /b 0
:fail
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
