/**
 * Direct test for OpenRouter MCP server
 *
 * This script directly connects to the OpenRouter MCP server
 * and tests its functionality.
 */

const net = require('net');
const { v4: uuidv4 } = require('uuid');

// MCP server configuration
const MCP_CONFIG = {
  host: 'localhost',
  port: 38001
};

// Connect to the MCP server
const socket = new net.Socket();

// Set up error handling
socket.on('error', (error) => {
  console.error(`Error connecting to MCP server: ${error.message}`);
  process.exit(1);
});

// Connect to the server
socket.connect(MCP_CONFIG.port, MCP_CONFIG.host, () => {
  console.log(`Connected to MCP server at ${MCP_CONFIG.host}:${MCP_CONFIG.port}`);

  // Set up message handling
  let messageBuffer = '';
  socket.on('data', (data) => {
    messageBuffer += data.toString();

    // Process complete messages
    let newlineIndex;
    while ((newlineIndex = messageBuffer.indexOf('\n')) !== -1) {
      const message = messageBuffer.substring(0, newlineIndex);
      messageBuffer = messageBuffer.substring(newlineIndex + 1);

      try {
        const response = JSON.parse(message);
        console.log('Received message:', JSON.stringify(response, null, 2));

        // Handle server_info message
        if (response.type === 'server_info') {
          console.log('\nServer info received');
          console.log(`Server name: ${response.server.name}`);
          console.log(`Server version: ${response.server.version}`);
          console.log(`Server description: ${response.server.description}`);
          console.log(`Available tools: ${response.server.tools.length}`);

          // Send a status request
          console.log('\nSending status request...');
          sendRequest({
            id: uuidv4(),
            type: 'tool_call',
            tool: 'openrouter_status',
            arguments: {}
          });
        }
        // Handle tool_result message
        else if (response.type === 'tool_result') {
          console.log('\nTool result received');

          if (response.result.availableModels) {
            console.log('\nAvailable models:');
            response.result.availableModels.forEach(model => {
              console.log(`- ${model.name} (${model.id})`);
            });

            console.log('\nUsage statistics:');
            console.log(`- Total requests: ${response.result.usageStats.totalRequests}`);
            console.log(`- Total cost: ${response.result.usageStats.totalCost}`);
            console.log(`- Prioritizing free models: ${response.result.usageStats.prioritizingFree}`);

            // Send a toggle free models request
            console.log('\nSending toggle free models request...');
            sendRequest({
              id: uuidv4(),
              type: 'tool_call',
              tool: 'openrouter_toggle_free_models',
              arguments: {
                prioritize_free: true
              }
            });
          }
          else if (response.result.prioritizeFree !== undefined) {
            console.log('\nToggle free models result:');
            console.log(`- Free models prioritized: ${response.result.prioritizeFree}`);
            console.log(`- Free models available: ${response.result.freeModels.length}`);

            // Send a chat request
            console.log('\nSending chat request...');
            sendRequest({
              id: uuidv4(),
              type: 'tool_call',
              tool: 'openrouter_chat',
              arguments: {
                prompt: 'What are the benefits of using free AI models?',
                options: {
                  maxTokens: 100,
                  temperature: 0.7,
                  prioritizeFree: true
                }
              }
            });
          }
          else if (response.result.content) {
            console.log('\nChat result:');
            console.log(`- Model used: ${response.result.model}`);
            console.log(`- Content: ${response.result.content}`);

            // Send a shutdown request
            console.log('\nSending shutdown request...');
            sendRequest({
              id: uuidv4(),
              type: 'shutdown'
            });
          }
        }
        // Handle shutdown_acknowledged message
        else if (response.type === 'shutdown_acknowledged') {
          console.log('\nShutdown acknowledged');
          console.log('Closing connection...');
          socket.end();
          process.exit(0);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    }
  });

  // Function to send a request to the server
  function sendRequest(request) {
    const json = JSON.stringify(request);
    console.log('Sending request:', json);
    socket.write(json + '\n');
  }
});

// Handle socket close
socket.on('close', () => {
  console.log('Connection closed');
  process.exit(0);
});
