@echo off
setlocal

set "SITE_URL=http://127.0.0.1:5173"
set "FRONTEND_DIR=%~dp0frontend"

if not exist "%FRONTEND_DIR%\package.json" (
  echo Could not find the Zeevan frontend folder:
  echo %FRONTEND_DIR%
  pause
  exit /b 1
)

start "Zeevan Website Dev Server" /D "%FRONTEND_DIR%" cmd /k "npm run dev -- --host 127.0.0.1"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$url='http://127.0.0.1:5173'; for($i=0; $i -lt 40; $i++){ try { Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 1 | Out-Null; Start-Process $url; exit 0 } catch { Start-Sleep -Milliseconds 500 } }; Write-Error 'The Zeevan development server did not start. Check the server window for errors.'; exit 1"
if errorlevel 1 pause

endlocal
