@echo off
chcp 65001 > nul
echo [EVA ^& GUARANI] - Initializing MCP Server

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

REM Install required packages if needed
pip install -q websockets python-dotenv aiohttp

REM Start the MCP server with proper path handling
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM Run the server in the foreground to see logs
python -m tools.integration.mcp_server

REM Keep the window open if there's an error
if errorlevel 1 (
    echo.
    echo Error starting MCP server. Press any key to exit...
    pause > nul
)

echo MCP server initialized and running in background.
echo You can now restart Cursor to use the MCP features.
