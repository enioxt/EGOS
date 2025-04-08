# OpenRouter MCP Server

This directory contains the OpenRouter MCP (Model Context Protocol) server implementation for the EGOS project. The server provides intelligent model selection and cost optimization through the OpenRouter API.

## Overview

The OpenRouter MCP server allows you to use various AI models through a unified interface, automatically selecting the most appropriate model based on the task type, context size, and complexity. This helps optimize costs while ensuring appropriate model capabilities for each task.

## Files

- `openrouter_client.js`: Client for interacting with the OpenRouter API
- `openrouter_mcp_server.js`: MCP server implementation
- `test_openrouter_client.js`: Test script for the OpenRouter client
- `test_openrouter_mcp_server.js`: Test script for the OpenRouter MCP server

## Configuration

The OpenRouter MCP server is configured in the following files:

- `.cursor/mcp/openrouter.json`: Configuration for the OpenRouter MCP server
- `.cursor/mcp-servers/openrouter.json`: Configuration for the MCP server launcher
- `.cursor/mcp.json`: Main MCP configuration file (includes OpenRouter MCP server)

## Tools

The OpenRouter MCP server provides the following tools:

1. **`openrouter_chat`**: General chat completion with automatic model selection
   - Parameters: `prompt`, `options` (optional)
   - Returns: Model response

2. **`openrouter_code`**: Code-specific completion using Claude models
   - Parameters: `code_prompt`, `language` (optional), `options` (optional)
   - Returns: Generated code with explanation

3. **`openrouter_analyze`**: Analysis with context-appropriate models
   - Parameters: `content`, `analysis_type`, `options` (optional)
   - Returns: Analysis results

4. **`openrouter_select_model`**: Manual model selection override
   - Parameters: `model_name`, `prompt`, `options` (optional)
   - Returns: Model response

5. **`openrouter_status`**: Get status information about available models
   - Parameters: None
   - Returns: Model availability, quotas, etc.

## Models

The OpenRouter MCP server supports the following models:

### Code-focused models
- **Claude 3.7 Opus**: Complex coding tasks, architecture design, critical code generation
- **Claude 3.7 Sonnet**: Routine coding tasks, debugging, code explanations

### Long context models
- **Gemini 2.5 Pro Max**: Very large contexts (>100k tokens), complex analysis tasks
- **Gemini 2.5 Pro**: Medium-large contexts (30k-100k tokens)

### General & Simple tasks
- **Mistral Large**: General tasks with moderate complexity
- **Phi-3 Mini**: Simple tasks, quick responses, minimal context

## Model Selection Strategy

The OpenRouter MCP server uses the following strategy to select the appropriate model:

1. If the task involves code:
   - Use Claude 3.7 Opus for complex code
   - Use Claude 3.7 Sonnet for routine code

2. If the context is very large:
   - Use Gemini 2.5 Pro Max for contexts >100k tokens
   - Use Gemini 2.5 Pro for contexts 30k-100k tokens

3. For general tasks:
   - Use Mistral Large for medium complexity
   - Use Phi-3 Mini for low complexity

## Usage

### Starting the Server

You can start the OpenRouter MCP server using the provided batch file:

```
.cursor/start_openrouter_mcp.bat
```

### Testing the Client

You can test the OpenRouter client using the provided test script:

```
.cursor/test_openrouter_client.bat
```

### Testing the MCP Server

You can test the OpenRouter MCP server using the provided test script:

```
.cursor/test_openrouter_mcp_server.bat
```

## Creating Your Own MCP Server

To create your own MCP server, you can use this implementation as a template. Here are the key components you'll need:

1. **Client**: Implement a client for the API you want to use
2. **MCP Server**: Implement an MCP server that uses the client
3. **Configuration**: Create configuration files for your MCP server
4. **Tools**: Define the tools your MCP server will provide

For more details, see the implementation of the OpenRouter MCP server.

## Troubleshooting

If you encounter issues with the OpenRouter MCP server, check the following:

1. Make sure the OpenRouter API key is correctly set in the configuration files
2. Check the logs in `C:/Eva Guarani EGOS/logs/mcp/openrouter.log`
3. Run the test scripts to verify that the client and server are working correctly

## License

This code is part of the EGOS project and is subject to its licensing terms.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
