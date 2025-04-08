/**
 * OpenRouter MCP Server for EVA & GUARANI
 *
 * This server implements the Model Context Protocol (MCP) for OpenRouter,
 * providing intelligent model selection and cost optimization.
 *
 * Based on the MCP Server specification v1.0
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');
const { v4: uuidv4 } = require('uuid');
const OpenRouterClient = require('./openrouter_client');

// Configure logging
const LOG_LEVEL = process.env.MCP_LOG_LEVEL || 'warn'; // Changed from 'info' to 'warn' to reduce verbosity
const LOG_FILE = process.env.MCP_LOG_FILE || path.join(os.tmpdir(), 'openrouter-mcp.log');
const VERBOSE_OUTPUT = process.env.VERBOSE_OUTPUT === 'true'; // New flag to control console output

// Ensure log directory exists
const logDir = path.dirname(LOG_FILE);
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// Create logger
const logger = {
  debug: (message, data) => log('DEBUG', message, data),
  info: (message, data) => log('INFO', message, data),
  warn: (message, data) => log('WARN', message, data),
  error: (message, data) => log('ERROR', message, data)
};

/**
 * Log a message to the console and file
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} data - Additional data to log
 */
function log(level, message, data) {
  const levels = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
  if (levels[level] < levels[LOG_LEVEL]) return;

  const timestamp = new Date().toISOString();
  const logMessage = `${timestamp} [${level}] ${message}`;

  // Log to console only if verbose output is enabled or level is ERROR
  if (VERBOSE_OUTPUT || level === 'ERROR') {
    console.error(logMessage);
    if (data) console.error(JSON.stringify(data, null, 2));
  }

  // Log to file
  try {
    const logEntry = data
      ? `${logMessage}\n${JSON.stringify(data, null, 2)}\n`
      : `${logMessage}\n`;
    fs.appendFileSync(LOG_FILE, logEntry);
  } catch (error) {
    console.error(`Failed to write to log file: ${error.message}`);
  }
}

/**
 * OpenRouter MCP Server class
 */
