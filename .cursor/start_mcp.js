const net = require('net');
const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

// Configuração do servidor MCP
const MCP_CONFIG = {
    host: "localhost",
    port: 38002,
    timeout: 1000
};

// Função para verificar se o servidor está rodando
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

// Função para iniciar o servidor MCP
function startMCPServer() {
    const projectRoot = path.resolve(__dirname, '..');
    const pythonPath = path.join(projectRoot, 'venv', 'Scripts', 'python.exe');
    const scriptPath = path.join(projectRoot, 'tools', 'integration', 'mcp_server.py');

    const server = spawn(pythonPath, ['-m', 'tools.integration.mcp_server'], {
        cwd: projectRoot,
        stdio: 'pipe',
        shell: true
    });

    server.stdout.on('data', (data) => {
        console.log(`MCP Server: ${data}`);
    });

    server.stderr.on('data', (data) => {
        console.error(`MCP Server Error: ${data}`);
    });

    server.on('close', (code) => {
        console.log(`MCP Server exited with code ${code}`);
    });

    return server;
}

// Função principal
async function main() {
    try {
        // Verifica se o servidor já está rodando
        const isRunning = await checkServerRunning();

        if (isRunning) {
            console.log("MCP Server já está rodando");
            process.exit(0);
        }

        // Se não estiver rodando, inicia o servidor
        console.log("Iniciando MCP Server...");
        const server = startMCPServer();

        // Aguarda um pouco para verificar se o servidor iniciou corretamente
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Verifica se o servidor está rodando agora
        const isNowRunning = await checkServerRunning();

        if (!isNowRunning) {
            console.error("Falha ao iniciar MCP Server");
            server.kill();
            process.exit(1);
        }

        console.log("MCP Server iniciado com sucesso");
        process.exit(0);

    } catch (error) {
        console.error("Erro ao iniciar/verificar servidor MCP:", error);
        process.exit(1);
    }
}

// Executa o script
main();
