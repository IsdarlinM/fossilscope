@echo off
setlocal EnableExtensions
set "INSTALL_ROOT=%USERPROFILE%\.fossilscope"
set "UPDATE_LOCK=%INSTALL_ROOT%\update-in-progress.json"
if exist "%UPDATE_LOCK%" (
  echo FossilScope update is finishing. Waiting for the verified handoff...
  for /L %%N in (1,1,300) do (
    if not exist "%UPDATE_LOCK%" goto :run
    >nul 2>&1 ping 127.0.0.1 -n 2
  )
  echo FossilScope update did not finish within 5 minutes.
  echo Review "%INSTALL_ROOT%\update-handoff.log" and "%INSTALL_ROOT%\update-result.json".
  exit /b 6
)
:run
@"%INSTALL_ROOT%\venv\Scripts\fossilscope.exe" %*
