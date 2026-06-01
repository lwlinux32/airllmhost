# AirLLMHost - REST API Server for AirLLM

A Flask-based REST API server that provides an easy-to-use interface for running large language models efficiently using [AirLLM](https://github.com/lyogavin/airllm). Run 122B+ models on minimal GPU memory with a simple HTTP API.

## Features

✨ **Multiple Endpoints:**
- Single-turn generation and chat
- Multi-turn conversations with session history
- Session management (view history, clear sessions)
- Model information and health checks

⚡ **Efficient:**
- Uses AirLLM for memory-optimized inference
- Supports model compression (4-bit/8-bit quantization)
- Conversation history management per session

🔧 **Easy Integration:**
- RESTful API design
- JSON request/response format
- CORS enabled for cross-origin requests
- Python client example included

## Installation

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (for optimal performance)
- Sufficient disk space (models require significant storage)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/lwlinux32/airllmhost.git
cd airllmhost

    Install dependencies:

bash

pip install -r requirements.txt

Usage
Starting the Server

Basic:
bash

python api_server.py

With custom model:
bash

python api_server.py --model "OpenYourMind/Qwopus3.5-122B-A10B-Kimi-K2.6-destill-healed-abliterated" --port 1410

With debug mode:
bash

python api_server.py --debug

Available arguments:
Code

--model MODEL           Model name or path (default: OpenYourMind/Qwopus3.5-122B-A10B-Kimi-K2.6-destill-healed-abliterated)
--host HOST             Host to bind to (default: 127.0.0.1)
--port PORT             Port to bind to (default: 1410)
--debug                 Enable debug mode

The server will start at http://localhost:1410 and display:
Code

Loading model: OpenYourMind/Qwopus3.5-122B-A10B-Kimi-K2.6-destill-healed-abliterated
Model loaded successfully
Starting API server on 127.0.0.1:1410

API Endpoints
1. Health Check

GET /health

Check if server is running and model is loaded.
bash

curl http://localhost:1410/health

Response:
JSON

{
  "status": "healthy",
  "model_loaded": true
}

2. Model Information

GET /info

Get information about the loaded model.
bash

curl http://localhost:1410/info

Response:
JSON

{
  "model_name": "Qwopus3.5-122B",
  "framework": "AirLLM",
  "status": "ready"
}

3. Generate Text

POST /generate

Generate text from a single prompt.
bash

curl -X POST http://localhost:1410/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "max_new_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9
  }'

Request Parameters:

    prompt (string, required): The input prompt
    max_new_tokens (integer, optional): Maximum tokens to generate (default: 100)
    temperature (float, optional): Sampling temperature (default: 0.7)
    top_p (float, optional): Nucleus sampling parameter (default: 0.9)
    use_cache (boolean, optional): Use KV cache (default: true)
    max_length (integer, optional): Maximum input length (default: 512)

Response:
JSON

{
  "success": true,
  "prompt": "What is artificial intelligence?",
  "response": "Artificial intelligence refers to...",
  "tokens_generated": 42
}

4. Single-Turn Chat

POST /chat

Chat endpoint without conversation history.
bash

curl -X POST http://localhost:1410/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How are you?",
    "max_new_tokens": 100,
    "temperature": 0.7
  }'

Request Parameters:

    message (string, required): User message
    max_new_tokens (integer, optional): Maximum tokens to generate (default: 100)
    temperature (float, optional): Sampling temperature (default: 0.7)

Response:
JSON

{
  "success": true,
  "user_message": "Hello! How are you?",
  "assistant_response": "Hello! I'm doing well, thank you for asking..."
}

5. Multi-Turn Chat with Session

POST /chat/session

Chat with conversation history maintained per session.
bash

curl -X POST http://localhost:1410/chat/session \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "What is Python?",
    "max_new_tokens": 100,
    "temperature": 0.7,
    "reset": false
  }'

Request Parameters:

    session_id (string, required): Unique session identifier
    message (string, required): User message
    max_new_tokens (integer, optional): Maximum tokens to generate (default: 100)
    temperature (float, optional): Sampling temperature (default: 0.7)
    reset (boolean, optional): Reset session history (default: false)

Response:
JSON

{
  "success": true,
  "session_id": "user123",
  "user_message": "What is Python?",
  "assistant_response": "Python is a high-level programming language...",
  "history_length": 2
}

6. Get Session History

GET /session/<session_id>

Retrieve conversation history for a specific session.
bash

curl http://localhost:1410/session/user123

Response:
JSON

