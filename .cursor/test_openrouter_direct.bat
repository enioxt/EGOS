@echo off
echo Testing OpenRouter MCP Server (Direct Test)...

:: Set environment variables
<<<<<<< HEAD
<<<<<<< HEAD
set OPENROUTER_API_KEY=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
=======
:: IMPORTANT: Set OPENROUTER_API_KEY in your environment variables separately.
::            Do not hardcode secrets in version control.
:: set OPENROUTER_API_KEY=YOUR_API_KEY_HERE
>>>>>>> e5f819512f57e668911b611effc183308fcb8c65
=======
:: IMPORTANT: Set OPENROUTER_API_KEY in your environment variables separately.
::            Do not hardcode secrets in version control.
:: set OPENROUTER_API_KEY=YOUR_API_KEY_HERE
>>>>>>> NewIntegrations
set DEBUG=mcp:*
set LOG_LEVEL=warn
set LOG_FORMAT=json
set NODE_ENV=development
set VERBOSE_OUTPUT=false

:: Run the direct test
echo.
echo Running direct test against OpenRouter MCP server...
echo.
node "%~dp0test_openrouter_direct.js"

echo.
echo Test completed. Press any key to exit.
<<<<<<< HEAD
<<<<<<< HEAD
pause > nul
=======
pause > nul
>>>>>>> e5f819512f57e668911b611effc183308fcb8c65
=======
pause > nul
>>>>>>> NewIntegrations
