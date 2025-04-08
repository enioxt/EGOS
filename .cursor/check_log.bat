@echo off
echo Checking OpenRouter MCP log file...
echo.

:: Set the log file path
set LOG_FILE=C:\Eva Guarani EGOS\logs\mcp\openrouter_stdout.log

:: Check if the log file exists
if not exist "%LOG_FILE%" (
    echo Log file does not exist: %LOG_FILE%
    goto :end
)

:: Display the log file contents
echo Log file contents:
echo ==================
type "%LOG_FILE%"
echo ==================

:end
echo.
echo Press any key to exit.
pause > nul
