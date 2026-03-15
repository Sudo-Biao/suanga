@echo off
:: ============================================================
:: start.bat - BaGua System Windows Launcher (cmd.exe)
:: ============================================================
:: Usage:
::   start.bat              start backend + frontend
::   start.bat backend      backend only
::   start.bat frontend     frontend only
::   start.bat stop         stop all services
::   start.bat install      install dependencies only
::
:: Prefer start.ps1 (PowerShell) for coloured output.
:: ============================================================

setlocal EnableDelayedExpansion

:: Force code page 936 (GBK) - safer than 65001 on Chinese Windows
chcp 936 >nul 2>&1

set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "BACKEND_DIR=%SCRIPT_DIR%"
set "FRONTEND_DIR=%SCRIPT_DIR%\frontend"
set "ENV_FILE=%SCRIPT_DIR%\.env"
set "ENV_EXAMPLE=%SCRIPT_DIR%\.env.example"

set "BACKEND_PORT=8888"
set "FRONTEND_PORT=5173"

:: ── Stable directories that SURVIVE zip re-extraction ─────────────────
:: Venv lives in %USERPROFILE%\.bagua\venv — shared across all versions.
:: node_modules stays inside frontend\ (npm requires it there).
set "VENV_DIR=%USERPROFILE%\.bagua\venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"
set "VENV_UVICORN=%VENV_DIR%\Scripts\uvicorn.exe"

:: Marker files track what was last installed (hash of requirements/package)
set "MARKERS_DIR=%USERPROFILE%\.bagua\markers"
if not exist "%MARKERS_DIR%" mkdir "%MARKERS_DIR%"
set "REQ_MARKER=%MARKERS_DIR%\requirements.hash"
set "PKG_MARKER=%MARKERS_DIR%\package.hash"

:: Use %TEMP%\bagua_run for PIDs and logs
set "RUN_DIR=%TEMP%\bagua_run"
if not exist "%RUN_DIR%" mkdir "%RUN_DIR%"

set "BACKEND_PID=%RUN_DIR%\backend.pid"
set "FRONTEND_PID=%RUN_DIR%\frontend.pid"
set "BACKEND_LOG=%RUN_DIR%\backend.log"
set "FRONTEND_LOG=%RUN_DIR%\frontend.log"

call :banner

set "MODE=%~1"
if "%MODE%"=="" set "MODE=all"

if /i "%MODE%"=="install"  goto MODE_INSTALL
if /i "%MODE%"=="backend"  goto MODE_BACKEND
if /i "%MODE%"=="frontend" goto MODE_FRONTEND
if /i "%MODE%"=="stop"     goto MODE_STOP
goto MODE_ALL

:: ============================================================
:MODE_INSTALL
call :check_python
if errorlevel 1 exit /b 1
call :check_node
if errorlevel 1 exit /b 1
call :install_backend
call :install_frontend
echo [OK] All dependencies installed.
goto END

:: ============================================================
:MODE_BACKEND
call :check_python
if errorlevel 1 exit /b 1
call :setup_env
call :install_backend
if errorlevel 1 exit /b 1
call :start_backend
call :show_summary
echo Backend log: %BACKEND_LOG%
echo Press any key to exit (backend keeps running)...
pause >nul
goto END

:: ============================================================
:MODE_FRONTEND
call :check_node
if errorlevel 1 exit /b 1
call :start_frontend
call :show_summary
echo Frontend log: %FRONTEND_LOG%
echo Press any key to exit (frontend keeps running)...
pause >nul
goto END

:: ============================================================
:MODE_STOP
call :stop_all
goto END

:: ============================================================
:MODE_ALL
call :check_python
if errorlevel 1 exit /b 1
call :check_node
if errorlevel 1 exit /b 1
call :setup_env

:: These functions self-skip when nothing has changed
call :install_backend
if errorlevel 1 exit /b 1
call :install_frontend

call :start_backend
call :start_frontend
call :show_summary

timeout /t 2 /nobreak >nul
start "" "http://localhost:%FRONTEND_PORT%"

echo Backend log : %TEMP%\bagua_run\backend.log
echo Frontend log: %TEMP%\bagua_run\frontend.log
echo.
echo Both services are running in the background.
echo Run   start.bat stop   to shut them down.
echo.
pause >nul
goto END

:: ============================================================
:: FUNCTIONS
:: ============================================================

:banner
echo.
echo   +--------------------------------------------+
echo   ^|      BaGua System  Eight Trigrams          ^|
echo   ^|  BaZi . LiuYao . QiMen . FengShui         ^|
echo   +--------------------------------------------+
echo.
goto :eof

:: ?? check_python ?????????????????????????????????????????
:check_python
set "PYTHON_EXE="
for %%P in (python python3 py) do (
    if "!PYTHON_EXE!"=="" (
        %%P --version >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=%%P"
    )
)
if "!PYTHON_EXE!"=="" (
    echo [ERROR] Python 3.10+ not found.
    echo         Download: https://www.python.org/downloads/
    echo         IMPORTANT: tick "Add Python to PATH" during install!
    exit /b 1
)
for /f "tokens=2" %%V in ('!PYTHON_EXE! --version 2^>^&1') do echo [ OK ] Python %%V found  ^(!PYTHON_EXE!^)
exit /b 0

