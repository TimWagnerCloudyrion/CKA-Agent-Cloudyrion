#!/usr/bin/env python3
"""
CKA-Agent API Proxy Server

Exposes an OpenAI-compatible /v1/chat/completions endpoint.
The proxy receives the prompt from the CKA-Agent, passes it to your
custom handler function, and returns the result back to the agent.

Usage:
    1. Edit handle_request() in proxy/handler.py
    2. python proxy/server.py [--port 8080] [--debug]
"""

import argparse
import json
import logging
import time
import uuid

from flask import Flask, jsonify, request as flask_request, Response

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cka-proxy")


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    app = Flask(__name__)

    # Import the user's handler
    from proxy.handler import handle_request

    @app.route("/v1/chat/completions", methods=["POST"])
    def chat_completions():
        """OpenAI-compatible chat completions endpoint."""
        incoming = flask_request.get_json(force=True)

        messages = incoming.get("messages", [])
        model = incoming.get("model", "proxy-model")

        # Extract the last user message as the prompt string
        prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                prompt = msg.get("content", "")
                break

        logger.info(
            f"Incoming request: model={model}, "
            f"prompt_length={len(prompt)}"
        )

        # Call the user's handler: str -> str
        try:
            response_text = handle_request(prompt)
        except Exception as e:
            logger.error(f"Handler error: {e}", exc_info=True)
            return jsonify({
                "error": {"message": str(e), "type": "handler_error"}
            }), 500

        if not isinstance(response_text, str):
            response_text = str(response_text)

        logger.info(f"Handler returned {len(response_text)} chars")

        # Wrap in OpenAI-compatible response format
        openai_response = {
            "id": f"chatcmpl-proxy-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

        return jsonify(openai_response)

    @app.route("/v1/models", methods=["GET"])
    def list_models():
        """Minimal /v1/models endpoint for compatibility."""
        return jsonify({
            "object": "list",
            "data": [
                {
                    "id": "proxy-model",
                    "object": "model",
                    "owned_by": "proxy",
                }
            ],
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    return app


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="CKA-Agent API Proxy Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting proxy on {args.host}:{args.port}")

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()