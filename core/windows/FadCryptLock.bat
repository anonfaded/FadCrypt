@echo off
REM FadCrypt Context Menu Lock Handler
REM Wraps the password-protected lock operation
REM Runs Python silently without showing console window
REM Supports both script execution (development) and packaged app execution (production)

setlocal enabledelayedexpansion

REM Get the FadCrypt installation directory (parent of core/windows)
set SCRIPT_DIR=%~dp0
for %%i in ("%SCRIPT_DIR%..\..") do set FADCRYPT_DIR=%%~fi

REM Get the file path from context menu argument
set FILE_PATH=%1

REM Get the full path to pythonw.exe (same directory as python.exe)
for /f "tokens=*" %%i in ('python -c "import sys; import os; print(os.path.join(os.path.dirname(sys.executable), \"pythonw.exe\"))" 2^>nul') do set PYTHONW_PATH=%%i

REM Check if running from packaged app (FadCrypt.exe exists in parent directory)
if exist "%FADCRYPT_DIR%\FadCrypt.exe" (
    REM Packaged app execution
    echo [CLI] Running packaged FadCrypt.exe --lock "%FILE_PATH%" >> "%TEMP%\fadcrypt_cli.log"
    powershell.exe -NoProfile -WindowStyle Hidden -Command "& '%FADCRYPT_DIR%\FadCrypt.exe' --lock '%FILE_PATH%'"
) else (
    REM Script execution (development) - use pythonw to avoid console window
    echo [CLI] Running script "%PYTHONW_PATH%" FadCrypt.py --lock "%FILE_PATH%" >> "%TEMP%\fadcrypt_cli.log"
    echo [CLI] Working directory: %FADCRYPT_DIR% >> "%TEMP%\fadcrypt_cli.log"
    cd /d "%FADCRYPT_DIR%"
    echo [CLI] Current directory: %CD% >> "%TEMP%\fadcrypt_cli.log"
    "%PYTHONW_PATH%" "%FADCRYPT_DIR%\FadCrypt.py" --lock "%FILE_PATH%" 2>> "%TEMP%\fadcrypt_cli_error.log"
    echo [CLI] Exit code: %ERRORLEVEL% >> "%TEMP%\fadcrypt_cli.log"
)

REM Exit silently
exit /b 0
