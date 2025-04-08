@echo off
echo ===== EVA & GUARANI MCP CONNECTION =====
echo Configurando conexão do Cursor com o MCP externo...

set APPDATA_CURSOR=%APPDATA%\Cursor
if not exist "%APPDATA_CURSOR%" mkdir "%APPDATA_CURSOR%"

echo {^
  "useExisting": true,^
  "port": 38001,^
  "host": "localhost",^
  "forceConnection": true,^
  "retryIntervalMs": 2000,^
  "maxRetries": 10^
} > "%APPDATA_CURSOR%\mcp_config.json"

echo Configuração MCP salva em %APPDATA_CURSOR%\mcp_config.json

echo.
echo ===== INSTRUÇÕES =====
echo 1. Certifique-se que o servidor MCP está rodando
echo 2. Reinicie o Cursor IDE
echo 3. Vá em Settings -^> MCP -^> desative e reative o servidor "eva-guarani-perplexity"
echo.
echo Pressione qualquer tecla para continuar...
pause > nul
