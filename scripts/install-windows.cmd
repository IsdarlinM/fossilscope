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
set "VENV_ROLLBACK=%INSTALL_ROOT%\venv.rollback"
set "BIN_DIR=%USERPROFILE%\.local\bin"
set "PY_CMD="
where py >nul 2>&1 && (py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1 && set "PY_CMD=py -3")
if not defined PY_CMD where python >nul 2>&1 && (python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>&1 && set "PY_CMD=python")
if not defined PY_CMD (echo Python 3.11+ is required.& exit /b 2)
if not exist "%INSTALL_ROOT%" mkdir "%INSTALL_ROOT%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

rem Never mutate an installed runtime in place. Move it aside first so a failed
rem repair can restore the previous environment without touching workspaces/data.
if exist "%VENV_ROLLBACK%" rmdir /s /q "%VENV_ROLLBACK%"
if exist "%VENV_ROLLBACK%" (echo Unable to remove stale runtime rollback directory. Close FossilScope/Python processes and retry.& exit /b 3)
if exist "%VENV%" (
  move /y "%VENV%" "%VENV_ROLLBACK%" >nul 2>&1 || (
    echo Unable to stage the existing FossilScope runtime for repair.
    echo Close all fossilscope.exe and Python processes using "%VENV%" and retry.
    exit /b 3
  )
)

%PY_CMD% -m venv "%VENV%" || goto :restore_runtime
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel || goto :restore_runtime
if defined SRIC_CORE_SOURCE (
  if not exist "%SRIC_CORE_SOURCE%\pyproject.toml" goto :restore_runtime
  "%VENV%\Scripts\python.exe" -m pip install --upgrade -c "%CONSTRAINTS%" "%SRIC_CORE_SOURCE%" "%REPO_ROOT%" || goto :restore_runtime
) else (
  if not exist "%FIRST_PARTY%" goto :restore_runtime
  "%VENV%\Scripts\python.exe" -m pip install --upgrade -c "%CONSTRAINTS%" -r "%FIRST_PARTY%" "%REPO_ROOT%" || goto :restore_runtime
)
"%VENV%\Scripts\python.exe" -m pip check || goto :restore_runtime
"%VENV%\Scripts\python.exe" -c "import annotated_types, pydantic, fossilscope; import importlib.metadata as m; assert m.version('fossilscope') == '0.5.15'; import sric.web_console, sric.web_workbench, sric.web_security_workspace, sric.web_catalog, sric.web_runtime, sric.web_theme; v=tuple(int(x) for x in m.version('sric-core').split('.')[:3]); raise SystemExit(0 if (0,5,16)<=v<(0,6,0) else 1)" || (echo FossilScope/SRIC runtime integrity check failed. Required fossilscope==0.5.15 and sric-core ^>=0.5.16,^<0.6.& goto :restore_runtime)
if not exist "%SCRIPT_DIR%fossilscope-wrapper.cmd" (echo Missing scripts\fossilscope-wrapper.cmd.& goto :restore_runtime)
copy /y "%SCRIPT_DIR%fossilscope-wrapper.cmd" "%BIN_DIR%\%CMD%.cmd" >nul || goto :restore_runtime
"%VENV%\Scripts\python.exe" -m sric.install_path "%BIN_DIR%" || goto :restore_runtime
set "SENTINEL_BANNER=never"
set "CHECK_LOG=%INSTALL_ROOT%\install-check.log"
>"%CHECK_LOG%" type nul
"%VENV%\Scripts\%CMD%.exe" version >>"%CHECK_LOG%" 2>&1 || goto :validation_failed
"%VENV%\Scripts\%CMD%.exe" doctor --json >>"%CHECK_LOG%" 2>&1 || goto :validation_failed
"%VENV%\Scripts\%CMD%.exe" capabilities >>"%CHECK_LOG%" 2>&1 || goto :validation_failed
"%VENV%\Scripts\%CMD%.exe" --help >>"%CHECK_LOG%" 2>&1 || goto :validation_failed
"%VENV%\Scripts\%CMD%.exe" -h >>"%CHECK_LOG%" 2>&1 || goto :validation_failed
"%VENV%\Scripts\%CMD%.exe" help >>"%CHECK_LOG%" 2>&1 || goto :validation_failed
del /q "%CHECK_LOG%" >nul 2>&1
del /q "%INSTALL_ROOT%\update-in-progress.json" >nul 2>&1
if exist "%VENV_ROLLBACK%" rmdir /s /q "%VENV_ROLLBACK%"
echo %PROJECT% installed/repaired successfully in standalone mode.
exit /b 0

:validation_failed
echo Installation validation failed.
type "%CHECK_LOG%"

:restore_runtime
rem Remove only the replacement runtime and restore the previous venv if one existed.
if exist "%VENV%" rmdir /s /q "%VENV%"
if exist "%VENV_ROLLBACK%" move /y "%VENV_ROLLBACK%" "%VENV%" >nul 2>&1
if exist "%VENV_ROLLBACK%" (
  echo Runtime rollback failed. User workspaces/configuration were not deleted.
) else (
  echo Runtime installation/repair failed; previous runtime restored when available.
)
exit /b 4
