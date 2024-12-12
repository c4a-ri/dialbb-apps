title remdis-dialbb
set script_dir=%~dp0
cd %script_dir%

:: 必要なプロセス起動batをまとめて実行する
start "" ".\input.bat"
timeout /t 1 /nobreak >nul
start "" ".\text_vap.bat"
timeout /t 1 /nobreak >nul
start "" ".\asr.bat"
timeout /t 1 /nobreak >nul
start "" ".\tts.bat"
timeout /t 1 /nobreak >nul
start "" ".\dialbb.bat"
::start "" ".\output.bat"
cd %script_dir%..\MMDAgent-EX
cscript .\run.vbs