class OpenRouterMCPServer {
  constructor() {
    // Initialize properties
    this.apiKey = process.env.OPENROUTER_API_KEY;
    this.client = new OpenRouterClient(this.apiKey);
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
      'openrouter_chat': {
        name: 'openrouter_chat',
        description: 'General chat completion with automatic model selection',
        parameters: {
          type: 'object',
          properties: {
            prompt: {
              type: 'string',
              description: 'The prompt text'
            },
            options: {
              type: 'object',
              description: 'Additional options',
              properties: {
                model: { type: 'string', description: 'Specific model to use (optional)' },
                maxTokens: { type: 'number', description: 'Maximum tokens to generate' },
                temperature: { type: 'number', description: 'Temperature for sampling' },
                useCache: { type: 'boolean', description: 'Whether to use cache' },
                prioritizeFree: { type: 'boolean', description: 'Whether to prioritize free models' }
              }
            }
          },
          required: ['prompt']
        },
        handler: this.handleChatCompletion.bind(this)
      },
      'openrouter_code': {
        name: 'openrouter_code',
        description: 'Code-specific completion using appropriate models',
        parameters: {
          type: 'object',
          properties: {
            code_prompt: {
              type: 'string',
              description: 'The code prompt'
            },
            language: {
              type: 'string',
              description: 'Programming language'
            },
            options: {
              type: 'object',
              description: 'Additional options',
              properties: {
                complexity: { type: 'string', description: 'Code complexity (low, medium, high)' },
                maxTokens: { type: 'number', description: 'Maximum tokens to generate' },
                temperature: { type: 'number', description: 'Temperature for sampling' },
                prioritizeFree: { type: 'boolean', description: 'Whether to prioritize free models' }
              }
            }
          },
          required: ['code_prompt']
        },
        handler: this.handleCodeCompletion.bind(this)
      },
      'openrouter_analyze': {
        name: 'openrouter_analyze',
        description: 'Analysis with context-appropriate models',
        parameters: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'The content to analyze'
            },
            analysis_type: {
              type: 'string',
              description: 'Type of analysis',
              enum: ['summarize', 'extract_key_points', 'sentiment', 'general']
            },
            options: {
              type: 'object',
              description: 'Additional options',
              properties: {
                maxTokens: { type: 'number', description: 'Maximum tokens to generate' },
                temperature: { type: 'number', description: 'Temperature for sampling' },
                prioritizeFree: { type: 'boolean', description: 'Whether to prioritize free models' }
              }
            }
          },
          required: ['content']
        },
        handler: this.handleContentAnalysis.bind(this)
      },
      'openrouter_select_model': {
        name: 'openrouter_select_model',
        description: 'Manual model selection override',
        parameters: {
          type: 'object',
          properties: {
            model_name: {
              type: 'string',
              description: 'Model name to use'
            },
            prompt: {
              type: 'string',
              description: 'The prompt text'
            },
            options: {
              type: 'object',
              description: 'Additional options',
              properties: {
                maxTokens: { type: 'number', description: 'Maximum tokens to generate' },
                temperature: { type: 'number', description: 'Temperature for sampling' }
              }
            }
          },
          required: ['model_name', 'prompt']
        },
        handler: this.handleSelectModel.bind(this)
      },
      'openrouter_toggle_free_models': {
        name: 'openrouter_toggle_free_models',
        description: 'Toggle between prioritizing free models and using optimal models',
        parameters: {
          type: 'object',
          properties: {
            prioritize_free: {
              type: 'boolean',
              description: 'Whether to prioritize free models (true) or use optimal models (false)'
            }
          },
          required: ['prioritize_free']
        },
        handler: this.handleToggleFreeModels.bind(this)
      },
      'openrouter_status': {
        name: 'openrouter_status',
        description: 'Get status information about available models',
        parameters: {
          type: 'object',
          properties: {}
        },
        handler: this.handleStatus.bind(this)
      }
    };

    // Bind methods
    this.handleMessage = this.handleMessage.bind(this);
    this.sendResponse = this.sendResponse.bind(this);
    this.sendError = this.sendError.bind(this);
  }

  /**
   * Start the MCP server
   */
  start() {
    logger.info('Starting OpenRouter MCP Server');

    // Print a simple startup message to the console
    console.log('OpenRouter MCP Server starting...');

    // Check if API key is configured
    if (!this.apiKey) {
      logger.error('OpenRouter API key not configured');
      process.exit(1);
    }

    // Set up message handling
    this.running = true;
    this.rl.on('line', this.handleMessage);

    // Send server info
    this.sendServerInfo();

    logger.info('OpenRouter MCP Server started');

    // Print a simple success message to the console
    console.log('OpenRouter MCP Server started successfully!');
    console.log('The server is now ready to accept requests.');
  }

  /**
   * Stop the MCP server
   */
  stop() {
    logger.info('Stopping OpenRouter MCP Server');
    this.running = false;
    this.rl.close();
    process.exit(0);
  }

  /**
   * Send server info to the client
   */
  sendServerInfo() {
    const serverInfo = {
      type: 'server_info',
      server: {
        name: 'EVA & GUARANI OpenRouter',
        version: '1.0.0',
        description: 'OpenRouter MCP Server with intelligent model selection',
        tools: Object.values(this.tools).map(tool => ({
          name: tool.name,
          description: tool.description,
          parameters: tool.parameters
        }))
      }
    };

    this.sendMessage(serverInfo);
  }

  /**
   * Handle an incoming message
   * @param {string} line - The message line
   */
  handleMessage(line) {
    try {
      // Parse the message
      const message = JSON.parse(line);
      logger.debug('Received message', message);

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
          logger.warn(`Unknown message type: ${message.type}`);
          this.sendError(message.id, 'unknown_message_type', `Unknown message type: ${message.type}`);
      }
    } catch (error) {
      logger.error('Error handling message', { error: error.message, line });
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

  /**
   * Handle a ping message
   * @param {Object} message - The ping message
   */
  handlePing(message) {
    this.sendMessage({
      id: message.id,
      type: 'pong'
    });
  }

  /**
   * Handle a shutdown message
   * @param {Object} message - The shutdown message
   */
  handleShutdown(message) {
    logger.info('Received shutdown request');
    this.sendMessage({
      id: message.id,
      type: 'shutdown_acknowledged'
    });

    // Stop the server after a short delay
    setTimeout(() => this.stop(), 100);
  }

  /**
   * Handle a tool call message
   * @param {Object} message - The tool call message
   */
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
      logger.error(`Error calling tool ${tool}`, { error: error.message, args });
      this.sendError(id, 'tool_execution_error', `Error executing tool ${tool}: ${error.message}`);
    }
  }

  /**
   * Handle a chat completion request
   * @param {string} id - The request ID
   * @param {Object} args - The request arguments
   */
  async handleChatCompletion(id, args) {
    try {
      const { prompt, options = {} } = args;

      // Validate required parameters
      if (!prompt) {
        return this.sendError(id, 'missing_parameter', 'Missing required parameter: prompt');
      }

      // Call the OpenRouter client
      const result = await this.client.chatCompletion({
        prompt,
        model: options.model,
        maxTokens: options.maxTokens,
        temperature: options.temperature,
        useCache: options.useCache,
        prioritizeFree: options.prioritizeFree
      });

      // Send the response
      this.sendResponse(id, {
        content: result.content,
        model: result.model,
        usage: result.usage
      });
    } catch (error) {
      logger.error('Error in chat completion', { error: error.message, args });
      this.sendError(id, 'chat_completion_error', `Error in chat completion: ${error.message}`);
    }
  }

  /**
   * Handle a code completion request
   * @param {string} id - The request ID
   * @param {Object} args - The request arguments
   */
  async handleCodeCompletion(id, args) {
    try {
      const { code_prompt, language, options = {} } = args;

      // Validate required parameters
      if (!code_prompt) {
        return this.sendError(id, 'missing_parameter', 'Missing required parameter: code_prompt');
      }

      // Call the OpenRouter client
      const result = await this.client.codeCompletion({
        prompt: code_prompt,
        language,
        complexity: options.complexity,
        maxTokens: options.maxTokens,
        temperature: options.temperature,
        prioritizeFree: options.prioritizeFree
      });

      // Send the response
      this.sendResponse(id, {
        content: result.content,
        model: result.model,
        usage: result.usage
      });
    } catch (error) {
      logger.error('Error in code completion', { error: error.message, args });
      this.sendError(id, 'code_completion_error', `Error in code completion: ${error.message}`);
    }
  }

  /**
   * Handle a content analysis request
   * @param {string} id - The request ID
   * @param {Object} args - The request arguments
   */
  async handleContentAnalysis(id, args) {
    try {
      const { content, analysis_type, options = {} } = args;

      // Validate required parameters
      if (!content) {
        return this.sendError(id, 'missing_parameter', 'Missing required parameter: content');
      }

      // Call the OpenRouter client
      const result = await this.client.analyzeContent({
        content,
        analysisType: analysis_type,
        maxTokens: options.maxTokens,
        temperature: options.temperature,
        prioritizeFree: options.prioritizeFree
      });

      // Send the response
      this.sendResponse(id, {
        content: result.content,
        model: result.model,
        usage: result.usage
      });
    } catch (error) {
      logger.error('Error in content analysis', { error: error.message, args });
      this.sendError(id, 'content_analysis_error', `Error in content analysis: ${error.message}`);
    }
  }

  /**
   * Handle a select model request
   * @param {string} id - The request ID
   * @param {Object} args - The request arguments
   */
  async handleSelectModel(id, args) {
    try {
      const { model_name, prompt, options = {} } = args;

      // Validate required parameters
      if (!model_name) {
        return this.sendError(id, 'missing_parameter', 'Missing required parameter: model_name');
      }
      if (!prompt) {
        return this.sendError(id, 'missing_parameter', 'Missing required parameter: prompt');
      }

      // Call the OpenRouter client
      const result = await this.client.chatCompletion({
        prompt,
        model: model_name,
        maxTokens: options.maxTokens,
        temperature: options.temperature
      });

      // Send the response
      this.sendResponse(id, {
        content: result.content,
        model: result.model,
        usage: result.usage
      });
    } catch (error) {
      logger.error('Error in select model', { error: error.message, args });
      this.sendError(id, 'select_model_error', `Error in select model: ${error.message}`);
    }
  }

  /**
   * Handle a status request
   * @param {string} id - The request ID
   * @param {Object} args - The request arguments
   */
  async handleStatus(id, args) {
    try {
      // Call the OpenRouter client
      const status = await this.client.getStatus();

      // Send the response
      this.sendResponse(id, status);
    } catch (error) {
      logger.error('Error getting status', { error: error.message });
      this.sendError(id, 'status_error', `Error getting status: ${error.message}`);
    }
  }

  /**
   * Handle a toggle free models request
   * @param {string} id - The request ID
   * @param {Object} args - The request arguments
   */
  async handleToggleFreeModels(id, args) {
    try {
      const { prioritize_free } = args;

      // Validate required parameters
      if (prioritize_free === undefined) {
        return this.sendError(id, 'missing_parameter', 'Missing required parameter: prioritize_free');
      }

      // Update the client's prioritizeFree setting
      this.client.prioritizeFree = prioritize_free;

      // Send the response
      this.sendResponse(id, {
        prioritizeFree: this.client.prioritizeFree,
        message: `Free models ${this.client.prioritizeFree ? 'prioritized' : 'not prioritized'}`,
        freeModels: Object.entries(this.client.models)
          .filter(([_, model]) => model.isFree)
          .map(([id, model]) => ({
            id,
            name: model.name,
            provider: model.provider,
            contextSize: model.contextSize
          }))
      });
    } catch (error) {
      logger.error('Error toggling free models', { error: error.message, args });
      this.sendError(id, 'toggle_free_models_error', `Error toggling free models: ${error.message}`);
    }
  }

  /**
   * Send a message to the client
   * @param {Object} message - The message to send
   */
  sendMessage(message) {
    const json = JSON.stringify(message);

    // Always write to stdout for MCP protocol communication
    this.stdout.write(json + '\n');

    // Only log debug messages if verbose output is enabled
    if (VERBOSE_OUTPUT) {
      logger.debug('Sent message', message);
    }

    // Print a cleaner message for server_info to avoid cluttering the console
    if (!VERBOSE_OUTPUT && message.type === 'server_info') {
      console.log(`Server initialized with ${message.server.tools.length} tools.`);
    }
  }

  /**
   * Send a response to the client
   * @param {string} id - The request ID
   * @param {Object} result - The response result
   */
  sendResponse(id, result) {
    this.sendMessage({
      id,
      type: 'tool_result',
      result
    });
  }

  /**
   * Send an error to the client
   * @param {string} id - The request ID
   * @param {string} code - The error code
   * @param {string} message - The error message
   */
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
const server = new OpenRouterMCPServer();
server.start();

// Handle process signals
process.on('SIGINT', () => {
  logger.info('Received SIGINT signal');
  server.stop();
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM signal');
  server.stop();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', { error: error.message, stack: error.stack });
  server.stop();
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled promise rejection', { reason, promise });
  server.stop();
});
