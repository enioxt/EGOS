@echo off
echo Testing OpenRouter Client...

:: Set environment variables
set OPENROUTER_API_KEY=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
set DEBUG=mcp:*
set LOG_LEVEL=debug
set NODE_ENV=development

:: Run the test script
node "%~dp0mcp-servers\test_openrouter_client.js"

echo.
echo Test completed. Press any key to exit.
pause > nul
