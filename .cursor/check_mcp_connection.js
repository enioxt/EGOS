const WebSocket = require('ws');

// MCP Configuration
const MCP_CONFIG = {
    host: 'localhost',
    port: 38001,
    timeout: 5000
};

// Function to check if server is running
async function checkServerRunning() {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(`ws://${MCP_CONFIG.host}:${MCP_CONFIG.port}`);

        ws.on('open', () => {
            console.log('✅ Conexão WebSocket estabelecida');
            ws.close();
            resolve(true);
        });

        ws.on('error', (error) => {
            console.error('❌ Erro na conexão WebSocket:', error.message);
            reject(error);
        });

        // Set timeout
        setTimeout(() => {
            ws.close();
            reject(new Error('Timeout ao conectar'));
        }, MCP_CONFIG.timeout);
    });
}

// Main function
async function main() {
    console.log('===================================');
    console.log('Verificando conexão com MCP...');
    console.log('===================================');

    try {
        await checkServerRunning();
        console.log('✅ Servidor MCP detectado e respondendo');
        console.log(`📡 Host: ${MCP_CONFIG.host}`);
        console.log(`🔌 Porta: ${MCP_CONFIG.port}`);
        console.log('\n');
    } catch (error) {
        console.error('❌ Erro ao conectar com o servidor MCP:', error.message);
        console.log('\nSugestões de solução:');
        console.log('1. Verifique se o servidor MCP está em execução');
        console.log('2. Verifique se a porta 38001 está disponível');
        console.log('3. Verifique se há bloqueio de firewall');
        console.log('4. Tente reiniciar o servidor MCP');
        process.exit(1);
    }
}

main();
