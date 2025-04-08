@echo off
chcp 65001 > nul
echo [EVA ^& GUARANI] - Starting MCP Service

REM Get the project root directory
set "PROJECT_ROOT=%~dp0.."

REM Run the Python script
python "%PROJECT_ROOT%\tools\integration\start_mcp.py"

REM Keep the window open if there's an error
if errorlevel 1 (
    echo.
    echo Error starting MCP service. Press any key to exit...
    pause > nul
)
