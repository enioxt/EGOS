@echo off
echo OpenRouter MCP Demo - Free Models
echo ================================
echo.

:: Set environment variables
set OPENROUTER_API_KEY=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
set DEBUG=mcp:*
set LOG_LEVEL=warn
set LOG_FORMAT=json
set NODE_ENV=development
set VERBOSE_OUTPUT=false

:: Check if the server is already running
echo Checking if OpenRouter MCP server is running...
node -e "const net = require('net'); const socket = new net.Socket(); socket.setTimeout(1000); socket.on('connect', () => { console.log('Server is already running.'); socket.end(); process.exit(0); }); socket.on('timeout', () => { console.log('Server is not running. Starting server...'); socket.destroy(); process.exit(1); }); socket.on('error', () => { console.log('Server is not running. Starting server...'); socket.destroy(); process.exit(1); }); socket.connect(38001, 'localhost');"

:: Start the server if it's not running
if %errorlevel% neq 0 (
    echo Starting OpenRouter MCP Server...
    start "OpenRouter MCP Server" cmd /c "%~dp0start_openrouter_mcp.bat"
    echo Waiting for server to start...
    timeout /t 3 > nul
)

echo.
echo Running OpenRouter MCP Demo...
echo.

:: Run the demo
node -e "
const net = require('net');
const { v4: uuidv4 } = require('uuid');

// Connect to the MCP server
const socket = new net.Socket();
socket.setTimeout(5000);

socket.on('timeout', () => {
    console.error('Connection timeout. Make sure the server is running.');
    process.exit(1);
});

socket.connect(38001, 'localhost', () => {
    console.log('Connected to OpenRouter MCP server');

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

                if (response.type === 'server_info') {
                    console.log('Server info received');
                    console.log('Available tools:');
                    response.server.tools.forEach(tool => {
                        console.log(`- ${tool.name}: ${tool.description}`);
                    });
                    console.log();

                    // Step 1: Check status (shows if free models are prioritized)
                    console.log('Step 1: Checking status...');
                    sendRequest({
                        id: 'demo-status-1',
                        type: 'tool_call',
                        tool: 'openrouter_status',
                        arguments: {}
                    });
                }
                else if (response.type === 'tool_result') {
                    if (response.id === 'demo-status-1') {
                        console.log('Status result received:');
                        console.log(`- Prioritizing free models: ${response.result.usageStats.prioritizingFree}`);
                        console.log(`- Available models: ${response.result.availableModels.length}`);
                        console.log();

                        // Step 2: Send a chat request with free models
                        console.log('Step 2: Sending chat request with free models...');
                        sendRequest({
                            id: 'demo-chat-free',
                            type: 'tool_call',
                            tool: 'openrouter_chat',
                            arguments: {
                                prompt: 'What are the benefits of using free AI models?',
                                options: {
                                    prioritizeFree: true
                                }
                            }
                        });
                    }
                    else if (response.id === 'demo-chat-free') {
                        console.log('Chat result received (free model):');
                        console.log(`- Model used: ${response.result.model}`);
                        console.log(`- Response: ${response.result.content.substring(0, 150)}...`);
                        console.log();

                        // Step 3: Toggle to paid models
                        console.log('Step 3: Toggling to paid models...');
                        sendRequest({
                            id: 'demo-toggle',
                            type: 'tool_call',
                            tool: 'openrouter_toggle_free_models',
                            arguments: {
                                prioritize_free: false
                            }
                        });
                    }
                    else if (response.id === 'demo-toggle') {
                        console.log('Toggle result received:');
                        console.log(`- Free models prioritized: ${response.result.prioritizeFree}`);
                        console.log(`- Free models available: ${response.result.freeModels.length}`);
                        console.log();

                        // Step 4: Send a chat request with paid models
                        console.log('Step 4: Sending chat request with paid models...');
                        sendRequest({
                            id: 'demo-chat-paid',
                            type: 'tool_call',
                            tool: 'openrouter_chat',
                            arguments: {
                                prompt: 'What are the benefits of using paid AI models?',
                                options: {
                                    prioritizeFree: false
                                }
                            }
                        });
                    }
                    else if (response.id === 'demo-chat-paid') {
                        console.log('Chat result received (paid model):');
                        console.log(`- Model used: ${response.result.model}`);
                        console.log(`- Response: ${response.result.content.substring(0, 150)}...`);
                        console.log();

                        // Step 5: Toggle back to free models
                        console.log('Step 5: Toggling back to free models...');
                        sendRequest({
                            id: 'demo-toggle-back',
                            type: 'tool_call',
                            tool: 'openrouter_toggle_free_models',
                            arguments: {
                                prioritize_free: true
                            }
                        });
                    }
                    else if (response.id === 'demo-toggle-back') {
                        console.log('Toggle result received:');
                        console.log(`- Free models prioritized: ${response.result.prioritizeFree}`);
                        console.log();

                        // Step 6: Check final status
                        console.log('Step 6: Checking final status...');
                        sendRequest({
                            id: 'demo-status-final',
                            type: 'tool_call',
                            tool: 'openrouter_status',
                            arguments: {}
                        });
                    }
                    else if (response.id === 'demo-status-final') {
                        console.log('Final status received:');
                        console.log(`- Prioritizing free models: ${response.result.usageStats.prioritizingFree}`);
                        console.log(`- Total requests: ${response.result.usageStats.totalRequests}`);
                        console.log();

                        console.log('Demo completed successfully!');
                        console.log();
                        console.log('Press Ctrl+C to exit or close this window.');
                    }
                }
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        }
    });

    // Function to send a request to the server
    function sendRequest(request) {
        socket.write(JSON.stringify(request) + '\n');
    }

    // Handle socket events
    socket.on('close', () => {
        console.log('Connection closed');
        process.exit(0);
    });

    socket.on('error', (error) => {
        console.error('Socket error:', error);
        process.exit(1);
    });
});
"

echo.
echo Demo completed. Press any key to exit.
pause > nul
