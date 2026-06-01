"""
AirLLM API Server
Provides a REST API for interacting with AirLLM models
Access at: http://localhost:1410
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from airllm import AutoModel
import torch
import threading
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global model instance
model = None
model_lock = threading.Lock()

# Store conversation history per session
conversation_history: Dict[str, List[str]] = {}


def load_model(model_name: str):
    """Load the model once at startup"""
    global model
    with model_lock:
        if model is None:
            logger.info(f"Loading model: {model_name}")
            model = AutoModel.from_pretrained(model_name)
            logger.info("Model loaded successfully")
    return model


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    }), 200


@app.route('/info', methods=['GET'])
def info():
    """Get model information"""
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503
    
    return jsonify({
        "model_name": "Qwopus3.5-122B",
        "framework": "AirLLM",
        "status": "ready"
    }), 200


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate text from a single prompt
    
    Request JSON:
    {
        "prompt": "Your prompt here",
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "use_cache": true
    }
    """
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 503
        
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' field"}), 400
        
        prompt = data['prompt']
        max_new_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        use_cache = data.get('use_cache', True)
        max_length = data.get('max_length', 512)
        
        if not isinstance(prompt, str) or len(prompt) == 0:
            return jsonify({"error": "Prompt must be a non-empty string"}), 400
        
        logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        # Tokenize input
        input_tokens = model.tokenizer(
            [prompt],
            return_tensors="pt",
            return_attention_mask=False,
            truncation=True,
            max_length=max_length,
            padding=False
        )
        
        # Generate
        with torch.no_grad():
            generation_output = model.generate(
                input_tokens['input_ids'].cuda(),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                use_cache=use_cache,
                return_dict_in_generate=True
            )
        
        # Decode response
        response_text = model.tokenizer.decode(
            generation_output.sequences[0],
            skip_special_tokens=True
        )
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "response": response_text,
            "tokens_generated": len(generation_output.sequences[0]) - len(input_tokens['input_ids'][0])
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """
    Single turn chat endpoint (no history)
    
    Request JSON:
    {
        "message": "Your message here",
        "max_new_tokens": 100,
        "temperature": 0.7
    }
    """
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 503
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data['message']
        max_new_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        if not isinstance(message, str) or len(message) == 0:
            return jsonify({"error": "Message must be a non-empty string"}), 400
        
        logger.info(f"Chat message: {message[:50]}...")
        
        # Tokenize
        input_tokens = model.tokenizer(
            [message],
            return_tensors="pt",
            return_attention_mask=False,
            truncation=True,
            max_length=512,
            padding=False
        )
        
        # Generate
        with torch.no_grad():
            generation_output = model.generate(
                input_tokens['input_ids'].cuda(),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                use_cache=True,
                return_dict_in_generate=True
            )
        
        # Decode
        response = model.tokenizer.decode(
            generation_output.sequences[0],
            skip_special_tokens=True
        )
        
        return jsonify({
            "success": True,
            "user_message": message,
            "assistant_response": response
        }), 200
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat/session', methods=['POST'])
def chat_session():
    """
    Multi-turn chat with session history
    
    Request JSON:
    {
        "session_id": "unique_session_id",
        "message": "Your message here",
        "max_new_tokens": 100,
        "temperature": 0.7,
        "reset": false
    }
    """
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 503
        
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'message' not in data:
            return jsonify({"error": "Missing 'session_id' or 'message' field"}), 400
        
        session_id = data['session_id']
        message = data['message']
        max_new_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        reset = data.get('reset', False)
        
        if not isinstance(message, str) or len(message) == 0:
            return jsonify({"error": "Message must be a non-empty string"}), 400
        
        # Reset session if requested
        if reset or session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Build context from history
        context_lines = conversation_history[session_id].copy()
        context_lines.append(f"User: {message}")
        full_context = "\n".join(context_lines)
        
        logger.info(f"Session {session_id}: {message[:50]}...")
        
        # Tokenize
        input_tokens = model.tokenizer(
            [full_context],
            return_tensors="pt",
            return_attention_mask=False,
            truncation=True,
            max_length=2048,
            padding=False
        )
        
        # Generate
        with torch.no_grad():
            generation_output = model.generate(
                input_tokens['input_ids'].cuda(),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                use_cache=True,
                return_dict_in_generate=True
            )
        
        # Decode
        response = model.tokenizer.decode(
            generation_output.sequences[0],
            skip_special_tokens=True
        )
        
        # Store in history
        conversation_history[session_id].append(f"User: {message}")
        conversation_history[session_id].append(f"Assistant: {response}")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "user_message": message,
            "assistant_response": response,
            "history_length": len(conversation_history[session_id])
        }), 200
    
    except Exception as e:
        logger.error(f"Session chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get conversation history for a session"""
    if session_id not in conversation_history:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "session_id": session_id,
        "history": conversation_history[session_id],
        "message_count": len(conversation_history[session_id])
    }), 200


@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Clear conversation history for a session"""
    if session_id in conversation_history:
        del conversation_history[session_id]
        return jsonify({
            "success": True,
            "message": f"Session {session_id} cleared"
        }), 200
    
    return jsonify({"error": "Session not found"}), 404


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AirLLM API Server')
    parser.add_argument('--model', type=str, 
                       default='OpenYourMind/Qwopus3.5-122B-A10B-Kimi-K2.6-destill-healed-abliterated',
                       help='Model name or path')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=1410, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Load model before starting server
    logger.info("Loading model before starting server...")
    load_model(args.model)
    
    logger.info(f"Starting API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
