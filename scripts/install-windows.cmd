@echo off
setlocal EnableExtensions
set "PROJECT=FossilScope"
set "CMD=fossilscope"
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
set "CONSTRAINTS=%REPO_ROOT%\requirements\runtime-py311.lock"
set "FIRST_PARTY=%REPO_ROOT%\requirements\first-party.txt"
set "INSTALL_ROOT=%USERPROFILE%\.fossilscope"
set "VENV=%INSTALL_ROOT%\venv"
set "BIN_DIR=%USERPROFILE%\.local\bin"
set "PY_CMD="
where py >nul 2>&1 && (py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1 && set "PY_CMD=py -3")
if not defined PY_CMD where python >nul 2>&1 && (python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1 && set "PY_CMD=python")
if not defined PY_CMD (echo Python 3.11+ is required.& exit /b 2)
if not exist "%INSTALL_ROOT%" mkdir "%INSTALL_ROOT%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
if exist "%VENV%\Scripts\python.exe" ("%VENV%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1 || rmdir /s /q "%VENV%") else if exist "%VENV%" rmdir /s /q "%VENV%"
if not exist "%VENV%\Scripts\python.exe" %PY_CMD% -m venv "%VENV%" || exit /b 3
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel || exit /b 3
if defined SRIC_CORE_SOURCE (
  if not exist "%SRIC_CORE_SOURCE%\pyproject.toml" exit /b 3
  "%VENV%\Scripts\python.exe" -m pip install --upgrade -c "%CONSTRAINTS%" "%SRIC_CORE_SOURCE%" "%REPO_ROOT%" || exit /b 3
) else (
  if not exist "%FIRST_PARTY%" exit /b 3
  "%VENV%\Scripts\python.exe" -m pip install --upgrade -c "%CONSTRAINTS%" -r "%FIRST_PARTY%" "%REPO_ROOT%" || exit /b 3
)
"%VENV%\Scripts\python.exe" -m pip check || exit /b 3
"%VENV%\Scripts\python.exe" -c "import sric.web_console, sric.web_workbench" || exit /b 3
>"%BIN_DIR%\%CMD%.cmd" echo @"%VENV%\Scripts\%CMD%.exe" %%*
"%VENV%\Scripts\python.exe" -m sric.install_path "%BIN_DIR%" || exit /b 3
set "SENTINEL_BANNER=never"
"%VENV%\Scripts\%CMD%.exe" doctor --json >nul || exit /b 1
"%VENV%\Scripts\%CMD%.exe" capabilities >nul || exit /b 1
"%VENV%\Scripts\%CMD%.exe" --help >nul 2>&1 || exit /b 1
"%VENV%\Scripts\%CMD%.exe" -h >nul 2>&1 || exit /b 1
"%VENV%\Scripts\%CMD%.exe" help >nul 2>&1 || exit /b 1
echo %PROJECT% installed/repaired successfully in standalone mode.
exit /b 0
