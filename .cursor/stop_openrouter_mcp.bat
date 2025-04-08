@echo off
echo Stopping OpenRouter MCP Server...

:: Set the port
set MCP_PORT=38001

:: Check if the server is running
netstat -an | findstr ":%MCP_PORT% " > nul
if %errorlevel% neq 0 (
    echo OpenRouter MCP Server is not running.
    goto :end
)

:: Find the process ID of the server
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%MCP_PORT% "') do (
    set PID=%%a
    goto :kill
)

:kill
:: Kill the process
echo Stopping process with PID %PID%...
taskkill /F /PID %PID%

:: Check if the process was killed
timeout /t 1 > nul
netstat -an | findstr ":%MCP_PORT% " > nul
if %errorlevel% equ 0 (
    echo Failed to stop OpenRouter MCP Server.
    echo Please close it manually.
) else (
    echo OpenRouter MCP Server stopped successfully.
)

:end
echo.
echo Press any key to exit.
pause > nul
