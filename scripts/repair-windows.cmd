@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
echo FossilScope Windows runtime repair
echo User workspaces, configuration, evidence and reports are preserved.
call "%SCRIPT_DIR%install-windows.cmd"
exit /b %ERRORLEVEL%
