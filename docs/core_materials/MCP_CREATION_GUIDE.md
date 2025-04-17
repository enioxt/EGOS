# Creating Custom MCP Servers

This guide explains how to create custom Model Context Protocol (MCP) servers for the EGOS project. MCP servers allow you to extend the capabilities of Cursor/Roocode by providing additional tools and resources.

## Table of Contents

1. [Understanding MCP](#understanding-mcp)
2. [MCP Server Architecture](#mcp-server-architecture)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Testing Your MCP Server](#testing-your-mcp-server)
5. [Integrating with Cursor/Roocode](#integrating-with-cursorroocode)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

## Understanding MCP

The Model Context Protocol (MCP) is a protocol for communication between Cursor/Roocode and external servers that provide additional tools and resources. MCP servers can provide various capabilities, such as:

- Access to external APIs
- Custom tools for specific tasks
- Data processing and analysis
- Integration with other systems

MCP servers communicate with Cursor/Roocode using a simple JSON-based protocol over standard input/output (stdio) or WebSockets.

## MCP Server Architecture

A typical MCP server consists of the following components:

1. **Server Core**: Handles communication with Cursor/Roocode
2. **Tool Handlers**: Implement the functionality of the tools provided by the server
3. **External API Clients**: Communicate with external APIs or services
4. **Configuration**: Define server settings and tool parameters

### Communication Protocol

MCP servers communicate with Cursor/Roocode using JSON messages. The main message types are:

- `server_info`: Sent by the server to provide information about itself and its tools
- `ping`/`pong`: Used for heartbeat checks
- `tool_call`: Sent by Cursor/Roocode to call a tool
- `tool_result`: Sent by the server to return the result of a tool call
- `tool_error`: Sent by the server to report an error in a tool call
- `shutdown`: Sent by Cursor/Roocode to request server shutdown

### Tool Definition

Each tool provided by an MCP server is defined by:

- `name`: The name of the tool
- `description`: A description of what the tool does
- `parameters`: The parameters accepted by the tool, defined using JSON Schema

## Step-by-Step Guide

### 1. Set Up Your Project

Create a new directory for your MCP server and initialize it:

```bash
mkdir my-mcp-server
cd my-mcp-server
npm init -y
```

Install the necessary dependencies:

```bash
npm install uuid
```

### 2. Create the Server Core

Create a file named `server.js` with the following content:

```javascript
const readline = require('readline');
const { v4: uuidv4 } = require('uuid');

class MCPServer {
  constructor() {
    // Initialize properties
    this.running = false;
    this.requestMap = new Map();

    // Set up stdin/stdout for MCP communication
    this.stdin = process.stdin;
    this.stdout = process.stdout;
    this.rl = readline.createInterface({
      input: this.stdin,
      output: this.stdout,
      terminal: false
    });

    // Define MCP tools
    this.tools = {
      // Define your tools here
    };

    // Bind methods
    this.handleMessage = this.handleMessage.bind(this);
    this.sendResponse = this.sendResponse.bind(this);
    this.sendError = this.sendError.bind(this);
  }

  // Start the MCP server
  start() {
    console.error('Starting MCP Server');

    // Set up message handling
    this.running = true;
    this.rl.on('line', this.handleMessage);

    // Send server info
    this.sendServerInfo();

    console.error('MCP Server started');
  }

  // Stop the MCP server
  stop() {
    console.error('Stopping MCP Server');
    this.running = false;
    this.rl.close();
    process.exit(0);
  }

  // Send server info to the client
  sendServerInfo() {
    const serverInfo = {
      type: 'server_info',
      server: {
        name: 'My MCP Server',
        version: '1.0.0',
        description: 'Custom MCP Server',
        tools: Object.values(this.tools).map(tool => ({
          name: tool.name,
          description: tool.description,
          parameters: tool.parameters
        }))
      }
    };

    this.sendMessage(serverInfo);
  }

  // Handle an incoming message
  handleMessage(line) {
    try {
      // Parse the message
      const message = JSON.parse(line);
      console.error('Received message:', message);

      // Handle different message types
      switch (message.type) {
        case 'ping':
          this.handlePing(message);
          break;
        case 'shutdown':
          this.handleShutdown(message);
          break;
        case 'tool_call':
          this.handleToolCall(message);
          break;
        default:
          console.error(`Unknown message type: ${message.type}`);
          this.sendError(message.id, 'unknown_message_type', `Unknown message type: ${message.type}`);
      }
    } catch (error) {
      console.error('Error handling message:', error);
      try {
        // Try to send an error response if possible
        const message = JSON.parse(line);
        this.sendError(message.id, 'invalid_message', `Invalid message: ${error.message}`);
      } catch (e) {
        // If we can't parse the message, send a generic error
        this.sendError(uuidv4(), 'invalid_json', `Invalid JSON: ${error.message}`);
      }
    }
  }

  // Handle a ping message
  handlePing(message) {
    this.sendMessage({
      id: message.id,
      type: 'pong'
    });
  }

  // Handle a shutdown message
  handleShutdown(message) {
    console.error('Received shutdown request');
    this.sendMessage({
      id: message.id,
      type: 'shutdown_acknowledged'
    });

    // Stop the server after a short delay
    setTimeout(() => this.stop(), 100);
  }

  // Handle a tool call message
  handleToolCall(message) {
    const { id, tool, arguments: args } = message;

    // Check if the tool exists
    if (!this.tools[tool]) {
      return this.sendError(id, 'unknown_tool', `Unknown tool: ${tool}`);
    }

    // Get the tool handler
    const toolHandler = this.tools[tool].handler;

    // Call the tool handler
    try {
      // Store the request ID for async handling
      this.requestMap.set(id, message);

      // Call the handler
      toolHandler(id, args);
    } catch (error) {
      console.error(`Error calling tool ${tool}:`, error);
      this.sendError(id, 'tool_execution_error', `Error executing tool ${tool}: ${error.message}`);
    }
  }

  // Send a message to the client
  sendMessage(message) {
    const json = JSON.stringify(message);
    this.stdout.write(json + '\n');
    console.error('Sent message:', message);
  }

  // Send a response to the client
  sendResponse(id, result) {
    this.sendMessage({
      id,
      type: 'tool_result',
      result
    });
  }

  // Send an error to the client
  sendError(id, code, message) {
    this.sendMessage({
      id,
      type: 'tool_error',
      error: {
        code,
        message
      }
    });
  }
}

// Create and start the server
const server = new MCPServer();
server.start();

// Handle process signals
process.on('SIGINT', () => {
  console.error('Received SIGINT signal');
  server.stop();
});

process.on('SIGTERM', () => {
  console.error('Received SIGTERM signal');
  server.stop();
});
```

### 3. Define Your Tools

Add your tools to the `tools` object in the `MCPServer` constructor:

```javascript
this.tools = {
  'hello_world': {
    name: 'hello_world',
    description: 'A simple hello world tool',
    parameters: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Your name'
        }
      },
      required: ['name']
    },
    handler: this.handleHelloWorld.bind(this)
  }
};
```

Then implement the handler method:

```javascript
// Handle a hello world request
handleHelloWorld(id, args) {
  const { name } = args;

  // Validate required parameters
  if (!name) {
    return this.sendError(id, 'missing_parameter', 'Missing required parameter: name');
  }

  // Send the response
  this.sendResponse(id, {
    message: `Hello, ${name}!`
  });
}
```

### 4. Create External API Clients

If your MCP server needs to communicate with external APIs, create client classes for them:

```javascript
class ExternalAPIClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.example.com';
  }

  async getData(params) {
    // Implement API call logic here
    return { data: 'example data' };
  }
}
```

Then use the client in your tool handlers:

```javascript
// Initialize the client
this.apiClient = new ExternalAPIClient(process.env.API_KEY);

// Handle an API request
handleAPIRequest(id, args) {
  const { params } = args;

  // Call the API
  this.apiClient.getData(params)
    .then(result => {
      this.sendResponse(id, result);
    })
    .catch(error => {
      this.sendError(id, 'api_error', `API error: ${error.message}`);
    });
}
```

### 5. Create Configuration Files

Create configuration files for your MCP server:

#### `mcp-config.json`

```json
{
  "name": "My MCP Server",
  "version": "1.0.0",
  "description": "Custom MCP Server",
  "env": {
    "API_KEY": "your-api-key"
  }
}
```

## Testing Your MCP Server

### 1. Create a Test Script

Create a file named `test.js` with the following content:

```javascript
const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');

// Start the MCP server as a child process
console.log('Starting MCP Server...');
const server = spawn('node', ['server.js'], {
  env: {
    ...process.env,
    API_KEY: 'your-api-key'
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
      console.log('Received response:', response);

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
          sendToolCall('hello_world', {
            name: 'World'
          });
        }, 1000);
      } else if (response.type === 'tool_result') {
        console.log('\nTool result received:');
        console.log(`Tool ID: ${response.id}`);
        console.log(`Result: ${JSON.stringify(response.result)}`);

        // Send a shutdown request
        setTimeout(() => {
          sendShutdown();
        }, 1000);
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
```

### 2. Run the Test

```bash
node test.js
```

## Integrating with Cursor/Roocode

### 1. Create Configuration Files

Create the following configuration files:

#### `.cursor/mcp/your-server.json`

```json
{
  "mcpServers": {
    "your-server": {
      "command": "node",
      "args": [
        "C:/path/to/your/server.js"
      ],
      "type": "stdio",
      "env": {
        "DEBUG": "*",
        "NODE_ENV": "development",
        "API_KEY": "your-api-key"
      },
      "windowsHide": true
    }
  }
}
```

#### `.cursor/mcp-servers/your-server.json`

```json
{
  "name": "Your Server Name",
  "command": "node",
  "args": [
    "C:/path/to/your/server.js"
  ],
  "env": {
    "API_KEY": "your-api-key"
  },
  "autoStart": true,
  "priority": 100
}
```

### 2. Update `.cursor/mcp.json`

Add your server to the `mcpServers` section and your configuration file to the `configPaths` array:

```json
{
  "mcpServers": {
    "your-server": {
      "command": "node",
      "args": [
        "C:/path/to/your/server.js"
      ],
      "type": "stdio",
      "env": {
        "DEBUG": "*",
        "NODE_ENV": "development",
        "API_KEY": "your-api-key"
      },
      "windowsHide": true
    }
  },
  "configPaths": [
    ".cursor/mcp/your-server.json"
  ]
}
```

### 3. Create Start Script

Create a batch file to start your MCP server:

```batch
@echo off
echo Starting Your MCP Server...

:: Set environment variables
set API_KEY=your-api-key
set DEBUG=mcp:*
set NODE_ENV=development

:: Start the MCP server
node "C:/path/to/your/server.js"

echo Your MCP Server started.
```

## Best Practices

1. **Error Handling**: Implement robust error handling to ensure your MCP server can recover from errors.
2. **Logging**: Use logging to track server activity and diagnose issues.
3. **Configuration**: Use configuration files to store settings and API keys.
4. **Testing**: Create test scripts to verify that your MCP server works correctly.
5. **Documentation**: Document your MCP server and its tools.

## Examples

### Example 1: Weather API MCP Server

```javascript
const readline = require('readline');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

class WeatherAPIClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = 'https://api.weatherapi.com/v1';
  }

  async getCurrentWeather(location) {
    const url = `${this.baseUrl}/current.json?key=${this.apiKey}&q=${encodeURIComponent(location)}`;
    const response = await axios.get(url);
    return response.data;
  }

  async getForecast(location, days) {
    const url = `${this.baseUrl}/forecast.json?key=${this.apiKey}&q=${encodeURIComponent(location)}&days=${days}`;
    const response = await axios.get(url);
    return response.data;
  }
}

class WeatherMCPServer {
  constructor() {
    // Initialize properties
    this.apiKey = process.env.WEATHER_API_KEY;
    this.client = new WeatherAPIClient(this.apiKey);
    this.running = false;
    this.requestMap = new Map();

    // Set up stdin/stdout for MCP communication
    this.stdin = process.stdin;
    this.stdout = process.stdout;
    this.rl = readline.createInterface({
      input: this.stdin,
      output: this.stdout,
      terminal: false
    });

    // Define MCP tools
    this.tools = {
      'get_current_weather': {
        name: 'get_current_weather',
        description: 'Get the current weather for a location',
        parameters: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: 'The location to get weather for'
            }
          },
          required: ['location']
        },
        handler: this.handleGetCurrentWeather.bind(this)
      },
      'get_forecast': {
        name: 'get_forecast',
        description: 'Get the weather forecast for a location',
        parameters: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: 'The location to get weather for'
            },
            days: {
              type: 'number',
              description: 'The number of days to forecast'
            }
          },
          required: ['location']
        },
        handler: this.handleGetForecast.bind(this)
      }
    };

    // Bind methods
    this.handleMessage = this.handleMessage.bind(this);
    this.sendResponse = this.sendResponse.bind(this);
    this.sendError = this.sendError.bind(this);
  }

  // ... (rest of the server implementation)

  // Handle a get current weather request
  async handleGetCurrentWeather(id, args) {
    const { location } = args;

    // Validate required parameters
    if (!location) {
      return this.sendError(id, 'missing_parameter', 'Missing required parameter: location');
    }

    try {
      // Call the API
      const result = await this.client.getCurrentWeather(location);

      // Send the response
      this.sendResponse(id, {
        location: result.location.name,
        country: result.location.country,
        temperature: result.current.temp_c,
        condition: result.current.condition.text,
        humidity: result.current.humidity,
        wind_speed: result.current.wind_kph
      });
    } catch (error) {
      this.sendError(id, 'api_error', `API error: ${error.message}`);
    }
  }

  // Handle a get forecast request
  async handleGetForecast(id, args) {
    const { location, days = 3 } = args;

    // Validate required parameters
    if (!location) {
      return this.sendError(id, 'missing_parameter', 'Missing required parameter: location');
    }

    try {
      // Call the API
      const result = await this.client.getForecast(location, days);

      // Send the response
      this.sendResponse(id, {
        location: result.location.name,
        country: result.location.country,
        forecast: result.forecast.forecastday.map(day => ({
          date: day.date,
          max_temp: day.day.maxtemp_c,
          min_temp: day.day.mintemp_c,
          condition: day.day.condition.text,
          chance_of_rain: day.day.daily_chance_of_rain
        }))
      });
    } catch (error) {
      this.sendError(id, 'api_error', `API error: ${error.message}`);
    }
  }
}

// Create and start the server
const server = new WeatherMCPServer();
server.start();
```

### Example 2: Database MCP Server

```javascript
const readline = require('readline');
const { v4: uuidv4 } = require('uuid');
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');

class DatabaseClient {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
  }

  async connect() {
    this.db = await open({
      filename: this.dbPath,
      driver: sqlite3.Database
    });
  }

  async query(sql, params = []) {
    return this.db.all(sql, params);
  }

  async execute(sql, params = []) {
    return this.db.run(sql, params);
  }
}

class DatabaseMCPServer {
  constructor() {
    // Initialize properties
    this.dbPath = process.env.DB_PATH || 'database.db';
    this.client = new DatabaseClient(this.dbPath);
    this.running = false;
    this.requestMap = new Map();

    // Set up stdin/stdout for MCP communication
    this.stdin = process.stdin;
    this.stdout = process.stdout;
    this.rl = readline.createInterface({
      input: this.stdin,
      output: this.stdout,
      terminal: false
    });

    // Define MCP tools
    this.tools = {
      'query': {
        name: 'query',
        description: 'Execute a SQL query',
        parameters: {
          type: 'object',
          properties: {
            sql: {
              type: 'string',
              description: 'The SQL query to execute'
            },
            params: {
              type: 'array',
              description: 'The parameters for the query'
            }
          },
          required: ['sql']
        },
        handler: this.handleQuery.bind(this)
      },
      'execute': {
        name: 'execute',
        description: 'Execute a SQL statement',
        parameters: {
          type: 'object',
          properties: {
            sql: {
              type: 'string',
              description: 'The SQL statement to execute'
            },
            params: {
              type: 'array',
              description: 'The parameters for the statement'
            }
          },
          required: ['sql']
        },
        handler: this.handleExecute.bind(this)
      }
    };

    // Bind methods
    this.handleMessage = this.handleMessage.bind(this);
    this.sendResponse = this.sendResponse.bind(this);
    this.sendError = this.sendError.bind(this);
  }

  // ... (rest of the server implementation)

  // Start the MCP server
  async start() {
    console.error('Starting Database MCP Server');

    try {
      // Connect to the database
      await this.client.connect();

      // Set up message handling
      this.running = true;
      this.rl.on('line', this.handleMessage);

      // Send server info
      this.sendServerInfo();

      console.error('Database MCP Server started');
    } catch (error) {
      console.error('Error starting server:', error);
      process.exit(1);
    }
  }

  // Handle a query request
  async handleQuery(id, args) {
    const { sql, params = [] } = args;

    // Validate required parameters
    if (!sql) {
      return this.sendError(id, 'missing_parameter', 'Missing required parameter: sql');
    }

    try {
      // Execute the query
      const result = await this.client.query(sql, params);

      // Send the response
      this.sendResponse(id, {
        rows: result,
        count: result.length
      });
    } catch (error) {
      this.sendError(id, 'query_error', `Query error: ${error.message}`);
    }
  }

  // Handle an execute request
  async handleExecute(id, args) {
    const { sql, params = [] } = args;

    // Validate required parameters
    if (!sql) {
      return this.sendError(id, 'missing_parameter', 'Missing required parameter: sql');
    }

    try {
      // Execute the statement
      const result = await this.client.execute(sql, params);

      // Send the response
      this.sendResponse(id, {
        changes: result.changes,
        lastID: result.lastID
      });
    } catch (error) {
      this.sendError(id, 'execute_error', `Execute error: ${error.message}`);
    }
  }
}

// Create and start the server
const server = new DatabaseMCPServer();
server.start();
```

## Conclusion

Creating custom MCP servers allows you to extend the capabilities of Cursor/Roocode with your own tools and integrations. By following this guide, you can create MCP servers that provide access to external APIs, custom tools, and other resources.

For more information, see the OpenRouter MCP server implementation in the EGOS project.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
