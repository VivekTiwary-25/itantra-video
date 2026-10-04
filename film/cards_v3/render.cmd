@echo off
rem Build and render the cards (render machines only; the lead runs this over SSH).
python "%~dp0build.py" --render
