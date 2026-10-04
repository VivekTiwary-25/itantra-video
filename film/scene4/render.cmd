@echo off
rem Stage local media, render the fallback scene, and mux the narration/ticks.
setlocal
pushd "%~dp0"
python build.py || goto :fail
python audio.py || goto :fail
for /f "usebackq delims=" %%R in (`python -c "import json;print(json.load(open(r'..\..\machine.local.json'))['renders_dir'])"`) do set "RENDERS=%%R"
call hyperframes.cmd check "%~dp0." || goto :fail
call hyperframes.cmd render "%~dp0." -q high -f 30 -o "%RENDERS%\scene4\scene4_picture.mp4" || goto :fail
ffmpeg -v error -y -i "%RENDERS%\scene4\scene4_picture.mp4" -i "%RENDERS%\scene4\scene4_audio.wav" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest "%RENDERS%\scene4\scene4.mp4" || goto :fail
popd
exit /b 0
:fail
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%
