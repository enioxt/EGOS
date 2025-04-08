/**
 * OpenRouter API Client for EVA & GUARANI
 *
 * This client handles communication with the OpenRouter API, including:
 * - Authentication
 * - Request/response handling
 * - Error management
 * - Model selection
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');

class OpenRouterClient {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.OPENROUTER_API_KEY;
    this.baseUrl = 'https://openrouter.ai/api/v1';
    this.models = {
      // Code-focused models
      'claude-3-opus-20240229': {
        provider: 'anthropic',
        name: 'Claude 3.7 Opus',
        category: 'code',
        complexity: 'high',
        contextSize: 200000,
        costPer1kTokensInput: 0.015,
        costPer1kTokensOutput: 0.075,
        isFree: false
      },
      'claude-3-sonnet-20240229': {
        provider: 'anthropic',
        name: 'Claude 3.7 Sonnet',
        category: 'code',
        complexity: 'medium',
        contextSize: 200000,
        costPer1kTokensInput: 0.003,
        costPer1kTokensOutput: 0.015,
        isFree: false
      },

      // Long context models
      'gemini-1.5-pro-latest': {
        provider: 'google',
        name: 'Gemini 2.5 Pro Max',
        category: 'context',
        complexity: 'high',
        contextSize: 1000000,
        costPer1kTokensInput: 0.00035,
        costPer1kTokensOutput: 0.00175,
        isFree: false
      },
      'gemini-1.0-pro': {
        provider: 'google',
        name: 'Gemini 2.5 Pro',
        category: 'context',
        complexity: 'medium',
        contextSize: 100000,
        costPer1kTokensInput: 0.00025,
        costPer1kTokensOutput: 0.00125,
        isFree: false
      },

      // Free models
      'gemini-1.5-flash': {
        provider: 'google',
        name: 'Gemini 2.5 Flash',
        category: 'general',
        complexity: 'medium',
        contextSize: 128000,
        costPer1kTokensInput: 0.0,  // Free
        costPer1kTokensOutput: 0.0,  // Free
        isFree: true
      },
      'llama-3-70b-instruct': {
        provider: 'meta',
        name: 'Llama 3 70B',
        category: 'general',
        complexity: 'medium',
        contextSize: 8192,
        costPer1kTokensInput: 0.0,  // Free
        costPer1kTokensOutput: 0.0,  // Free
        isFree: true
      },

      // General & Simple tasks
      'mistral-large-latest': {
        provider: 'mistral',
        name: 'Mistral Large',
        category: 'general',
        complexity: 'medium',
        contextSize: 32000,
        costPer1kTokensInput: 0.0002,
        costPer1kTokensOutput: 0.0006,
        isFree: false
      },
      'phi-3-mini-128k': {
        provider: 'microsoft',
        name: 'Phi-3 Mini',
        category: 'general',
        complexity: 'low',
        contextSize: 128000,
        costPer1kTokensInput: 0.0,  // Free
        costPer1kTokensOutput: 0.0,  // Free
        isFree: true
      }
    };

    // Set free models as defaults
    this.defaultModel = 'phi-3-mini-128k'; // Free model for general tasks
    this.codeModel = 'llama-3-70b-instruct'; // Free model for code tasks
    this.longContextModel = 'gemini-1.5-flash'; // Free model for long context tasks

    // Set paid models as fallbacks
    this.paidDefaultModel = 'mistral-large-latest';
    this.paidCodeModel = 'claude-3-sonnet-20240229';
    this.paidLongContextModel = 'gemini-1.0-pro';

    this.prioritizeFree = true; // Default to prioritizing free models

    // Create a cache directory if it doesn't exist
    this.cacheDir = path.join(os.tmpdir(), 'openrouter-cache');
    if (!fs.existsSync(this.cacheDir)) {
      fs.mkdirSync(this.cacheDir, { recursive: true });
    }

    // Initialize the cache
    this.cache = {};
    this.cacheFile = path.join(this.cacheDir, 'cache.json');
    this.loadCache();

    // Initialize usage tracking
    this.usage = {
      totalRequests: 0,
      totalTokensInput: 0,
      totalTokensOutput: 0,
      totalCost: 0,
      modelUsage: {}
    };
    this.usageFile = path.join(this.cacheDir, 'usage.json');
    this.loadUsage();

    // Set up axios instance with default headers
    this.client = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'HTTP-Referer': 'https://github.com/enioxt/EVA-e-Guarani-EGOS',
        'X-Title': 'EVA & GUARANI EGOS'
      }
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => this.handleApiError(error)
    );
  }

  /**
   * Load the cache from disk
   */
  loadCache() {
    try {
      if (fs.existsSync(this.cacheFile)) {
        const cacheData = fs.readFileSync(this.cacheFile, 'utf8');
        this.cache = JSON.parse(cacheData);

        // Clean up old cache entries (older than 24 hours)
        const now = Date.now();
        Object.keys(this.cache).forEach(key => {
          if (now - this.cache[key].timestamp > 24 * 60 * 60 * 1000) {
            delete this.cache[key];
          }
        });
      }
    } catch (error) {
      console.error('Error loading cache:', error);
      this.cache = {};
    }
  }

  /**
   * Save the cache to disk
   */
  saveCache() {
    try {
      fs.writeFileSync(this.cacheFile, JSON.stringify(this.cache), 'utf8');
    } catch (error) {
      console.error('Error saving cache:', error);
    }
  }

  /**
   * Load usage data from disk
   */
  loadUsage() {
    try {
      if (fs.existsSync(this.usageFile)) {
        const usageData = fs.readFileSync(this.usageFile, 'utf8');
        this.usage = JSON.parse(usageData);
      }
    } catch (error) {
      console.error('Error loading usage data:', error);
    }
  }

  /**
   * Save usage data to disk
   */
  saveUsage() {
    try {
      fs.writeFileSync(this.usageFile, JSON.stringify(this.usage), 'utf8');
    } catch (error) {
      console.error('Error saving usage data:', error);
    }
  }

  /**
   * Handle API errors
   * @param {Error} error - The error object
   * @returns {Promise<Error>} - A rejected promise with the error
   */
  handleApiError(error) {
    let errorMessage = 'Unknown error occurred';
    let statusCode = 500;

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      statusCode = error.response.status;
      errorMessage = error.response.data.error || error.response.data.message || `Error ${statusCode}`;

      console.error('API Error Response:', {
        status: statusCode,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      // The request was made but no response was received
      errorMessage = 'No response received from OpenRouter API';
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      errorMessage = error.message;
      console.error('Error setting up request:', error.message);
    }

    // Create a structured error object
    const enhancedError = new Error(errorMessage);
    enhancedError.statusCode = statusCode;
    enhancedError.originalError = error;

    // Implement retry logic for certain errors
    if (statusCode === 429 || statusCode >= 500) {
      console.log('Retryable error detected, will retry after delay');
      // The retry logic would be implemented here in a real system
    }

    return Promise.reject(enhancedError);
  }

  /**
   * Select the appropriate model based on the task
   * @param {Object} options - Selection options
   * @param {string} options.prompt - The prompt text
   * @param {boolean} options.isCode - Whether the task involves code
   * @param {number} options.contextLength - Estimated context length
   * @param {string} options.complexity - Task complexity (low, medium, high)
   * @param {string} options.preferredModel - Preferred model (optional)
   * @returns {string} - The selected model ID
   */
  selectModel(options) {
    // If a preferred model is specified and it exists, use it
    if (options.preferredModel && this.models[options.preferredModel]) {
      return options.preferredModel;
    }

    // Check if we should prioritize free models
    const prioritizeFree = options.prioritizeFree !== undefined ?
      options.prioritizeFree : this.prioritizeFree;

    // If the task involves code, select a code-focused model
    if (options.isCode) {
      if (options.complexity === 'high') {
        // For high complexity code tasks
        return prioritizeFree ? this.codeModel : 'claude-3-opus-20240229';
      } else {
        // For medium/low complexity code tasks
        return prioritizeFree ? this.codeModel : this.paidCodeModel;
      }
    }

    // If the context is very large, select a long context model
    if (options.contextLength > 100000) {
      // For very large contexts
      return prioritizeFree ? this.longContextModel : 'gemini-1.5-pro-latest';
    } else if (options.contextLength > 30000) {
      // For large contexts
      return prioritizeFree ? this.longContextModel : this.paidLongContextModel;
    }

    // For general tasks, select based on complexity
    if (options.complexity === 'medium') {
      // For medium complexity general tasks
      return prioritizeFree ? 'llama-3-70b-instruct' : this.paidDefaultModel;
    } else {
      // For low complexity general tasks (always use free model)
      return this.defaultModel; // phi-3-mini-128k (free)
    }
  }

  /**
   * Estimate the number of tokens in a text
   * @param {string} text - The text to estimate
   * @returns {number} - Estimated token count
   */
  estimateTokenCount(text) {
    // A very simple estimation: ~4 characters per token
    // This is a rough estimate and should be replaced with a proper tokenizer
    return Math.ceil(text.length / 4);
  }

  /**
   * Track usage for a request
   * @param {string} modelId - The model ID
   * @param {number} inputTokens - Number of input tokens
   * @param {number} outputTokens - Number of output tokens
   */
  trackUsage(modelId, inputTokens, outputTokens) {
    const model = this.models[modelId];
    if (!model) return;

    // Calculate cost
    const inputCost = (inputTokens / 1000) * model.costPer1kTokensInput;
    const outputCost = (outputTokens / 1000) * model.costPer1kTokensOutput;
    const totalCost = inputCost + outputCost;

    // Update global usage
    this.usage.totalRequests++;
    this.usage.totalTokensInput += inputTokens;
    this.usage.totalTokensOutput += outputTokens;
    this.usage.totalCost += totalCost;

    // Update model-specific usage
    if (!this.usage.modelUsage[modelId]) {
      this.usage.modelUsage[modelId] = {
        requests: 0,
        tokensInput: 0,
        tokensOutput: 0,
        cost: 0
      };
    }

    this.usage.modelUsage[modelId].requests++;
    this.usage.modelUsage[modelId].tokensInput += inputTokens;
    this.usage.modelUsage[modelId].tokensOutput += outputTokens;
    this.usage.modelUsage[modelId].cost += totalCost;

    // Save usage data
    this.saveUsage();
  }

  /**
   * Generate a cache key for a request
   * @param {Object} params - Request parameters
   * @returns {string} - Cache key
   */
  generateCacheKey(params) {
    // Create a deterministic string representation of the params
    const paramsString = JSON.stringify(params, Object.keys(params).sort());

    // Create a simple hash of the string
    let hash = 0;
    for (let i = 0; i < paramsString.length; i++) {
      const char = paramsString.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }

    return `${params.model || 'default'}_${hash}`;
  }

  /**
   * Check if a response is cached
   * @param {Object} params - Request parameters
   * @returns {Object|null} - Cached response or null
   */
  getCachedResponse(params) {
    const cacheKey = this.generateCacheKey(params);
    const cachedItem = this.cache[cacheKey];

    if (cachedItem && Date.now() - cachedItem.timestamp < 3600000) { // 1 hour cache
      console.log('Cache hit:', cacheKey);
      return cachedItem.response;
    }

    return null;
  }

  /**
   * Cache a response
   * @param {Object} params - Request parameters
   * @param {Object} response - Response to cache
   */
  cacheResponse(params, response) {
    const cacheKey = this.generateCacheKey(params);

    this.cache[cacheKey] = {
      timestamp: Date.now(),
      response: response
    };

    // Save cache to disk
    this.saveCache();
  }

  /**
   * Send a chat completion request to OpenRouter
   * @param {Object} params - Request parameters
   * @param {string} params.prompt - The prompt text
   * @param {string} params.model - Model ID (optional)
   * @param {boolean} params.isCode - Whether the task involves code (optional)
   * @param {string} params.complexity - Task complexity (optional)
   * @param {number} params.maxTokens - Maximum tokens to generate (optional)
   * @param {number} params.temperature - Temperature (optional)
   * @param {boolean} params.stream - Whether to stream the response (optional)
   * @param {boolean} params.useCache - Whether to use cache (optional)
   * @returns {Promise<Object>} - The response from OpenRouter
   */
  async chatCompletion(params) {
    // Check cache if enabled
    if (params.useCache !== false) {
      const cachedResponse = this.getCachedResponse(params);
      if (cachedResponse) {
        return cachedResponse;
      }
    }

    // Estimate context length
    const contextLength = this.estimateTokenCount(params.prompt);

    // Select model if not specified
    const modelId = params.model || this.selectModel({
      prompt: params.prompt,
      isCode: params.isCode || this.detectCode(params.prompt),
      contextLength: contextLength,
      complexity: params.complexity || this.detectComplexity(params.prompt),
      prioritizeFree: params.prioritizeFree
    });

    // Prepare request payload
    const payload = {
      model: modelId,
      messages: [
        { role: 'user', content: params.prompt }
      ],
      max_tokens: params.maxTokens || 1024,
      temperature: params.temperature || 0.7,
      stream: params.stream || false
    };

    try {
      console.log(`Sending request to OpenRouter (model: ${modelId})`);

      // Send request to OpenRouter
      const response = await this.client.post('/chat/completions', payload);

      // Extract response content
      const result = {
        model: response.data.model,
        content: response.data.choices[0].message.content,
        usage: response.data.usage
      };

      // Track usage
      this.trackUsage(
        modelId,
        response.data.usage.prompt_tokens,
        response.data.usage.completion_tokens
      );

      // Cache response if not streaming
      if (!params.stream && params.useCache !== false) {
        this.cacheResponse(params, result);
      }

      return result;
    } catch (error) {
      console.error(`Error in chatCompletion with model ${modelId}:`, error.message);

      // If this is a model-specific error, try falling back to a different model
      if (error.statusCode === 404 || error.statusCode === 400) {
        if (modelId !== this.defaultModel) {
          console.log(`Falling back to default model: ${this.defaultModel}`);
          return this.chatCompletion({
            ...params,
            model: this.defaultModel
          });
        }
      }

      throw error;
    }
  }

  /**
   * Send a code completion request to OpenRouter
   * @param {Object} params - Request parameters
   * @param {string} params.prompt - The code prompt
   * @param {string} params.language - Programming language (optional)
   * @param {string} params.complexity - Code complexity (optional)
   * @param {number} params.maxTokens - Maximum tokens to generate (optional)
   * @param {number} params.temperature - Temperature (optional)
   * @returns {Promise<Object>} - The response from OpenRouter
   */
  async codeCompletion(params) {
    // Enhance the prompt with language information if provided
    let enhancedPrompt = params.prompt;
    if (params.language) {
      enhancedPrompt = `Please provide code in ${params.language}:\n\n${params.prompt}`;
    }

    // Select the appropriate code model based on complexity and free model preference
    let modelId;
    if (params.prioritizeFree !== undefined ? params.prioritizeFree : this.prioritizeFree) {
      modelId = this.codeModel; // Free model for code
    } else {
      modelId = params.complexity === 'high' ?
        'claude-3-opus-20240229' : this.paidCodeModel;
    }

    return this.chatCompletion({
      prompt: enhancedPrompt,
      model: modelId,
      isCode: true,
      complexity: params.complexity || 'medium',
      maxTokens: params.maxTokens || 2048,
      temperature: params.temperature || 0.2,
      useCache: params.useCache
    });
  }

  /**
   * Analyze content with an appropriate model
   * @param {Object} params - Request parameters
   * @param {string} params.content - The content to analyze
   * @param {string} params.analysisType - Type of analysis (optional)
   * @param {number} params.maxTokens - Maximum tokens to generate (optional)
   * @param {number} params.temperature - Temperature (optional)
   * @returns {Promise<Object>} - The analysis results
   */
  async analyzeContent(params) {
    // Enhance the prompt based on analysis type
    let enhancedPrompt = '';

    switch (params.analysisType) {
      case 'summarize':
        enhancedPrompt = `Please summarize the following content:\n\n${params.content}`;
        break;
      case 'extract_key_points':
        enhancedPrompt = `Please extract the key points from the following content:\n\n${params.content}`;
        break;
      case 'sentiment':
        enhancedPrompt = `Please analyze the sentiment of the following content:\n\n${params.content}`;
        break;
      default:
        enhancedPrompt = `Please analyze the following content:\n\n${params.content}`;
    }

    // Estimate context length
    const contextLength = this.estimateTokenCount(params.content);

    // Select model based on context length
    let modelId;
    if (contextLength > 100000) {
      modelId = 'gemini-1.5-pro-latest';
    } else if (contextLength > 30000) {
      modelId = 'gemini-1.0-pro';
    } else {
      modelId = 'mistral-large-latest';
    }

    return this.chatCompletion({
      prompt: enhancedPrompt,
      model: modelId,
      isCode: false,
      contextLength: contextLength,
      complexity: 'medium',
      maxTokens: params.maxTokens || 1024,
      temperature: params.temperature || 0.5,
      useCache: params.useCache,
      prioritizeFree: params.prioritizeFree
    });
  }

  /**
   * Get status information about available models
   * @returns {Promise<Object>} - Status information
   */
  async getStatus() {
    try {
      // Get models from OpenRouter
      const response = await this.client.get('/models');

      // Process the response
      const availableModels = response.data.data.map(model => ({
        id: model.id,
        name: model.name,
        provider: model.provider,
        contextLength: model.context_length,
        pricing: model.pricing
      }));

      // Get usage statistics
      const usageStats = {
        totalRequests: this.usage.totalRequests,
        totalCost: this.usage.totalCost.toFixed(4),
        modelUsage: Object.entries(this.usage.modelUsage).map(([modelId, stats]) => ({
          model: this.models[modelId]?.name || modelId,
          requests: stats.requests,
          cost: stats.cost.toFixed(4),
          isFree: this.models[modelId]?.isFree || false
        })),
        prioritizingFree: this.prioritizeFree
      };

      return {
        availableModels,
        usageStats,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error getting status:', error);
      throw error;
    }
  }

  /**
   * Detect if a prompt contains code
   * @param {string} prompt - The prompt text
   * @returns {boolean} - Whether the prompt contains code
   */
  detectCode(prompt) {
    // Check for code markers
    const codeMarkers = [
      '```', 'function', 'class', 'def ', 'import ', 'from ', 'const ', 'let ', 'var ',
      'public class', 'private class', 'protected class', 'interface ', 'enum ',
      '#include', 'package ', 'using namespace', 'module.exports', 'export default',
      'SELECT ', 'INSERT INTO', 'UPDATE ', 'DELETE FROM'
    ];

    for (const marker of codeMarkers) {
      if (prompt.includes(marker)) {
        return true;
      }
    }

    // Check for code-like patterns
    const codePatterns = [
      /\b(if|else|for|while|switch|case|return|try|catch)\b.*\{/,
      /\b(def|class|function)\s+\w+\s*\(/,
      /\b(var|let|const)\s+\w+\s*=/,
      /\b(public|private|protected)\s+\w+\s+\w+\(/,
      /\b(import|export)\s+[\w\s,{}]*\s+from\s+['"]/
    ];

    for (const pattern of codePatterns) {
      if (pattern.test(prompt)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Detect the complexity of a prompt
   * @param {string} prompt - The prompt text
   * @returns {string} - Complexity level (low, medium, high)
   */
  detectComplexity(prompt) {
    // Simple heuristic based on length and complexity indicators
    const length = prompt.length;

    // Check for complexity indicators
    const complexityIndicators = [
      'complex', 'complicated', 'difficult', 'advanced', 'sophisticated',
      'analyze', 'analysis', 'evaluate', 'assessment', 'research',
      'compare', 'contrast', 'synthesize', 'critique', 'review',
      'architecture', 'design pattern', 'algorithm', 'optimization',
      'security', 'performance', 'scalability', 'reliability'
    ];

    let complexityScore = 0;

    // Add score based on length
    if (length > 5000) {
      complexityScore += 2;
    } else if (length > 1000) {
      complexityScore += 1;
    }

    // Add score based on complexity indicators
    for (const indicator of complexityIndicators) {
      if (prompt.toLowerCase().includes(indicator)) {
        complexityScore += 1;
      }
    }

    // Determine complexity level
    if (complexityScore >= 3) {
      return 'high';
    } else if (complexityScore >= 1) {
      return 'medium';
    } else {
      return 'low';
    }
  }
}

module.exports = OpenRouterClient;