:: ?? check_node ???????????????????????????????????????????
:check_node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 18+ not found.
    echo         Download: https://nodejs.org/
    exit /b 1
)
for /f %%V in ('node --version') do echo [ OK ] Node %%V found
exit /b 0

:: ?? setup_env ????????????????????????????????????????????
:setup_env
:: Always regenerate .env from .env.example so stale settings
:: (like a bad CORS_ORIGINS line) cannot crash the backend.
if not exist "!ENV_EXAMPLE!" goto skip_env_setup
copy /y "!ENV_EXAMPLE!" "!ENV_FILE!" >nul
echo [ OK ] .env refreshed from .env.example
:skip_env_setup
goto :eof

:: ?? install_backend ??????????????????????????????????????
:install_backend
echo [ .. ] Checking Python environment...
cd /d "!BACKEND_DIR!"

:: Create venv if missing
if exist "!VENV_DIR!" goto skip_venv_create
echo [ .. ] Creating virtual environment at !VENV_DIR! ...
"!PYTHON_EXE!" -m venv "!VENV_DIR!"
if not exist "!VENV_DIR!\Scripts\python.exe" (
    echo [ERROR] venv creation failed.
    echo         Try running:  python -m venv "!VENV_DIR!"
    exit /b 1
)
echo [ OK ] Created virtual environment
:: Force pip install on fresh venv
if exist "!REQ_MARKER!" del /f "!REQ_MARKER!" >nul 2>&1
:skip_venv_create

:: Compute current requirements.txt hash
set "REQ_HASH_NEW="
for /f "skip=1 tokens=*" %%H in ('certutil -hashfile "!BACKEND_DIR!\requirements.txt" MD5 2^>nul') do (
    if "!REQ_HASH_NEW!"=="" set "REQ_HASH_NEW=%%H"
)

:: Read stored hash
set "REQ_HASH_OLD="
if exist "!REQ_MARKER!" set /p REQ_HASH_OLD=<"!REQ_MARKER!"

:: Skip pip ONLY if hash matches AND uvicorn is actually present in the venv
if "!REQ_HASH_NEW!"=="!REQ_HASH_OLD!" (
    if exist "!VENV_DIR!\Lib\site-packages\uvicorn" (
        echo [ OK ] Dependencies up to date
        goto :eof
    )
    echo [INFO] Packages missing from venv ^(reinstalling^)...
)

echo [ .. ] Installing packages...
"!VENV_DIR!\Scripts\python.exe" -m pip install -r "!BACKEND_DIR!\requirements.txt"
if errorlevel 1 (
    echo [ERROR] pip install failed — check your internet connection
    exit /b 1
)
echo [ OK ] Backend dependencies installed

:: Save new hash
echo !REQ_HASH_NEW!>"!REQ_MARKER!"
goto :eof

:: install_frontend
:install_frontend
echo [ .. ] Checking Node dependencies...

:: Compute current package.json hash
set "PKG_HASH_NEW="
for /f "skip=1 tokens=*" %%H in ('certutil -hashfile "!FRONTEND_DIR!\package.json" MD5 2^>nul') do (
    if "!PKG_HASH_NEW!"=="" set "PKG_HASH_NEW=%%H"
)

:: Read stored hash
set "PKG_HASH_OLD="
if exist "!PKG_MARKER!" set /p PKG_HASH_OLD=<"!PKG_MARKER!"

:: Skip if hash unchanged AND node_modules present
if exist "!FRONTEND_DIR!\node_modules" (
    if "!PKG_HASH_NEW!"=="!PKG_HASH_OLD!" (
        echo [ OK ] Node dependencies up to date
        goto :eof
    )
)

echo [ .. ] Installing Node packages...

:: Run npm install via a helper bat — npm outputs thousands of lines which
:: shifts CMD's file-read pointer and causes "label not found" errors.
set "NHELPER=%TEMP%\bagua_npm_install.bat"
(
    echo @echo off
    echo cd /d "!FRONTEND_DIR!"
    echo npm install
) > "!NHELPER!"
call "!NHELPER!"
if errorlevel 1 (
    echo [ERROR] npm install failed — check your internet connection
    exit /b 1
)
echo [ OK ] Frontend dependencies installed

echo !PKG_HASH_NEW!>"!PKG_MARKER!"
goto :eof

:: ?? start_backend ????????????????????????????????????????
:start_backend
call :stop_pid "%BACKEND_PID%" "backend"

echo [ .. ] Starting backend on port !BACKEND_PORT! ...

:: IMPORTANT: We always use ".venv\Scripts\python.exe -m uvicorn" rather than
:: "uvicorn.exe" because:
::   1. The helper bat runs in a fresh cmd.exe with NO conda activation.
::   2. uvicorn.exe inside a venv built on conda fails without conda on PATH.
::   3. python.exe -m uvicorn is fully self-contained inside the venv.
set "VENV_PY=!VENV_DIR!\Scripts\python.exe"

