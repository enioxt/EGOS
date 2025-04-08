// MCP Connection Helper
// Este script força o Cursor a se conectar ao MCP externo já em execução

const fs = require('fs');
const path = require('path');
const os = require('os');

// Configurações para conexão externa
const externalConfig = {
    useExisting: true,
    port: 38001,
    host: "localhost",
    forceConnection: true,
    retryIntervalMs: 2000,
    maxRetries: 10
};

// Função principal
async function configureMCPConnection() {
    try {
        console.log('[EVA & GUARANI] Configurando conexão MCP externa...');

        // Verifica se o servidor está rodando
        const serverRunning = await checkServerRunning(externalConfig.host, externalConfig.port);
        if (!serverRunning) {
            console.error('[EVA & GUARANI] Servidor MCP não detectado na porta especificada.');
            console.log('[EVA & GUARANI] Certifique-se que o servidor MCP está rodando antes de iniciar o Cursor.');
            return;
        }

        console.log('[EVA & GUARANI] Servidor MCP detectado! Configurando Cursor para conexão externa...');

        // Atualiza as configurações do Cursor
        updateCursorSettings();

        console.log('[EVA & GUARANI] Configuração concluída! MCP externo conectado.');
    } catch (error) {
        console.error('[EVA & GUARANI] Erro ao configurar MCP:', error);
    }
}

// Função para verificar se o servidor está rodando
async function checkServerRunning(host, port) {
    return new Promise((resolve) => {
        const net = require('net');
        const socket = new net.Socket();

        socket.setTimeout(1000);

        socket.on('connect', () => {
            socket.destroy();
            resolve(true);
        });

        socket.on('timeout', () => {
            socket.destroy();
            resolve(false);
        });

        socket.on('error', () => {
            socket.destroy();
            resolve(false);
        });

        socket.connect(port, host);
    });
}

// Função para atualizar configurações do Cursor
function updateCursorSettings() {
    // Diretório de configuração do Cursor
    const cursorConfigDir = path.join(os.homedir(), 'AppData', 'Roaming', 'Cursor');

    // Verifica se o diretório existe
    if (!fs.existsSync(cursorConfigDir)) {
        fs.mkdirSync(cursorConfigDir, { recursive: true });
    }

    // Salva arquivo de configuração específico para MCP
    const mcpConfigPath = path.join(cursorConfigDir, 'mcp_config.json');
    fs.writeFileSync(mcpConfigPath, JSON.stringify(externalConfig, null, 2));

    console.log('[EVA & GUARANI] Arquivo de configuração salvo em:', mcpConfigPath);
}

// Executa a função principal
configureMCPConnection();
