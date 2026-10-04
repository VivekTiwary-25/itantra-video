@echo off
rem Build and render the cards (render machines only; the lead runs this over SSH).
rem Stems first: ticks (cards_sfx.wav) and narration N8/N9 (cards_dx.wav); lengths follow film/common/narration_v4.json.
python "%~dp0cards_sfx.py"
if errorlevel 1 exit /b 1
python "%~dp0cards_dx.py"
if errorlevel 1 exit /b 1
python "%~dp0build.py" --render
