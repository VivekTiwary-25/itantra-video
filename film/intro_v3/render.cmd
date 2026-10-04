@echo off
setlocal
cd /d "%~dp0"
python build.py || exit /b 1
hyperframes.cmd check . || exit /b 1
for /f "usebackq delims=" %%P in (`python -c "import json,pathlib;print(pathlib.Path(json.load(open('../../machine.local.json'))['renders_dir'])/'intro_v3'/'intro_v3.mp4')"`) do set "OUTPUT=%%P"
hyperframes.cmd render . -o "%OUTPUT%" || exit /b 1
echo RENDERS:intro_v3/intro_v3.mp4