{
  "session_id": "user123",
  "history": [
    "User: What is Python?",
    "Assistant: Python is a high-level programming language...",
    "User: Tell me more",
    "Assistant: Python was created by Guido van Rossum..."
  ],
  "message_count": 4
}

7. Clear Session History

DELETE /session/<session_id>

Clear conversation history for a specific session.
bash

curl -X DELETE http://localhost:1410/session/user123

Response:
JSON

{
  "success": true,
  "message": "Session user123 cleared"
}

Python Client Examples
Using the included client:
bash

python client_example.py

Programmatic usage:
Python

from client_example import chat, chat_with_session, get_session_history

# Single-turn chat
result = chat("What is AI?")
print(result['assistant_response'])

# Multi-turn chat with history
result = chat_with_session("user123", "Hello!")
print(result['assistant_response'])

result = chat_with_session("user123", "Tell me more about Python")
print(result['assistant_response'])

# Get full history
history = get_session_history("user123")
print(history['history'])

JavaScript/Node.js Example
JavaScript

const axios = require('axios');

const BASE_URL = 'http://localhost:1410';

async function chat(message) {
  const response = await axios.post(`${BASE_URL}/chat`, {
    message: message,
    max_new_tokens: 100,
    temperature: 0.7
  });
  return response.data;
}

async function chatWithSession(sessionId, message) {
  const response = await axios.post(`${BASE_URL}/chat/session`, {
    session_id: sessionId,
    message: message,
    max_new_tokens: 100,
    temperature: 0.7
  });
  return response.data;
}

// Usage
(async () => {
  const result = await chat("Hello!");
  console.log(result.assistant_response);
})();

Configuration
Adjusting Parameters

Response Length:

    Increase max_new_tokens for longer responses
    Typical range: 50-500

Response Diversity:

    temperature: 0.0-2.0 (lower = more deterministic, higher = more creative)
        0.0: Always same response
        0.7: Balanced (recommended)
        1.5+: Very creative

    top_p: 0.0-1.0 (nucleus sampling)
        0.9: Recommended (keep top 90% probability tokens)

Performance:

    Context length: Adjust max_length based on your GPU memory
    Compression: Enable with compression='4bit' in model loading for 3x speedup

Troubleshooting
Server won't start

    Ensure CUDA drivers are installed: nvidia-smi
    Check Python version: python --version (should be 3.8+)
    Verify GPU memory: nvidia-smi (requires 4GB+ for 70B models)

Out of Memory (OOM)

    Reduce max_new_tokens
    Reduce context length (max_length)
    Enable model compression in api_server.py
    Use a smaller model

Slow responses

    First response is slow while model loads (normal)
    Subsequent requests should be faster with caching
    Consider enabling compression for 3x speedup

Connection refused

    Check server is running: curl http://localhost:1410/health
    Verify port: default is 1410
    Check firewall settings

Advanced Usage
Using with Different Models
bash

# Llama 3 70B
python api_server.py --model "meta-llama/Llama-2-70b-hf"

# Qwen
python api_server.py --model "Qwen/Qwen-7B"

# ChatGLM
python api_server.py --model "THUDM/chatglm3-6b"

Docker Deployment

Create a Dockerfile:
Dockerfile

FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y python3-pip
RUN pip install -r requirements.txt

EXPOSE 1410
CMD ["python", "api_server.py", "--host", "0.0.0.0"]

Build and run:
bash

docker build -t airllmhost .
docker run --gpus all -p 1410:1410 airllmhost

Performance Tips

    Preload model: Server loads model on startup (first request takes longer)
    Use sessions: Multi-turn conversations reuse loaded weights
    Batch requests: Send multiple queries in parallel
    Enable compression: Use compression='4bit' for 3x speedup
    Adjust context: Larger context = slower but more contextual responses

API Rate Limits

Currently no built-in rate limiting. For production use, consider:

    Using a reverse proxy (nginx, Caddy)
    Adding middleware for rate limiting
    Implementing token-based authentication

Security Considerations

⚠️ This server is designed for local development/testing

For production use:

    Add authentication (API keys, OAuth)
    Use HTTPS/SSL encryption
    Restrict access with firewall rules
    Deploy behind reverse proxy
    Implement rate limiting
    Validate/sanitize all inputs

Contributing

Contributions are welcome! Feel free to:

    Report bugs
    Suggest features
    Submit pull requests
    Improve documentation

License

MIT License
References

    AirLLM GitHub
    Flask Documentation
    Hugging Face Models

Support

For issues and questions:

    Check troubleshooting section above
    Review AirLLM documentation
    Open an issue on GitHub
