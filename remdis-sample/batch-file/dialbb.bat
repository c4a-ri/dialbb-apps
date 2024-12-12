@echo off
title dialbb.py
mode con: cols=100 lines=26

:: remdis/に移動 (scriptの一つ上)
cd /d %~dp0\..

:: アプリの設定値
set app_dir=modules
set app_prog=dialbb_dialogue.py
set app_conf=..\config\dialbb\chatgpt\config_ja.yml
::set app_conf=..\config\dialbb\lab_app_ja\config.yml

:: Pythonスクリプトの実行
poetry run cmd /c "cd %app_dir%&python %app_prog% %app_conf%"
