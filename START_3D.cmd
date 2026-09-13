@echo off
cd /d "%~dp0"
set "FYP_BATCH=0"
set "FYP_CAPTURE=1"
set "FYP_VIDEO=0"
set "FYP_SEED=0"
set "FYP_WEBOTS=C:\Users\User\Documents\ChatGPT\fyp\tools\Webots\msys64\mingw64\bin\webots.exe"
if not exist "%FYP_WEBOTS%" (
  echo Webots was not found. Update FYP_WEBOTS in this launcher.
  pause
  exit /b 1
)
start "" "%FYP_WEBOTS%" --mode=realtime --stdout --stderr "%~dp0worlds\human_following.wbt"
