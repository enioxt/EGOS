/**
 * Test script for OpenRouter MCP Server
 *
 * This script tests the OpenRouter MCP server by simulating a client connecting to the server
 * and sending tool call requests. It uses the MCP protocol to communicate with the server.
 */

const { spawn } = require('child_process');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// Path to the MCP server script
const serverPath = path.join(__dirname, 'openrouter_mcp_server.js');

// Start the MCP server as a child process
console.log('Starting OpenRouter MCP Server...');
const server = spawn('node', [serverPath], {
  env: {
    ...process.env,
    OPENROUTER_API_KEY: process.env.OPENROUTER_API_KEY || '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',
    DEBUG: 'mcp:*',
    MCP_LOG_LEVEL: 'debug',
    NODE_ENV: 'development'
  },
  stdio: ['pipe', 'pipe', 'pipe']
});

// Set up event handlers for the server process
server.stdout.on('data', (data) => {
  try {
    // Parse the JSON response from the server
    const messages = data.toString().trim().split('\n');

    for (const message of messages) {
      if (!message) continue;

      const response = JSON.parse(message);
      console.log('Received response:', JSON.stringify(response, null, 2));

      // Handle different response types
      if (response.type === 'server_info') {
        console.log('\nServer info received. Available tools:');
        response.server.tools.forEach(tool => {
          console.log(`- ${tool.name}: ${tool.description}`);
        });

        // Send a ping request
        sendPing();

        // Wait a bit and then send a tool call
        setTimeout(() => {
          sendToolCall('openrouter_status', {});
        }, 1000);

        // Wait a bit more and then send another tool call
        setTimeout(() => {
          sendToolCall('openrouter_chat', {
            prompt: 'Hello, can you tell me about the EVA & GUARANI project?'
          });
        }, 2000);
      } else if (response.type === 'tool_result') {
        console.log('\nTool result received:');
        console.log(`Tool ID: ${response.id}`);
        console.log(`Result: ${JSON.stringify(response.result, null, 2)}`);

        // If we've received the chat result, we're done
        if (response.result && response.result.content && response.result.content.includes('EVA & GUARANI')) {
          console.log('\nAll tests completed successfully!');

          // Send a shutdown request
          setTimeout(() => {
            sendShutdown();
          }, 1000);
        }
      } else if (response.type === 'shutdown_acknowledged') {
        console.log('\nServer shutdown acknowledged. Exiting...');

        // Exit after a short delay
        setTimeout(() => {
          process.exit(0);
        }, 500);
      }
    }
  } catch (error) {
    console.error('Error parsing server response:', error);
  }
});

server.stderr.on('data', (data) => {
  console.error('Server error:', data.toString());
});

server.on('close', (code) => {
  console.log(`Server process exited with code ${code}`);
  process.exit(code);
});

// Function to send a message to the server
function sendMessage(message) {
  const json = JSON.stringify(message);
  console.log('Sending message:', json);
  server.stdin.write(json + '\n');
}

// Function to send a ping request
function sendPing() {
  sendMessage({
    id: uuidv4(),
    type: 'ping'
  });
}

// Function to send a tool call request
function sendToolCall(tool, args) {
  sendMessage({
    id: uuidv4(),
    type: 'tool_call',
    tool,
    arguments: args
  });
}

// Function to send a shutdown request
function sendShutdown() {
  sendMessage({
    id: uuidv4(),
    type: 'shutdown'
  });
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('Received SIGINT signal. Shutting down...');
  sendShutdown();
});

process.on('SIGTERM', () => {
  console.log('Received SIGTERM signal. Shutting down...');
  sendShutdown();
});
