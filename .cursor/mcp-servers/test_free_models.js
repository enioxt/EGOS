/**
 * Test script for OpenRouter MCP free models functionality
 *
 * This script tests the free models functionality in the OpenRouter MCP server,
 * including model selection and the toggle free models tool.
 */

const OpenRouterClient = require('./openrouter_client');
const { v4: uuidv4 } = require('uuid');
const { spawn } = require('child_process');
const path = require('path');

// Path to the MCP server script
const serverPath = path.join(__dirname, 'openrouter_mcp_server.js');

// Test the OpenRouter client directly
async function testClient() {
  console.log('=== Testing OpenRouter Client Free Models ===');

  // Create a client with the API key
  const apiKey = process.env.OPENROUTER_API_KEY || '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';
  const client = new OpenRouterClient(apiKey);

  // 1. Check if free models are correctly defined
  console.log('\n1. Checking free models:');
  const freeModels = Object.entries(client.models)
    .filter(([_, model]) => model.isFree)
    .map(([id, model]) => ({
      id,
      name: model.name,
      provider: model.provider
    }));

  console.log('Free models:', freeModels);

  // 2. Test model selection with prioritizeFree = true
  console.log('\n2. Testing model selection with prioritizeFree = true:');
  client.prioritizeFree = true;

  const testCases = [
    { description: 'Code task (high complexity)', options: { isCode: true, complexity: 'high' } },
    { description: 'Code task (medium complexity)', options: { isCode: true, complexity: 'medium' } },
    { description: 'Large context task (>100k)', options: { contextLength: 150000 } },
    { description: 'Medium context task (>30k)', options: { contextLength: 50000 } },
    { description: 'General task (medium complexity)', options: { complexity: 'medium' } },
    { description: 'General task (low complexity)', options: { complexity: 'low' } }
  ];

  for (const testCase of testCases) {
    const model = client.selectModel(testCase.options);
    const modelInfo = client.models[model];
    console.log(`- ${testCase.description}: ${model} (${modelInfo.name}) - Free: ${modelInfo.isFree}`);
  }

  // 3. Test model selection with prioritizeFree = false
  console.log('\n3. Testing model selection with prioritizeFree = false:');
  client.prioritizeFree = false;

  for (const testCase of testCases) {
    const model = client.selectModel(testCase.options);
    const modelInfo = client.models[model];
    console.log(`- ${testCase.description}: ${model} (${modelInfo.name}) - Free: ${modelInfo.isFree}`);
  }

  console.log('\nClient tests completed successfully!');
}

// Test the MCP server
async function testServer() {
  console.log('\n=== Testing OpenRouter MCP Server Free Models ===');

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
          console.log('\nServer info received. Testing toggle free models tool...');

          // Send a ping request
          sendPing();

          // Wait a bit and then test the toggle free models tool
          setTimeout(() => {
            console.log('\nTesting toggle free models tool (prioritize_free = true):');
            sendToolCall('openrouter_toggle_free_models', {
              prioritize_free: true
            });
          }, 1000);

          // Wait a bit more and then test the status tool
          setTimeout(() => {
            console.log('\nTesting status tool:');
            sendToolCall('openrouter_status', {});
          }, 2000);

          // Wait a bit more and then test the toggle free models tool again
          setTimeout(() => {
            console.log('\nTesting toggle free models tool (prioritize_free = false):');
            sendToolCall('openrouter_toggle_free_models', {
              prioritize_free: false
            });
          }, 3000);

          // Wait a bit more and then test the status tool again
          setTimeout(() => {
            console.log('\nTesting status tool again:');
            sendToolCall('openrouter_status', {});
          }, 4000);

          // Wait a bit more and then send a shutdown request
          setTimeout(() => {
            console.log('\nSending shutdown request:');
            sendShutdown();
          }, 5000);
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
    console.log('\nServer tests completed!');
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
}

// Run the tests
async function runTests() {
  try {
    // Test the client first
    await testClient();

    // Then test the server
    await testServer();
  } catch (error) {
    console.error('Error running tests:', error);
    process.exit(1);
  }
}

// Run the tests
runTests();
