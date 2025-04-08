@echo off
echo Testing OpenRouter MCP Server (Simple Test)...

:: Set environment variables
set OPENROUTER_API_KEY=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
set DEBUG=mcp:*
set LOG_LEVEL=warn
set LOG_FORMAT=json
set NODE_ENV=development
set VERBOSE_OUTPUT=false
set MCP_STDOUT_FILE=C:\Eva Guarani EGOS\logs\mcp\test_stdout.log

:: Create log directory if it doesn't exist
if not exist "C:\Eva Guarani EGOS\logs\mcp" mkdir "C:\Eva Guarani EGOS\logs\mcp"

:: Run a simple test
echo.
echo 1. Testing OpenRouter Status...
echo.
node -e "const { spawn } = require('child_process'); const server = spawn('node', ['%~dp0mcp-servers\\openrouter_mcp_server.js'], { env: process.env, stdio: ['pipe', 'pipe', 'pipe'] });

console.log('Starting test server...');

// Handle server output
server.stdout.on('data', data => {
  try {
    const messages = data.toString().trim().split('\n');
    for (const message of messages) {
      if (!message) continue;

      const response = JSON.parse(message);

      if (response.type === 'server_info') {
        console.log('Server started successfully. Testing status...');

        // Send status request
        const statusRequest = {
          id: 'test-status',
          type: 'tool_call',
          tool: 'openrouter_status',
          arguments: {}
        };
        server.stdin.write(JSON.stringify(statusRequest) + '\n');
      }
      else if (response.type === 'tool_result' && response.id === 'test-status') {
        // Process status result
        console.log('\nStatus result received:');
        console.log('- Available models: ' + response.result.availableModels.length);

        // Show free models
        const freeModels = response.result.availableModels.filter(model =>
          response.result.usageStats.modelUsage.some(usage =>
            usage.model === model.name && usage.isFree
          )
        );
        console.log('- Free models: ' + freeModels.length);
        freeModels.forEach(model => console.log('  * ' + model.name));

        console.log('- Prioritizing free models: ' + response.result.usageStats.prioritizingFree);
        console.log('- Total requests: ' + response.result.usageStats.totalRequests);

        console.log('\nTest completed successfully!');

        // Send shutdown request
        setTimeout(() => {
          console.log('Shutting down test server...');
          const shutdownRequest = {
            id: 'test-shutdown',
            type: 'shutdown'
          };
          server.stdin.write(JSON.stringify(shutdownRequest) + '\n');
        }, 500);
      }
      else if (response.type === 'shutdown_acknowledged') {
        console.log('Server shutdown acknowledged.');
        setTimeout(() => process.exit(0), 500);
      }
    }
  } catch (error) {
    console.error('Error parsing response:', error);
  }
});

// Handle server errors
server.stderr.on('data', data => {
  const errorMsg = data.toString().trim();
  if (errorMsg) {
    console.error('Server error:', errorMsg);
  }
});

// Handle server close
server.on('close', code => {
  if (code !== 0) {
    console.log(`Server exited with code ${code}`);
  }
  process.exit(code);
});"

echo.
echo Test completed. Press any key to exit.
pause > nul