if not exist "!VENV_PY!" (
    echo [ERROR] Virtual environment not found: !VENV_PY!
    echo         Run:  start.bat install
    exit /b 1
)

:: Write a disposable helper script to %TEMP%
::   - Sets its own working directory  (fixes: start ignores cd /d)
::   - Log path is %TEMP%\bagua_run\   (fixes: spaces-in-path quoting)
::   - Uses python -m uvicorn          (fixes: conda env not inherited)
set "BHELPER=%TEMP%\bagua_run_backend.bat"
(
    echo @echo off
    echo cd /d "!BACKEND_DIR!"
    echo "!VENV_PY!" -m uvicorn main:app --host 0.0.0.0 --port !BACKEND_PORT! --reload ^>"!BACKEND_LOG!" 2^>^&1
) > "!BHELPER!"

start "bagua-backend" /b "!BHELPER!"

:: Give Python time to start (conda envs can be slower)
timeout /t 5 /nobreak >nul

for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr ":!BACKEND_PORT! " ^| findstr "LISTENING"') do (
    echo %%P>"!BACKEND_PID!"
    echo [ OK ] Backend started  ^(PID %%P^)
    goto backend_wait
)
echo [WARN] Could not capture backend PID - process may still be starting

:backend_wait
call :wait_port !BACKEND_PORT! "Backend"
:: If backend never came up, print the log so user sees the real error
netstat -ano 2>nul | findstr ":!BACKEND_PORT! " | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Backend failed to start. Last log lines:
    echo -----------------------------------------------
    if exist "!BACKEND_LOG!" ( type "!BACKEND_LOG!" ) else ( echo   ^(log file not found^) )
    echo -----------------------------------------------
    echo   Log file: !BACKEND_LOG!
    echo.
)
goto :eof

:: ?? start_frontend ???????????????????????????????????????
:start_frontend
call :stop_pid "%FRONTEND_PID%" "frontend"

if exist "!FRONTEND_DIR!\node_modules" goto skip_npm_install
echo [WARN] node_modules missing - running npm install...
set "NHELPER2=%TEMP%\bagua_npm_install2.bat"
(
    echo @echo off
    echo cd /d "!FRONTEND_DIR!"
    echo npm install
) > "!NHELPER2!"
call "!NHELPER2!"
:skip_npm_install

echo [ .. ] Starting frontend on port !FRONTEND_PORT! ...

:: Same helper-bat technique as backend
set "FHELPER=%TEMP%\bagua_run_frontend.bat"
(
    echo @echo off
    echo cd /d "!FRONTEND_DIR!"
    echo npm run dev -- --host 0.0.0.0 ^>^>"!FRONTEND_LOG!" 2^>^&1
) > "!FHELPER!"

start "bagua-frontend" /b "!FHELPER!"

timeout /t 4 /nobreak >nul
for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr ":!FRONTEND_PORT! " ^| findstr "LISTENING"') do (
    echo %%P>"!FRONTEND_PID!"
    echo [ OK ] Frontend started  ^(PID %%P^)
    goto frontend_wait
)
echo [WARN] Could not capture frontend PID - process may still be starting

:frontend_wait
call :wait_port !FRONTEND_PORT! "Frontend"
goto :eof

:: ?? stop_all ?????????????????????????????????????????????
:stop_all
echo [ .. ] Stopping all services...
call :stop_pid "%BACKEND_PID%"  "backend"
call :stop_pid "%FRONTEND_PID%" "frontend"
echo [ OK ] Done.
goto :eof

:: ?? stop_pid(file, label) ????????????????????????????????
:stop_pid
if exist "%~1" (
    set /p "SPID="<"%~1"
    if not "!SPID!"=="" (
        taskkill /f /pid !SPID! >nul 2>&1
        if not errorlevel 1 echo [STOP] Stopped %~2  ^(PID !SPID!^)
    )
    del /f "%~1" >nul 2>&1
)
goto :eof

:: ?? wait_port(port, label) ???????????????????????????????
:wait_port
set "_P=%~1"
set "_L=%~2"
echo [ .. ] Waiting for %_L% on port %_P% ...
for /l %%I in (1,1,40) do (
    netstat -ano 2>nul | findstr ":%_P% " | findstr "LISTENING" >nul 2>&1
    if not errorlevel 1 (
        echo [ OK ] %_L% is up  --^>  http://localhost:%_P%
        goto :eof
    )
    timeout /t 1 /nobreak >nul
)
echo [WARN] %_L% did not respond in 40s - check log: %TEMP%\bagua_run
goto :eof

:: ?? show_summary ?????????????????????????????????????????
:show_summary
echo.
echo   +--------------------------------------------+
echo   ^|  Backend   --^>  http://localhost:%BACKEND_PORT%      ^|
echo   ^|  API Docs  --^>  http://localhost:%BACKEND_PORT%/docs ^|
echo   ^|  Frontend  --^>  http://localhost:%FRONTEND_PORT%     ^|
echo   +--------------------------------------------+
echo.
goto :eof

:END
endlocal
