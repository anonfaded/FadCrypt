@echo off
REM FadCrypt Context Menu Unlock Handler
REM Wraps the password-protected unlock operation
REM Runs Python silently without showing console window

setlocal enabledelayedexpansion

REM Get the FadCrypt script directory (batch file location)
set SCRIPT_DIR=%~dp0

REM Get the file path from context menu argument
set FILE_PATH=%1

REM Run Python silently using a PowerShell wrapper
REM This ensures no console window is visible
powershell.exe -NoProfile -WindowStyle Hidden -Command "& python '%SCRIPT_DIR%FadCrypt.py' --unlock '%FILE_PATH%'"

REM Exit silently
exit /b 0
