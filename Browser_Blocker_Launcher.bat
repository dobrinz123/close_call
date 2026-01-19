@echo off
REM Browser Blocker Launcher - Auto-request Administrator privileges
REM Double-click this file to launch Browser Blocker with GUI

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run_program
) else (
    goto :request_admin
)

:request_admin
echo Requesting Administrator privileges...
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:run_program
cd /d "%~dp0"
pythonw browser_blocker.py
if errorlevel 1 (
    echo.
    echo Error: Could not launch Browser Blocker
    echo Make sure Python is installed and in PATH
    echo.
    pause
)
exit
