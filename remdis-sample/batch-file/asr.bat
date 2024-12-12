@echo off
title asr.py
mode con: cols=100 lines=26

:: remdis/に移動 (scriptの一つ上)
cd /d %~dp0\..

:: Pythonスクリプトの実行
poetry run cmd /c "cd modules & python asr.py"

pause
