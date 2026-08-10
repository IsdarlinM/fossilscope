@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
set "RUNTIME_PY=%USERPROFILE%\.fossilscope\venv\Scripts\python.exe"
set "TEST_HOME=%TEMP%\fossilscope-update-handoff-smoke"
set "RESULT=%TEST_HOME%\.fossilscope\update-result.json"
set "LOCK=%TEST_HOME%\.fossilscope\update-in-progress.json"
set "LOG=%TEST_HOME%\.fossilscope\update-handoff.log"

if not exist "%RUNTIME_PY%" (
  echo FossilScope isolated runtime not found at "%RUNTIME_PY%".
  echo Install or repair the 0.5.16 candidate first.
  exit /b 2
)

if exist "%TEST_HOME%" rmdir /s /q "%TEST_HOME%"
mkdir "%TEST_HOME%" || exit /b 2
set "FOSSILSCOPE_UPDATE_TEST_HOME=%TEST_HOME%"

echo [FossilScope] Windows post-exit handoff smoke.
echo Keep this single CMD window open. No additional console window should appear.
echo.
"%RUNTIME_PY%" "%SCRIPT_DIR%windows-update-handoff-smoke.py"
if errorlevel 1 exit /b %errorlevel%

for /L %%N in (1,1,120) do (
  if exist "%RESULT%" goto :result
  >nul 2>&1 timeout /t 1 /nobreak
)

echo Timed out waiting for the hidden update helper.
if exist "%LOG%" type "%LOG%"
exit /b 6

:result
echo.
echo [FossilScope] Post-exit result:
type "%RESULT%"
echo.
"%RUNTIME_PY%" -c "import json,pathlib,sys; p=pathlib.Path(sys.argv[1]); d=json.loads(p.read_text(encoding='utf-8')); assert d.get('status')=='INSTALLED', d; assert d.get('installed') is True, d; assert d.get('forced') is True, d; assert d.get('action')=='FORCED_REINSTALL', d" "%RESULT%"
if errorlevel 1 (
  echo Windows handoff smoke FAILED.
  if exist "%LOG%" type "%LOG%"
  exit /b 6
)
if exist "%LOCK%" (
  echo Windows handoff smoke FAILED: stale update lock remains.
  type "%LOCK%"
  exit /b 6
)

echo Windows handoff smoke PASS: one visible CLI, hidden helper result INSTALLED, forced action preserved, no stale lock.
exit /b 0
