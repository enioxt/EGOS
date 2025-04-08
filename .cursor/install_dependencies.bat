@echo off
echo Installing dependencies for OpenRouter MCP...

:: Check if npm is installed
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: npm is not installed. Please install Node.js and npm first.
    exit /b 1
)

:: Install required dependencies
npm install axios uuid ws

echo.
echo Dependencies installed successfully.
echo You can now run the OpenRouter MCP server using:
echo .cursor/start_openrouter_mcp.bat
echo.
echo Press any key to exit.
pause > nul
