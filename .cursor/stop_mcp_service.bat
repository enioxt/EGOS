@echo off
chcp 65001 > nul
echo [EVA ^& GUARANI] - Stopping MCP Service

REM Find and kill the Python MCP server process
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq tools.integration.mcp_server" /F > nul 2>&1

echo MCP service stopped.
echo.
echo To start the service again, run start_mcp_service.bat
