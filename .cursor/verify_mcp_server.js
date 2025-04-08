const net = require('net');
const fs = require('fs');
const path = require('path');
const os = require('os');
const WebSocket = require('ws');

// Configuração do servidor MCP
const MCP_CONFIG = {
    host: "localhost",
    port: 38002,
    statusPort: 38003,
    timeout: 1000,
    maxRetries: 3,
    retryDelay: 1000
};

// Função para verificar se a porta está em uso
function checkPortInUse(port) {
    return new Promise((resolve) => {
        const server = net.createServer()
            .once('error', () => {
                resolve(true);
            })
            .once('listening', () => {
                server.close();
                resolve(false);
            })
            .listen(port);
    });
}

// Função para verificar se o servidor está rodando via TCP
function checkServerRunning() {
    return new Promise((resolve) => {
        const socket = new net.Socket();
        const onError = () => {
            socket.destroy();
            resolve(false);
        };

        socket.setTimeout(MCP_CONFIG.timeout);
        socket.once('error', onError);
        socket.once('timeout', onError);

        socket.connect(MCP_CONFIG.port, MCP_CONFIG.host, () => {
            socket.end();
            resolve(true);
        });
    });
}

// Função para verificar se o servidor está respondendo via WebSocket
function checkWebSocketConnection() {
    return new Promise((resolve) => {
        const ws = new WebSocket(`ws://${MCP_CONFIG.host}:${MCP_CONFIG.port}`);

        const timer = setTimeout(() => {
            ws.terminate();
            resolve(false);
        }, MCP_CONFIG.timeout);

        ws.on('open', () => {
            clearTimeout(timer);
            ws.close();
            resolve(true);
        });

        ws.on('error', () => {
            clearTimeout(timer);
            resolve(false);
        });
    });
}

// Função para verificar o status HTTP
async function checkStatusEndpoint() {
    try {
        const response = await fetch(`http://${MCP_CONFIG.host}:${MCP_CONFIG.statusPort}/status`);
        if (response.ok) {
            const data = await response.json();
            return data.status === 'running';
        }
        return false;
    } catch (error) {
        return false;
    }
}

// Função para tentar múltiplas vezes
async function retryOperation(operation, maxRetries = MCP_CONFIG.maxRetries) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const result = await operation();
            if (result) return true;
        } catch (error) {
            console.error(`Tentativa ${i + 1} falhou:`, error.message);
        }
        if (i < maxRetries - 1) {
            await new Promise(resolve => setTimeout(resolve, MCP_CONFIG.retryDelay));
        }
    }
    return false;
}

// Função principal
async function main() {
    try {
        console.log("===================================");
        console.log("Verificando conexão com MCP...");

        // Verifica se as portas estão em uso
        const [portInUse, statusPortInUse] = await Promise.all([
            checkPortInUse(MCP_CONFIG.port),
            checkPortInUse(MCP_CONFIG.statusPort)
        ]);

        if (!portInUse && !statusPortInUse) {
            console.error("\n❌ ERRO: Nenhum servidor MCP detectado nas portas esperadas");
            process.exit(1);
        }

        // Verifica conexão TCP
        const serverRunning = await retryOperation(checkServerRunning);
        if (!serverRunning) {
            console.error("\n❌ ERRO: Servidor MCP não está aceitando conexões TCP");
            process.exit(1);
        }

        // Verifica conexão WebSocket
        const wsConnected = await retryOperation(checkWebSocketConnection);
        if (!wsConnected) {
            console.error("\n❌ ERRO: Servidor MCP não está aceitando conexões WebSocket");
            process.exit(1);
        }

        // Verifica endpoint de status
        const statusOk = await retryOperation(checkStatusEndpoint);
        if (!statusOk) {
            console.error("\n⚠️ AVISO: Endpoint de status não está respondendo, mas servidor está funcionando");
        }

        console.log("\n✅ Servidor MCP está rodando e respondendo corretamente");
        console.log("\nPara usar o servidor MCP no Cursor:");
        console.log("1. Vá para Configurações → MCP");
        console.log("2. Desative o servidor 'eva-guarani-perplexity'");
        console.log("3. Clique em Refresh");
        console.log("4. Reative o servidor");
        console.log("5. Clique em Refresh novamente");
        console.log("===================================");

        process.exit(0);
    } catch (error) {
        console.error("\n❌ ERRO:", error.message);
        process.exit(1);
    }
}

// Executa a verificação
main();
