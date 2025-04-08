@echo off
echo Starting OpenRouter MCP Server in background...

:: Set environment variables
set OPENROUTER_API_KEY=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
set DEBUG=mcp:*
set LOG_LEVEL=warn
set LOG_FORMAT=json
set LOG_DIR=C:\Eva Guarani EGOS\logs
set NODE_ENV=development
set MCP_LOG_FILE=C:\Eva Guarani EGOS\logs\mcp\openrouter.log
set VERBOSE_OUTPUT=false
set MCP_STDOUT_FILE=C:\Eva Guarani EGOS\logs\mcp\openrouter_stdout.log
set MCP_PORT=38001

:: Create log directories if they don't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%LOG_DIR%\mcp" mkdir "%LOG_DIR%\mcp"

:: Make sure the log file directory exists
echo Creating log directories...
mkdir "%LOG_DIR%\mcp" 2>nul

:: Check if the server is already running
echo Checking if server is already running...
netstat -an | findstr ":%MCP_PORT% " > nul
if %errorlevel% equ 0 (
    echo OpenRouter MCP Server is already running on port %MCP_PORT%.
    echo To restart, please stop the server first.
    goto :end
)

:: Start the MCP server in the background
echo OpenRouter MCP Server starting in background...
start /b cmd /c "node "%~dp0mcp-servers\openrouter_mcp_server.js" > "%MCP_STDOUT_FILE%" 2>&1"

:: Wait for the server to start
echo Waiting for server to start...
timeout /t 2 > nul

:: Check if the server started successfully
netstat -an | findstr ":%MCP_PORT% " > nul
if %errorlevel% equ 0 (
    echo OpenRouter MCP Server started successfully!
    echo The server is now running on port %MCP_PORT%.
    echo MCP protocol output is being redirected to %MCP_STDOUT_FILE%
    echo.
    echo To stop the server, run:
    echo .cursor/stop_openrouter_mcp.bat
) else (
    echo Failed to start OpenRouter MCP Server.
    echo Please check the log file: %MCP_STDOUT_FILE%
    echo.
    echo Try running the server in foreground mode for debugging:
    echo .cursor/start_openrouter_mcp.bat
)

:end
