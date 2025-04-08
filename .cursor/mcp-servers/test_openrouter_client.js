/**
 * Test script for OpenRouter client
 *
 * This script tests the OpenRouter client by sending a simple request to the OpenRouter API.
 * Run this script to verify that the client is working correctly before using it with the MCP server.
 */

const OpenRouterClient = require('./openrouter_client');

// Create a client with the API key
const apiKey = process.env.OPENROUTER_API_KEY || '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';
const client = new OpenRouterClient(apiKey);

// Test function
async function testClient() {
  console.log('Testing OpenRouter client...');

  try {
    // Test chat completion
    console.log('\n1. Testing chat completion with automatic model selection:');
    const chatResult = await client.chatCompletion({
      prompt: 'Hello, can you tell me about the EVA & GUARANI project?',
      useCache: false
    });

    console.log(`Model used: ${chatResult.model}`);
    console.log(`Response: ${chatResult.content.substring(0, 150)}...`);
    console.log(`Tokens: ${JSON.stringify(chatResult.usage)}`);

    // Test code completion
    console.log('\n2. Testing code completion:');
    const codeResult = await client.codeCompletion({
      prompt: 'Write a function to calculate the Fibonacci sequence in JavaScript',
      language: 'JavaScript',
      useCache: false
    });

    console.log(`Model used: ${codeResult.model}`);
    console.log(`Response: ${codeResult.content.substring(0, 150)}...`);
    console.log(`Tokens: ${JSON.stringify(codeResult.usage)}`);

    // Test content analysis
    console.log('\n3. Testing content analysis:');
    const analysisResult = await client.analyzeContent({
      content: 'The EVA & GUARANI project is an integrated, ethical, AI-centric development ecosystem focused on seamless human-AI collaboration.',
      analysisType: 'summarize',
      useCache: false
    });

    console.log(`Model used: ${analysisResult.model}`);
    console.log(`Response: ${analysisResult.content.substring(0, 150)}...`);
    console.log(`Tokens: ${JSON.stringify(analysisResult.usage)}`);

    // Test status
    console.log('\n4. Testing status:');
    const status = await client.getStatus();
    console.log(`Available models: ${status.availableModels.length}`);
    console.log(`Usage stats: ${JSON.stringify(status.usageStats)}`);

    console.log('\nAll tests completed successfully!');
  } catch (error) {
    console.error('Error testing OpenRouter client:', error);
  }
}

// Run the test
testClient();
