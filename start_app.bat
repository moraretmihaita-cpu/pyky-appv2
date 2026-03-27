@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0"

echo ========================================
echo   AI Ads Analyst - Local Launcher
echo ========================================
echo.

set "ROOT=%CD%"
set "FRONTEND_DIR=%ROOT%\frontend"
set "APP_MODULE=app.api_server_refactor_v1:app"
set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "FRONTEND_HOST=127.0.0.1"
set "FRONTEND_PORT=5173"
set "PYTHON_EXE="

rem Prefer local virtual environments first
if exist "%ROOT%\.venv\Scripts\python.exe" set "PYTHON_EXE=%ROOT%\.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%ROOT%\venv\Scripts\python.exe" set "PYTHON_EXE=%ROOT%\venv\Scripts\python.exe"

rem Common Windows Python locations
if not defined PYTHON_EXE if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYTHON_EXE if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined PYTHON_EXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python310\python.exe"
if not defined PYTHON_EXE if exist "%ProgramFiles%\Python312\python.exe" set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
if not defined PYTHON_EXE if exist "%ProgramFiles%\Python311\python.exe" set "PYTHON_EXE=%ProgramFiles%\Python311\python.exe"
if not defined PYTHON_EXE if exist "%ProgramFiles%\Python310\python.exe" set "PYTHON_EXE=%ProgramFiles%\Python310\python.exe"

rem PATH fallback
if not defined PYTHON_EXE (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=py"
)
if not defined PYTHON_EXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
  echo [ERROR] Nu am gasit Python.
  echo.
  echo Solutii rapide:
  echo  1. Creeaza un mediu local:  py -m venv .venv
  echo  2. Sau instaleaza Python si bifeaza "Add Python to PATH"
  echo  3. Sau pune python.exe in .\.venv\Scripts\python.exe
  echo.
  pause
  exit /b 1
)

echo [OK] Python: %PYTHON_EXE%

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm nu este disponibil in PATH.
  echo Instaleaza Node.js LTS si incearca din nou.
  pause
  exit /b 1
)

echo [OK] npm gasit.

if not exist "%FRONTEND_DIR%" (
  echo [ERROR] Folderul frontend nu exista: %FRONTEND_DIR%
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
  echo [INFO] node_modules lipseste. Rulez npm install...
  pushd "%FRONTEND_DIR%"
  call npm install
  if errorlevel 1 (
    echo [ERROR] npm install a esuat.
    popd
    pause
    exit /b 1
  )
  popd
)

echo.
echo [INFO] Pornesc backend-ul pe http://%BACKEND_HOST%:%BACKEND_PORT%
start "AI Ads Analyst - Backend" cmd /k "cd /d "%ROOT%" && "%PYTHON_EXE%" -m uvicorn %APP_MODULE% --host %BACKEND_HOST% --port %BACKEND_PORT% --reload"

echo [INFO] Astept 3 secunde...
timeout /t 3 /nobreak >nul

echo [INFO] Pornesc frontend-ul pe http://%FRONTEND_HOST%:%FRONTEND_PORT%
start "AI Ads Analyst - Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev -- --host %FRONTEND_HOST% --port %FRONTEND_PORT%"

echo [INFO] Astept 4 secunde...
timeout /t 4 /nobreak >nul

echo [INFO] Deschid aplicatia in browser...
start "" "http://%FRONTEND_HOST%:%FRONTEND_PORT%"

echo.
echo [DONE] Aplicatia a fost lansata.
exit /b 0
