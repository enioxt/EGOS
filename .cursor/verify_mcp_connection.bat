@echo off
echo ===== EVA & GUARANI MCP CONNECTION VERIFICATION =====
echo Verificando conexão com o servidor MCP...

node .cursor/check_mcp_connection.js

echo.
echo Pressione qualquer tecla para continuar...
pause > nul
