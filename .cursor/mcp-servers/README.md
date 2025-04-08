# OpenRouter MCP Server with Free Models

This directory contains the OpenRouter MCP (Model Context Protocol) server implementation for the EGOS project. The server provides intelligent model selection and cost optimization through the OpenRouter API, with a focus on prioritizing free models by default.

## Overview

The OpenRouter MCP server allows you to use various AI models through a unified interface, automatically selecting the most appropriate model based on the task type, context size, and complexity. By default, it prioritizes free models to optimize costs while ensuring appropriate model capabilities for each task.

## Free Models

The following free models are available:

- **Gemini 2.5 Flash**: General tasks with medium-large contexts
- **Llama 3 70B**: General tasks with medium complexity and code tasks
- **Phi-3 Mini**: Simple tasks, quick responses, minimal context

These models are set as the defaults for different types of tasks:
- **Default model** (general tasks): `phi-3-mini-128k`
- **Code model** (code tasks): `llama-3-70b-instruct`
- **Long context model** (large contexts): `gemini-1.5-flash`

## Paid Models (Fallbacks)

The following paid models are available as fallbacks when free models are not prioritized:

- **Claude 3.7 Opus**: Complex coding tasks, architecture design
- **Claude 3.7 Sonnet**: Routine coding tasks, debugging
- **Gemini 2.5 Pro Max**: Very large contexts (>100k tokens)
- **Gemini 2.5 Pro**: Large contexts (30k-100k tokens)
- **Mistral Large**: General tasks with moderate complexity

## Files

- `openrouter_client.js`: Client for interacting with the OpenRouter API
- `openrouter_mcp_server.js`: MCP server implementation
- `test_openrouter_client.js`: Test script for the OpenRouter client
- `test_openrouter_mcp_server.js`: Test script for the OpenRouter MCP server
- `test_free_models.js`: Test script for the free models functionality

## Tools

The OpenRouter MCP server provides the following tools:

1. **`openrouter_chat`**: General chat completion with automatic model selection
   - Parameters: `prompt`, `options` (optional)
   - Returns: Model response

2. **`openrouter_code`**: Code-specific completion using appropriate models
   - Parameters: `code_prompt`, `language` (optional), `options` (optional)
   - Returns: Generated code with explanation

3. **`openrouter_analyze`**: Analysis with context-appropriate models
   - Parameters: `content`, `analysis_type`, `options` (optional)
   - Returns: Analysis results

4. **`openrouter_select_model`**: Manual model selection override
   - Parameters: `model_name`, `prompt`, `options` (optional)
   - Returns: Model response

5. **`openrouter_toggle_free_models`**: Toggle between prioritizing free models and using optimal models
   - Parameters: `prioritize_free`
   - Returns: Toggle result with free models information

6. **`openrouter_status`**: Get status information about available models
   - Parameters: None
   - Returns: Model availability, usage statistics, etc.

## Usage

### Starting the Server

You can start the OpenRouter MCP server in two ways:

#### Foreground Mode (for debugging)

```
.cursor/start_openrouter_mcp.bat
```

This will:
- Start the server in the foreground
- Show all output directly in the console
- Allow you to see any errors that occur
- Run until you press Ctrl+C to stop it

#### Background Mode (for normal use)

```
.cursor/start_openrouter_mcp_background.bat
```

This will:
- Check if the server is already running
- Start the server in the background if it's not running
- Redirect the server output to a log file
- Show a success message when the server is started

### Stopping the Server

You can stop the OpenRouter MCP server using the provided batch file:

```
.cursor/stop_openrouter_mcp.bat
```

This will:
- Check if the server is running
- Find the process ID of the server
- Kill the process
- Show a success message when the server is stopped

### Testing the Server

You can test the OpenRouter MCP server using the provided batch files:

```
.cursor/test_openrouter_simple.bat
```

This will:
- Start a test instance of the server
- Test the status tool
- Show information about available models
- Shut down the test server

### Running the Demo

You can run a demo of the OpenRouter MCP server using the provided batch file:

```
.cursor/openrouter_demo.bat
```

This will:
- Check if the server is running and start it if needed
- Connect to the server
- Check the initial status (free models prioritized by default)
- Send a chat request using free models
- Toggle to paid models
- Send a chat request using paid models
- Toggle back to free models
- Check the final status

## Model Selection Logic

The OpenRouter MCP server uses the following logic to select the appropriate model:

1. If a preferred model is specified, use it
2. Check if free models should be prioritized (default: true)
3. Select the appropriate model based on:
   - Task type (code, general)
   - Context length
   - Task complexity

By default, free models are prioritized for all tasks. You can toggle this behavior using the `openrouter_toggle_free_models` tool.

## Benefits of Using Free Models

1. **Cost Savings**: Free models don't incur any usage costs, which can significantly reduce your API expenses.
2. **Suitable for Many Tasks**: The free models are capable of handling a wide range of tasks with good quality results.
3. **Toggle Flexibility**: You can easily switch between free and paid models based on your needs.

## Troubleshooting

If you encounter issues with the OpenRouter MCP server:

1. Check the log files:
   - Server log: `C:/Eva Guarani EGOS/logs/mcp/openrouter.log`
   - Server stdout: `C:/Eva Guarani EGOS/logs/mcp/openrouter_stdout.log`

2. Make sure the server is running:
   - Run `netstat -an | findstr ":38001"` to check if the server is listening on port 38001

3. Restart the server:
   - Run `.cursor/stop_openrouter_mcp.bat` to stop the server
   - Run `.cursor/start_openrouter_mcp.bat` to start the server again

4. Debugging issues:
   - Run the server in foreground mode (`.cursor/start_openrouter_mcp.bat`) to see any errors directly
   - Check if the logs directory exists: `C:/Eva Guarani EGOS/logs/mcp`
   - Make sure Node.js is installed and working correctly

## License

This code is part of the EGOS project and is subject to its licensing terms.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
